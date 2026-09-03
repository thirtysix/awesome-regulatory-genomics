#!/usr/bin/env python3
"""Stage 2f - find a url for a tool that has none, or whose url is wrong.

Everything here is an API a cron job can call. No search engine, no browsing,
no agent: the sources are the tool's own full text, the package registries, the
GitHub search API and the Wayback Machine, in that order of trust.

    full text   the availability section of the paper, already cached under
                data/cache/fulltext. What the authors wrote beats what we infer
    registry    PyPI, Bioconda, Bioconductor, CRAN. A named package is strong
                evidence and comes with a canonical home
    github      the search API, then the SAME validation layer 1 uses. Never
                accepted on a name match: names in this field are short and
                generic, and `bisearch` is a binary-search package
    wayback     only when the stated url is dead. This does not resurrect a
                tool; it records that the tool existed and where it lived,
                which is the honest thing to publish about software that was
                served once and is not served now

Two hard-won rules are baked in. The Wayback availability API is queried
**serially with backoff**, because firing six in parallel returns 429 and the
429 body parses as "no snapshot" - reading that as absence retires tools that
are merely offline. And a recovered url is handed to verify_urls before it is
believed, because a resolving domain is not the same as the right domain.
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
import time
from pathlib import Path

import gzip

import requests
from urllib.parse import urlparse

from config import user_agent
from jsonio import read_json, write_json
from discover_literature import software_urls
from resolve_repos import (clean_slug, from_bioconda, from_bioconductor,
                           from_cran, from_github_search, from_pypi,
                           github_meta, validate)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw" / "recovered_urls.json"
WAYBACK = "https://archive.org/wayback/available"


def wayback(http: requests.Session, url: str, tries: int = 4) -> tuple[str, str]:
    """Closest snapshot, or ("", ""). Serial and backed off, on purpose.

    A parallel burst against this endpoint returns 429 whose body deserialises
    to an empty snapshot set. That is indistinguishable from "never archived"
    unless you look at the status code, and treating it as absence declares
    live-but-offline tools dead.
    """
    for attempt in range(tries):
        try:
            r = http.get(WAYBACK, params={"url": url}, timeout=40)
            if r.status_code == 429:
                time.sleep(8 * (attempt + 1))
                continue
            if r.status_code != 200:
                return "", f"wayback http {r.status_code}"
            snap = (r.json().get("archived_snapshots") or {}).get("closest") or {}
            if snap.get("url"):
                return snap["url"], f"archived {str(snap.get('timestamp', ''))[:8]}"
            return "", "no snapshot"
        except requests.RequestException as e:
            time.sleep(4 * (attempt + 1))
    return "", "wayback rate-limited throughout"


EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
FULLTEXT_DIR = ROOT / "data" / "cache" / "fulltext"


def article_fulltext(http: requests.Session, tool: dict) -> str:
    """The tool's paper, from the gzipped store or Europe PMC.

    Shares the store promote_literature fills, so a document fetched for the
    literature pipeline is never fetched again here.
    """
    pmcid = tool.get("pmcid") or ""
    if not pmcid:
        query = (f"EXT_ID:{tool['pmid']}" if tool.get("pmid")
                 else f"DOI:{tool['doi']}" if tool.get("doi") else "")
        if not query:
            return ""
        try:
            r = http.get(f"{EPMC}/search", timeout=30,
                         params={"query": query, "resultType": "core", "format": "json"})
            res = (r.json().get("resultList") or {}).get("result") or []
        except (requests.RequestException, ValueError):
            return ""
        if not res or res[0].get("isOpenAccess") != "Y":
            return ""
        pmcid = res[0].get("pmcid") or ""
    if not pmcid:
        return ""
    path = FULLTEXT_DIR / f"{pmcid}.xml.gz"
    if path.exists():
        try:
            with gzip.open(path, "rt", encoding="utf-8", errors="replace") as fh:
                return fh.read()
        except OSError:
            return ""
    try:
        r = http.get(f"{EPMC}/{pmcid}/fullTextXML", timeout=60)
    except requests.RequestException:
        return ""
    if r.status_code != 200 or not r.text.strip():
        return ""
    try:
        FULLTEXT_DIR.mkdir(parents=True, exist_ok=True)
        with gzip.open(path, "wt", encoding="utf-8") as fh:
            fh.write(r.text)
    except OSError:
        pass
    return r.text


def from_kept_path(http: requests.Session, tool: dict) -> tuple[str, str]:
    """A redirect that moved the site but threw the path away.

    Institutional archives do this: lcbb.epfl.ch/software.html redirects, twice,
    to archiveweb.epfl.ch/lcbb.epfl.ch/ - the whole lab, minus the page you
    asked for. The content is there under the same path on the new host, and
    the redirect gives no hint of it. Re-asking with the path appended costs one
    request and returns the page the old url meant.
    """
    url = tool.get("url") or ""
    path = urlparse(url).path.strip("/")
    if not url or not path or path.lower() in ("index.html", "index.htm"):
        return "", ""
    try:
        r = http.get(url, timeout=25, allow_redirects=True)
    except requests.RequestException:
        return "", ""
    final = str(r.url)
    fp = urlparse(final)
    # Only interesting when we were redirected somewhere that dropped the path.
    if urlparse(url).netloc.lower() == fp.netloc.lower():
        return "", ""
    if path.lower() in final.lower():
        return "", ""
    # Append only to a bare root. When the redirect already lands on a path we
    # would be stitching two together: FirstEF redirects to ESEfinder's cgi and
    # this produced .../ESE3/esefinder.cgi/tools/FirstEF, a url that exists
    # nowhere. An archive redirect that keeps the site as a subdirectory -
    # archiveweb.epfl.ch/lcbb.epfl.ch/ - is the case worth serving.
    tail = fp.path.strip("/")
    if tail and not (fp.netloc.lower().startswith(("archive", "web.archive"))
                     or tail.count("/") == 0 and "." in tail):
        return "", ""
    cand = final.rstrip("/") + "/" + path
    try:
        rr = http.get(cand, timeout=25, allow_redirects=True)
    except requests.RequestException:
        return "", ""
    if rr.status_code == 200 and len(rr.text) > 800:
        return cand, "the redirect dropped the path; re-appended"
    return "", ""


def from_relocation(http: requests.Session, tool: dict) -> tuple[str, str]:
    """The successor address the broken page itself names, if it names one.

    Costs nothing: verify_urls already fetched and stored this page. A lab that
    migrates often leaves a notice rather than a redirect, and no status code
    or 3xx reveals it - PlantTFDB's PKU address answers 200 and serves a Gao
    Lab page listing a new address for each of a dozen tools.
    """
    from verify_urls import load_page, relocation_url, visible_text
    url = tool.get("url") or ""
    if not url:
        return "", ""
    html = load_page(url)
    if not html:
        try:
            r = http.get(url, timeout=25, allow_redirects=True)
            html = r.text if r.status_code < 400 else ""
        except requests.RequestException:
            return "", ""
    moved = relocation_url(tool.get("name", ""), visible_text(html, 12000), url)
    return (moved, "the old page names its successor") if moved else ("", "")


def from_article(http: requests.Session, tool: dict) -> tuple[str, str]:
    """Where the paper says the software lives. Tried before anything else.

    What the authors wrote beats what we infer, and it is not close: on the
    literature side this recovered 90 urls where inference recovered 8. The
    same availability-section rule applies - a url under an "Availability"
    heading is the authors stating an address, and it outranks a name match.

    It was never pointed at the catalog before, only at new candidates, so a
    catalog entry whose link rotted was never checked against its own paper.
    """
    text = article_fulltext(http, tool)
    if not text:
        return "", ""
    have = str(tool.get("url") or "").rstrip("/").lower()
    code, other = software_urls(text, tool.get("name", ""))
    for url, why in [(code[0] if code else "", "article, code host"),
                     (other[0] if other else "", "article, stated url")]:
        # Offering back the url we already know is broken is not a recovery.
        # Half of what this stage finds is exactly that, because the paper
        # records where the tool was on the day it was published.
        if url and url.rstrip("/").lower() != have:
            return url, why
    return "", ""


# Hosts that reorganised and kept the same last path segment. A rewrite is
# tried before anything else, because it is one request and it returns the
# tool's own current page rather than an archive of its old one.
#
# The Sanger Institute has used three shapes: /resources/software/<x>/, then
# /science/tools/<x>, now /tool/<x>/. Eponine's catalog url still answers 200
# and serves a generic "Tools" index, which is the worst kind of broken - it
# looks alive to any status-code check.
HOST_REWRITES = [
    (re.compile(r"^https?://(?:www\.)?sanger\.ac\.uk/(?:resources/software|science/tools|tool)/([^/?#]+)",
                re.I), "https://www.sanger.ac.uk/tool/{0}/"),
]


def from_rewrite(http: requests.Session, url: str) -> tuple[str, str]:
    """A known host reorganisation, tried and checked before anything else."""
    for pat, tmpl in HOST_REWRITES:
        m = pat.match(url or "")
        if not m:
            continue
        cand = tmpl.format(*m.groups())
        if cand.rstrip("/") == (url or "").rstrip("/"):
            continue
        try:
            r = http.get(cand, timeout=25, allow_redirects=True)
        except requests.RequestException:
            continue
        if r.status_code == 200:
            return cand, "host rewrite"
    return "", ""


# Path segments that are site furniture rather than a person or a group.
NOT_A_LAB = {
    "www", "web", "software", "tools", "tool", "research", "index", "home",
    "public", "html", "htm", "projects", "project", "downloads", "download",
    "resources", "science", "labs", "lab", "people", "group", "groups", "en",
    "bio", "bioinfo", "bioinformatics", "cgi", "bin", "pub", "data", "site",
}


def lab_tokens(url: str) -> list[str]:
    """Person or group names hiding in a url, most specific first.

    Academic urls name the lab in the path far more often than the tool does:
    labs.csb.utoronto.ca/moses/monkey.html says "moses", and MONKEY turned out
    to live at github.com/moses-lab/MONKEY. A tilde is the older convention -
    stats.gla.ac.uk/~mgupta - and the subdomain sometimes carries it too.
    """
    parsed = urlparse(url or "")
    out = []
    for seg in parsed.path.split("/"):
        seg = re.sub(r"\.(html?|php|jsp|aspx|cgi|rhtml)$", "", seg.strip("~ ").strip())
        if seg and seg.lower() not in NOT_A_LAB and re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{2,24}", seg):
            out.append(seg)
    host = parsed.netloc.split(":")[0].split(".")
    if host and host[0].lower() not in NOT_A_LAB and re.fullmatch(r"[a-z][a-z0-9-]{2,24}", host[0].lower()):
        out.append(host[0])
    seen, uniq = set(), []
    for t in out:
        if t.lower() not in seen:
            seen.add(t.lower()); uniq.append(t)
    return uniq


# Two tokens and three owner spellings, not four and four. The combinatorics
# are the whole risk here: sixteen probes per tool is 830 requests across a
# review set this size, spent almost entirely on 404s. Six is enough to catch
# the shape that works - <lab>-lab/<Tool> - and the budget below caps the rest.
# Three owner tokens, three spellings: nine probes per tool at the very most,
# and the run-wide budget caps the total. Ordering matters more than breadth -
# the shape that works is <firstauthor>-lab/<Tool>, and MONKEY resolves on the
# first probe of the first token. Each is one core-API call (5,000/hour), never
# the search API (30/minute).
OWNER_FORMS = ("{0}-lab", "{0}lab", "{0}")
MAX_TOKENS = 4
# 52 candidates at nine probes each needs 468, and a budget of 300 silently
# stopped before reaching TADMaster, whose Oluwadarelab/TADMaster answers 200.
# A cap that truncates the run is worse than no cap: it looks like the rule
# failing rather than the budget ending.
LAB_BUDGET = 500


# Surnames too common to be a useful GitHub owner guess.
COMMON_SURNAME = {"li", "wang", "zhang", "liu", "chen", "yang", "huang", "zhao",
                  "wu", "zhou", "xu", "sun", "ma", "zhu", "hu", "guo", "he",
                  "lin", "luo", "kim", "lee", "park", "smith", "jones", "brown"}


# German and Nordic names have two romanisations and GitHub accounts use both.
# Soding vs Soeding decides whether soedinglab/xxmotif is ever found: the NFKD
# fold gives the first, the convention the account was named under gives the
# second.
UMLAUT = {"\u00e4": "ae", "\u00f6": "oe", "\u00fc": "ue", "\u00df": "ss",
          "\u00c4": "Ae", "\u00d6": "Oe", "\u00dc": "Ue",
          "\u00e5": "aa", "\u00f8": "oe", "\u00e6": "ae"}


def transliterations(name: str) -> list[str]:
    """Both romanisations of a surname, most likely first."""
    plain = re.sub(r"[^A-Za-z-]", "", unicodedata.normalize("NFKD", name))
    expanded = re.sub(r"[^A-Za-z-]", "",
                      unicodedata.normalize("NFKD", "".join(UMLAUT.get(c, c) for c in name)))
    return [plain] if expanded == plain else [plain, expanded]


def author_tokens(tool: dict) -> list[str]:
    """First and last authors' surnames, from the OpenAlex cache. Offline.

    Better than mining the url, because a url encodes the lab only when the
    lab happened to name a directory after itself, whereas nearly every entry
    has a paper. 99% of the ~4,800 cached works carry authorships, and the
    lab's GitHub account is named for the first or the last author far more
    often than for anything in the old homepage's path.
    """
    from enrich import ident_key, read_openalex_work
    out = []
    # ident_key wants the prefixed form. Passing a bare pmid yields the key
    # "15575972_", which matches no file and fails silently as "no authors".
    idents = [f"doi:{tool['doi']}" if tool.get("doi") else "",
              f"pmid:{tool['pmid']}" if tool.get("pmid") else ""]
    for ident in [i for i in idents if i]:
        work = read_openalex_work(ident_key(ident))
        auths = (work or {}).get("authorships") or []
        for a in ([auths[0], auths[-1]] if auths else []):
            name = ((a.get("author") or {}).get("display_name") or "").strip()
            if not name:
                continue
            # Fold accents rather than deleting them: stripping non-ASCII
            # turns Piqué-Regi into "Piqu-Regi" and Söding into "Sding",
            # neither of which is anyone's GitHub account.
            raw = name.split()[-1]
            for variant in transliterations(raw):
                if len(variant) > 2 and variant.lower() not in COMMON_SURNAME:
                    out.append(variant)
        if out:
            break
    seen, uniq = set(), []
    for t in out:
        if t.lower() not in seen:
            seen.add(t.lower()); uniq.append(t)
    return uniq


def from_lab_guess(http: requests.Session, tool: dict, token: str | None,
                   budget: list[int]) -> tuple[str, str]:
    """Guess the lab's GitHub account from the url, then look for the tool there.

    One GET per candidate owner/repo pair against the core API, which allows
    5,000/hour - not the search API, which allows 30/minute and would be the
    wrong endpoint to spend on a guess. The answer still goes through the same
    validation layer 1 uses, so a coincidental name match is rejected.
    """
    name = tool.get("name") or ""
    if len(re.sub(r"[^A-Za-z0-9]", "", name)) < 3:
        return "", ""
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    # Authors first: nearly every entry has a paper, while a url names the lab
    # only when somebody happened to name a directory after it.
    cands = author_tokens(tool) + lab_tokens(tool.get("url", ""))
    for lab in cands[:MAX_TOKENS]:
        for form in OWNER_FORMS:
            if budget[0] <= 0:
                return "", ""
            owner = form.format(lab)
            slug = f"{owner}/{name}"
            budget[0] -= 1
            try:
                r = http.get(f"https://api.github.com/repos/{slug}", headers=headers, timeout=25)
            except requests.RequestException:
                continue
            if r.status_code == 403 and "rate" in r.text.lower():
                budget[0] = 0
                return "", "github rate limit reached; stopping lab guesses"
            if r.status_code != 200:
                continue
            d = r.json()
            meta = {"description": d.get("description"), "topics": d.get("topics") or [],
                    "stars": d.get("stargazers_count"), "archived": d.get("archived"),
                    "full_name": d.get("full_name"), "readme": ""}
            ok, why = validate(tool, d.get("full_name") or slug, meta, source="lab guess")
            if ok:
                return d.get("html_url") or f"https://github.com/{slug}", f"lab guess ({why[:40]})"
    return "", ""


# The canonical page a package registry keeps for itself. Preferred over the
# repository when the registry has one: it is the address the package is
# distributed from, it survives the repository being renamed or moved, and for
# an R or Bioconductor package it is what the community actually cites.
REGISTRY_PAGE = {
    "pypi": "https://pypi.org/project/{0}/",
    "cran": "https://cran.r-project.org/package={0}",
    "bioconductor": "https://bioconductor.org/packages/{0}/",
}


def from_registries(http: requests.Session, name: str) -> tuple[str, str]:
    """A repository or canonical page from PyPI, Bioconda, Bioconductor or CRAN.

    These resolvers return an owner/name SLUG, never a url. An earlier version
    of this function looked for a string starting with http, found none, and
    silently returned nothing every single time - so the registries, the most
    trustworthy source in the ordering above, contributed to no run at all.
    """
    for fn, label in ((from_pypi, "pypi"), (from_bioconda, "bioconda"),
                      (from_bioconductor, "bioconductor"), (from_cran, "cran")):
        try:
            got = fn(http, name)
        except Exception:
            continue
        if not got:
            continue
        slug = got[0] if isinstance(got, (tuple, list)) else got
        if not isinstance(slug, str) or "/" not in slug:
            continue
        # Prefer the registry's own page only if it can actually be READ. A
        # canonical address outlives a repository being renamed, which is worth
        # something, and nothing at all if the next stage cannot verify it:
        # pypi.org answers 200 and serves a bot challenge, so every pypi
        # candidate came back "unreadable, 226 characters". The repository is
        # the weaker address and the checkable one.
        page = REGISTRY_PAGE.get(label)
        if page:
            cand = page.format(name)
            try:
                r = http.get(cand, timeout=25, allow_redirects=True)
                body = re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)[^>]*>.*?</\1>", " ",
                                                      r.text, flags=re.S | re.I))
                if r.status_code == 200 and len(re.sub(r"\s+", " ", body).strip()) > 600:
                    return cand, f"{label} package page"
            except requests.RequestException:
                pass
        return f"https://github.com/{slug}", f"{label} -> repository"
    return "", ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True,
                    help="json with a list of {name, description, url?}")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--search-budget", type=int, default=40,
                    help="GitHub search calls; the API allows 30/min")
    ap.add_argument("--lab-budget", type=int, default=LAB_BUDGET,
                    help="cap on lab-guess probes for the whole run; each is one "
                         "core-API call and most are 404s")
    ap.add_argument("--no-wayback", action="store_true")
    args = ap.parse_args()

    src = read_json(Path(args.input))
    rows = src["tools"] if isinstance(src, dict) and "tools" in src else (
        src["list"] if isinstance(src, dict) else src)
    if args.limit:
        rows = rows[:args.limit]

    http = requests.Session()
    http.headers.update({"User-Agent": user_agent()})
    from enrich import github_token
    token, meta_cache, budget = github_token(), {}, args.search_budget
    lab_budget = [args.lab_budget]

    out = {}
    for t in rows:
        name, found, how = t["name"], "", ""
        # Ordered by trust: what the paper says, then what a registry
        # distributes, then a known host move, then guesses.
        url, why = from_kept_path(http, t)
        if not url:
            url, why = from_relocation(http, t)
        if not url:
            url, why = from_article(http, t)
        if not url:
            url, why = from_rewrite(http, t.get("url", ""))
        if not url:
            url, why = from_registries(http, name)
        if not url:
            url, why = from_lab_guess(http, t, token, lab_budget)
        if url:
            found, how = url, why
        if not found and budget > 0:
            budget -= 1
            try:
                for slug, _src in from_github_search(http, t, token) or []:
                    m = github_meta(http, slug, token, meta_cache)
                    ok, w = validate(t, slug, m, source="recover")
                    if ok:
                        found, how = f"https://github.com/{slug}", f"github search ({w[:44]})"
                        break
            except Exception as e:
                how = f"github search failed: {type(e).__name__}"
        if not found and t.get("url") and not args.no_wayback:
            snap, w = wayback(http, t["url"])
            time.sleep(6)
            if snap:
                found, how = snap, f"wayback ({w})"
        out[name] = {"url": found, "how": how or "nothing found"}
        print(f"  {'FOUND' if found else '  -  '} {name[:22]:24s} {how[:44]:46s} {found[:52]}")

    write_json(OUT, {"count": len(out), "recovered": sum(1 for v in out.values() if v['url']),
                     "list": [{"name": k, **v} for k, v in out.items()]})
    print(f"\n{sum(1 for v in out.values() if v['url'])}/{len(out)} recovered -> {OUT.relative_to(ROOT)}")
    print("verify before use:  python3 pipeline/verify_urls.py --input " + str(OUT.relative_to(ROOT)))


if __name__ == "__main__":
    main()
