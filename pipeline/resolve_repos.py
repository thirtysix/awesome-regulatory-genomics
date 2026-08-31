#!/usr/bin/env python3
"""Stage 2c - find source repositories that bio.tools does not record.

bio.tools stores whatever links a submitter supplied, which for older entries is
often just an institutional homepage. WebLogo is the clearest case: its record
carries only a Berkeley URL, while the source lives at gecrooks/weblogo and is
published on PyPI.

Four sources are tried, cheapest and most reliable first:

  bioconda    recipes/<name>/meta.yaml, a curated field maintained by packagers
  bioconductor  the package DESCRIPTION's URL / BugReports fields
  pypi        project_urls and home_page for a package of the same name
  homepage    GitHub links on the tool's own page

**Every candidate is validated before it is accepted**, because guessing by name
is actively dangerous here. A bare PyPI lookup returns `katylava/memepy`, a meme
generator, for MEME; `shyal/vulcan`, a terminal flashcard app, for vulcan; and
an unrelated personal project for GREAT. Three false positives in a five-tool
probe. A wrong repository link is the same class of error as a wrong DOI: it
looks fine and quietly misinforms.

Acceptance needs either an exact name match or real textual agreement between
the repository and the tool. Anything weaker is written to docs/repo-review.md
as a proposal rather than applied.

    python pipeline/resolve_repos.py [--limit N] [--refresh]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

import requests

from config import CACHE, DOCS, RAW, user_agent
from jsonio import read_json, redact_emails
from mdutil import cell

ENRICHED = RAW / "enriched.json.gz"
REPOMAP = CACHE / "repo_map.json"
REPORT = DOCS / "repo-review.md"

GH = re.compile(r"github\.com/([A-Za-z0-9._-]+)/([A-Za-z0-9._-]+)")
BAD_OWNER = {"orgs", "topics", "search", "about", "features", "sponsors", "site",
             "apps", "marketplace", "readme", "explore", "login", "join"}
# Generic English and software words only. Domain words are deliberately NOT
# here: "sequence", "motif", "genome" and "binding" are exactly what
# distinguishes a sequence-logo generator from a meme generator. Adding them to
# this list was enough to reject gecrooks/weblogo, the correct answer.
STOP = {"the", "a", "an", "for", "and", "of", "to", "in", "with", "from", "on", "by",
        "is", "are", "it", "its", "this", "that", "can", "you", "your", "we", "our",
        "using", "used", "use", "based", "tool", "tools", "software", "package",
        "library", "framework", "application", "program", "implementation",
        "simple", "fast", "easy", "new", "open", "source", "code", "project",
        "python", "java", "version", "web", "online", "server", "designed", "make",
        "provides", "allows", "support", "supports"}


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def tokens(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]{3,}", (s or "").lower()) if w not in STOP}


def clean_slug(url: str) -> str | None:
    m = GH.search(url or "")
    if not m:
        return None
    owner, repo = m.group(1), re.sub(r"\.git$", "", m.group(2))
    if owner.lower() in BAD_OWNER or not repo:
        return None
    return f"{owner}/{repo}"


# ---------------------------------------------------------------------------
# candidate sources
# ---------------------------------------------------------------------------
def from_bioconda(http, name) -> tuple[str, str] | None:
    for variant in dict.fromkeys([name, name.lower(), norm(name)]):
        try:
            r = http.get("https://raw.githubusercontent.com/bioconda/bioconda-recipes"
                         f"/master/recipes/{variant}/meta.yaml", timeout=20)
        except requests.RequestException:
            continue
        if r.status_code == 200:
            for field in ("dev_url", "home"):
                m = re.search(rf"{field}:\s*\S*?({GH.pattern})", r.text)
                if m:
                    slug = clean_slug(m.group(1))
                    if slug:
                        return slug, "bioconda"
            slug = clean_slug(r.text)
            if slug:
                return slug, "bioconda"
    return None


def from_bioconductor(http, name) -> tuple[str, str] | None:
    try:
        r = http.get(f"https://bioconductor.org/packages/release/bioc/html/{name}.html",
                     timeout=20)
    except requests.RequestException:
        return None
    if r.status_code != 200:
        return None
    slug = clean_slug(r.text)
    return (slug, "bioconductor") if slug else None


def from_pypi(http, name) -> tuple[str, str, str] | None:
    try:
        r = http.get(f"https://pypi.org/pypi/{name}/json", timeout=20)
    except requests.RequestException:
        return None
    if r.status_code != 200:
        return None
    info = r.json().get("info") or {}
    urls = [info.get("home_page") or ""] + list((info.get("project_urls") or {}).values())
    for u in urls:
        slug = clean_slug(u or "")
        if slug:
            return slug, "pypi", (info.get("summary") or "")
    return None


def from_cran(http, name) -> tuple[str, str] | None:
    """CRAN package metadata via crandb, which exposes URL and BugReports."""
    try:
        r = http.get(f"https://crandb.r-pkg.org/{name}", timeout=20)
    except requests.RequestException:
        return None
    if r.status_code != 200:
        return None
    try:
        blob = r.json()
    except ValueError:
        return None
    for field in ("URL", "BugReports"):
        slug = clean_slug(str(blob.get(field) or ""))
        if slug:
            return slug, "cran"
    return None


# GitHub's search endpoint allows 30 requests/minute for an authenticated user,
# far below the 5,000/hour core limit, and sustained abuse gets an account
# flagged. This throttle is deliberately stricter than the documented ceiling
# and is shared across all threads: searches are effectively serialised.
_search_lock = threading.Lock()
_search_last = [0.0]
SEARCH_MIN_INTERVAL = 3.5          # ~17 requests/minute, ~half the allowance


def from_github_search(http, tool, token) -> list[tuple[str, str]]:
    """Last-resort lookup: ask GitHub for repositories named like the tool.

    Used only when every cheaper source has failed, and only for tools whose
    type implies source code exists. The results are candidates, not answers;
    they go through the same validation as everything else, which is what stops
    a search for "Match" or "SEA" returning something plausible and wrong.
    """
    name = tool["name"]
    if len(norm(name)) < 4:
        return []                  # 2-3 character names are hopeless to search
    with _search_lock:
        wait = SEARCH_MIN_INTERVAL - (time.time() - _search_last[0])
        if wait > 0:
            time.sleep(wait)
        _search_last[0] = time.time()

    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        r = http.get("https://api.github.com/search/repositories",
                     params={"q": f"{name} in:name", "sort": "stars",
                             "order": "desc", "per_page": 5},
                     headers=headers, timeout=25)
    except requests.RequestException:
        return []
    if r.status_code == 403 or r.status_code == 429:
        # Secondary rate limit. Stand well back rather than retrying tightly.
        reset = r.headers.get("X-RateLimit-Reset")
        pause = 60.0
        if reset:
            pause = max(pause, float(reset) - time.time() + 5)
        print(f"    GitHub search rate limited; pausing {pause:.0f}s", file=sys.stderr)
        with _search_lock:
            time.sleep(min(pause, 300))
        return []
    if r.status_code != 200:
        return []
    # If the remaining budget is nearly gone, slow down further.
    try:
        if int(r.headers.get("X-RateLimit-Remaining", "99")) <= 2:
            with _search_lock:
                time.sleep(30)
    except ValueError:
        pass
    out = []
    for item in (r.json().get("items") or [])[:5]:
        slug = item.get("full_name")
        if slug and clean_slug(f"github.com/{slug}"):
            out.append((slug, "github-search"))
    return out


def from_homepage(http, url) -> list[tuple[str, str]]:
    """Every distinct GitHub link on the page, not just the first.

    Taking the first match makes the result depend on page layout: a docs site
    with an Angular badge in its header yielded `angular/angular` for PomBase's
    motif search. Collecting all of them lets validation choose, and a page
    rarely carries more than a handful.
    """
    if not url or "github.com" in url:
        return []
    try:
        r = http.get(url, timeout=8, allow_redirects=True)
    except requests.RequestException:
        return []
    if r.status_code != 200 or "html" not in r.headers.get("Content-Type", ""):
        return []
    out, seen = [], set()
    for m in GH.finditer(r.text[:400_000]):
        slug = clean_slug(m.group(0))
        if slug and slug not in seen:
            seen.add(slug)
            out.append((slug, "homepage"))
        if len(out) >= 8:
            break
    return out


# ---------------------------------------------------------------------------
def validate(tool: dict, slug: str, gh_meta: dict | None, extra_text: str = "",
             source: str = "") -> tuple[bool, str]:
    """Decide whether `slug` really is this tool's repository.

    **A matching name is necessary but never sufficient.** An earlier version
    accepted exact name matches outright and was right less than half the time:
    tool names in this field are short and generic, so `Match` resolved to a
    text-matching library, `SEA` to an RPC framework, `CREME` to an online
    machine-learning package and `PINES` to somebody's utility scripts.

    Even a domain-scoped registry does not rescue it. bioconda carries a recipe
    named `medusa` for a genome scaffolder, while this catalog's MEDUSA learns
    motif models of TF binding sites. Two real bioinformatics tools, one name.

    So the repository has to say something recognisably about the same subject:
    at least two content words shared with the tool's description. A repository
    with no description at all cannot be verified and is held for review, not
    accepted on the strength of its name.
    """
    repo_name = slug.split("/")[-1]
    # Substring matching is too loose: "cudameme" is a prefix of
    # "cudamemeticalgorithm" and "streme" of "stremefrontend", which is how
    # CUDA-MEME acquired a particle-swarm GRN repo and STREME a web frontend.
    # A few extra characters are fine ("weblogo" vs "weblogo3"); a different
    # word is not.
    tn, rn = norm(tool["name"]), norm(repo_name)
    name_ok = tn == rn or (tn in rn and len(rn) <= len(tn) + 3)

    repo_text = " ".join(filter(None, [
        (gh_meta or {}).get("description") or "",
        " ".join((gh_meta or {}).get("topics") or []),
        (gh_meta or {}).get("readme") or "",
        extra_text,
    ])).strip()
    if not repo_text:
        return False, "repo has no description; cannot verify beyond the name"

    shared = tokens(tool.get("description") or "") & tokens(repo_text)
    evidence = f"{len(shared)} shared terms ({', '.join(sorted(shared)[:4])})"
    # GitHub search is the least trustworthy source: it returns the most
    # popular repository with a similar name, which for a short bioinformatics
    # name is usually somebody else's project. Demand more agreement from it.
    need = 3 if source == "github-search" else 2
    if name_ok and len(shared) >= need:
        return True, f"name match + {evidence}"
    if len(shared) >= 4:
        return True, evidence
    if name_ok:
        return False, f"name matches but only {evidence}"
    return False, f"no name match and only {evidence}"


def github_meta(http, slug, token, cache) -> dict | None:
    if slug in cache:
        return cache[slug]
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        r = http.get(f"https://api.github.com/repos/{slug}", headers=headers, timeout=25)
    except requests.RequestException:
        return None
    if r.status_code != 200:
        cache[slug] = None
        return None
    d = r.json()
    meta = {"description": d.get("description"), "topics": d.get("topics") or [],
            "stars": d.get("stargazers_count"), "archived": d.get("archived"),
            "full_name": d.get("full_name"), "readme": ""}
    # Many research repos leave the description blank. The opening of the README
    # is usually enough to tell a motif finder from an RPC framework.
    if not meta["description"]:
        try:
            rr = http.get(f"https://api.github.com/repos/{slug}/readme",
                          headers={**headers, "Accept": "application/vnd.github.raw"},
                          timeout=20)
            if rr.status_code == 200:
                # Redact here, not at the write: this cache is committed and
                # this repository is public, so a README's "Contact:
                # someone@university.edu" would republish a third party's
                # address in bulk. jsonio.redact_emails states the policy; the
                # cache is written with a bare json.dumps and never reached it.
                meta["readme"] = redact_emails(rr.text[:1200])
        except requests.RequestException:
            pass
    cache[slug] = meta
    return cache[slug]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--workers", type=int, default=4,
                    help="kept low on purpose; these are other people's APIs")
    ap.add_argument("--no-search", action="store_true",
                    help="skip the GitHub search fallback entirely")
    ap.add_argument("--revalidate", action="store_true",
                    help="re-apply the current validation rules to already-cached "
                         "candidates and exit, without any network calls")
    ap.add_argument("--search-budget", type=int, default=250,
                    help="hard cap on GitHub search calls for this run, so a "
                         "run cannot quietly consume the whole rate limit")
    args = ap.parse_args()

    from enrich import github_token
    token = github_token()

    if args.revalidate:
        # Re-score decisions already on disk under the current rules. Metadata
        # is re-fetched from the GitHub core API (5,000/hour, and the SEARCH
        # endpoint is never touched) because the stored description is
        # truncated and omits the README, so scoring from it alone silently
        # demotes every match that was made on README evidence.
        blob = json.loads(REPOMAP.read_text()) if REPOMAP.exists() else {}
        http = requests.Session()
        http.headers.update({"User-Agent": user_agent()})
        cache: dict = {}
        flipped = 0
        for i, (bid, v) in enumerate(sorted(blob.items()), 1):
            meta = github_meta(http, v["slug"], token, cache) or {}
            ok, why = validate({"name": v["name"], "description": v.get("tool_desc") or ""},
                               v["slug"], meta, "", v.get("source", ""))
            if ok != v["accepted"]:
                flipped += 1
            v["accepted"], v["reason"] = ok, why
            if meta.get("description"):
                v["repo_desc"] = meta["description"][:140]
            if i % 100 == 0:
                print(f"  {i}/{len(blob)}", flush=True)
            time.sleep(0.05)
        REPOMAP.write_text(json.dumps(redact_emails(blob), indent=1, sort_keys=True))
        acc = sum(1 for v in blob.values() if v["accepted"])
        print(f"revalidated {len(blob)}: {acc} accepted, {len(blob)-acc} held "
              f"({flipped} changed)")
        return

    tools = [t for t in read_json(ENRICHED)["list"] if not t.get("_repo_slug")]
    tools = tools[: args.limit] if args.limit else tools
    print(f"{len(tools)} records without a repository")
    print(f"  sources: bioconda, Bioconductor, CRAN, PyPI, homepage"
          + ("" if args.no_search else f", GitHub search (budget {args.search_budget})"))

    found = json.loads(REPOMAP.read_text()) if REPOMAP.exists() and not args.refresh else {}
    gh_cache: dict = {}
    lock = threading.Lock()
    done = [0]
    searches = [0]

    # A repository is only expected for tools that ship code. Searching for a
    # web server or a database portal spends rate limit to find, at best, a
    # third party's reimplementation.
    CODEISH = {"Command-line tool", "Library", "Script", "Workflow", "Plug-in",
               "Suite", "Desktop application"}

    def may_search(tool) -> bool:
        if args.no_search:
            return False
        types = set(tool.get("toolType") or [])
        if types and not (types & CODEISH):
            return False
        with lock:
            if searches[0] >= args.search_budget:
                return False
            searches[0] += 1
        return True

    def resolve(tool):
        bid = tool["biotoolsID"]
        with lock:
            if bid in found:
                return None
        http = requests.Session()
        http.headers.update({"User-Agent": user_agent()})
        name = tool["name"]
        # Try several spellings: bio.tools display names carry spaces, hyphens
        # and capitalisation that package registries do not.
        variants = list(dict.fromkeys([name, name.lower(), name.replace(" ", ""),
                                       name.replace(" ", "-").lower(), norm(name)]))
        def gather(sources):
            out = []
            for fn in sources:
                try:
                    got = fn()
                except Exception:                            # noqa: BLE001
                    got = None
                if got:
                    out.extend(got if isinstance(got, list) else [got])
            return out

        def judge(cands, best):
            """Validate candidates; return (accepted_entry_or_None, best_seen)."""
            for cand in cands:
                slug, source = cand[0], cand[1]
                extra = cand[2] if len(cand) > 2 else ""
                meta = github_meta(http, slug, token, gh_cache)
                if meta is None:
                    continue
                ok, why = validate(tool, slug, meta, extra, source)
                entry = {"slug": slug, "source": source, "reason": why,
                         "accepted": ok, "stars": meta.get("stars"),
                         "repo_desc": (meta.get("description") or "")[:140],
                         "tool_desc": (tool.get("description") or "")[:140],
                         "name": name}
                if ok:
                    return entry, entry
                best = best or entry
            return None, best

        # Cheap, curated sources first. GitHub search is only reached if none of
        # them produced a candidate that validates, which keeps the search quota
        # for the records that actually need it.
        accepted, best = judge(gather(
            [lambda v=v: from_bioconda(http, v) for v in variants[:3]]
            + [lambda v=v: from_bioconductor(http, v) for v in variants[:2]]
            + [lambda v=v: from_cran(http, v) for v in variants[:2]]
            + [lambda v=v: from_pypi(http, v) for v in variants[:3]]
            + [lambda: from_homepage(http, tool.get("homepage"))]), None)

        if not accepted and may_search(tool):
            accepted, best = judge(from_github_search(http, tool, token), best)

        # Cache misses too. Without this, every record that yields no candidate
        # is retried on every run, which for the monthly refresh means fetching
        # roughly 800 third-party homepages again each time to learn nothing
        # new. `--refresh` reconsiders them.
        result = accepted or best or {
            "slug": "", "source": "", "reason": "no candidate from any source",
            "accepted": False, "stars": None, "repo_desc": "",
            "tool_desc": (tool.get("description") or "")[:140], "name": name}
        time.sleep(0.3)          # be gentle with the registries
        with lock:
            done[0] += 1
            if result:
                found[bid] = result
            if done[0] % 100 == 0:
                print(f"  {done[0]}/{len(tools)}  accepted "
                      f"{sum(1 for v in found.values() if v['accepted'])}  "
                      f"searches used {searches[0]}/{args.search_budget}", flush=True)
                REPOMAP.parent.mkdir(parents=True, exist_ok=True)
                REPOMAP.write_text(json.dumps(redact_emails(found), indent=1, sort_keys=True))
        return result

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for fut in as_completed([pool.submit(resolve, t) for t in tools]):
            try:
                fut.result()
            except Exception as exc:                         # noqa: BLE001
                print(f"    ! {exc}", file=sys.stderr)

    REPOMAP.parent.mkdir(parents=True, exist_ok=True)
    REPOMAP.write_text(json.dumps(redact_emails(found), indent=1, sort_keys=True))

    accepted = {k: v for k, v in found.items() if v["accepted"]}
    rejected = {k: v for k, v in found.items() if not v["accepted"]}
    candidates = {k: v for k, v in rejected.items() if v.get("slug")}
    print(f"\naccepted {len(accepted)}, held for review {len(candidates)}, "
          f"no candidate {len(rejected) - len(candidates)}")

    out = ["# Repository resolution review", "",
           f"Generated {date.today().isoformat()} by `make repos`.", "",
           "bio.tools records whatever links a submitter supplied, which for older "
           "entries is often only an institutional homepage. This stage looks for the "
           "source repository in bioconda recipes, Bioconductor DESCRIPTION fields, "
           "PyPI metadata and the tool's own homepage.", "",
           "**Every candidate is validated.** Guessing by name alone is dangerous: a "
           "bare PyPI lookup returns `katylava/memepy` for MEME and `shyal/vulcan`, a "
           "flashcard app, for vulcan. A wrong repository link is the same class of "
           "error as a wrong DOI, so a candidate is accepted only on an exact name "
           "match or real vocabulary overlap between repository and tool.", "",
           f"- **{len(accepted)} accepted** and applied to the catalog.",
           f"- **{len(candidates)} held for review** below; none of these are applied.",
           f"- **{len(rejected) - len(candidates)} records yielded no candidate at all** "
           "from any source. These are cached as such so the monthly refresh does "
           "not re-fetch the same third-party homepages to learn nothing new; "
           "`--refresh` reconsiders them.", ""]
    if candidates:
        out += ["## Held for review", "",
                "| Tool | Candidate | Source | Why it was not accepted | Repo description |",
                "| --- | --- | --- | --- | --- |"]
        for v in sorted((r for r in rejected.values() if r.get("slug")),
                        key=lambda x: x["name"].lower()):
            out.append(f"| {cell(v['name'])} | [{cell(v['slug'])}](https://github.com/{v['slug']}) "
                       f"| {cell(v['source'])} | {cell(v['reason'], 60)} | {cell(v['repo_desc'], 80)} |")
        out.append("")

    DOCS.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(out))
    print(f"-> {REPOMAP.name}, {REPORT}")


if __name__ == "__main__":
    main()
