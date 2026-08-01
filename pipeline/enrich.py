#!/usr/bin/env python3
"""Stage 2 - enrich harvested records with repository, registry and citation data.

bio.tools rarely states a source repository explicitly, so repo URLs are mined
from every URL a record carries (homepage, link, download, documentation) and,
for Bioconductor/CRAN/PyPI landing pages, resolved through those registries.
GitHub repositories are then queried for the signals that tell a user whether a
tool is alive: stars, last push, archived flag, license, language.

Citation counts come from OpenAlex, reusing the cache under data/cache/.

    python pipeline/enrich.py [--no-github] [--no-citations] [--limit N]
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import os
import re
import subprocess
import sys
import time
from urllib.parse import urlparse

import requests
import yaml

from jsonio import read_json, write_json
from config import (CACHE, CODE_HOSTS, CURATION, DATA, GITHUB_API, OPENALEX_API, RAW,
                    REGISTRY_HOSTS, openalex_params, openalex_tier, user_agent)

SELECTED = RAW / "selected.json.gz"
ENRICHED = RAW / "enriched.json.gz"
GH_CACHE = CACHE / "github.json"
CITE_CACHE = CACHE / "citation_cache.csv"
OA_DIR = CACHE / "openalex"

GH_REPO_RE = re.compile(r"github\.com/([A-Za-z0-9._-]+)/([A-Za-z0-9._-]+)", re.I)
BIOC_RE = re.compile(r"bioconductor\.org/packages/(?:release/|devel/)?(?:bioc/)?html/([A-Za-z0-9._-]+)\.html", re.I)
CRAN_RE = re.compile(r"cran\.r-project\.org/(?:web/)?packages?/([A-Za-z0-9._-]+)", re.I)
PYPI_RE = re.compile(r"pypi\.(?:org|python\.org)/(?:project|pypi)/([A-Za-z0-9._-]+)", re.I)


# ---------------------------------------------------------------------------
# URL harvesting
# ---------------------------------------------------------------------------
def record_urls(tool: dict) -> list[str]:
    urls = []
    if tool.get("homepage"):
        urls.append(tool["homepage"])
    for field in ("link", "download", "documentation"):
        for entry in tool.get(field) or []:
            if entry.get("url"):
                urls.append(entry["url"])
    seen, out = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def classify_urls(urls: list[str]) -> dict:
    """Split a record's URLs into code hosts, package registries and the rest."""
    code, registries = [], {}
    for u in urls:
        host = (urlparse(u).netloc or "").lower().removeprefix("www.")
        if host in CODE_HOSTS:
            code.append((CODE_HOSTS[host], u))
        elif host in REGISTRY_HOSTS:
            registries.setdefault(REGISTRY_HOSTS[host], u)
    return {"code": code, "registries": registries}


def normalise_github(url: str) -> str | None:
    m = GH_REPO_RE.search(url)
    if not m:
        return None
    owner, repo = m.group(1), m.group(2)
    repo = re.sub(r"\.git$", "", repo)
    if owner.lower() in {"orgs", "topics", "search", "about", "features", "sponsors"}:
        return None
    return f"{owner}/{repo}"


# ---------------------------------------------------------------------------
# Registry resolution (Bioconductor / CRAN / PyPI -> upstream repo)
# ---------------------------------------------------------------------------
def resolve_registry_repo(session: requests.Session, kind: str, url: str) -> str | None:
    """Ask a package registry for the source repository of a package."""
    try:
        if kind == "pypi":
            m = PYPI_RE.search(url)
            if not m:
                return None
            r = session.get(f"https://pypi.org/pypi/{m.group(1)}/json", timeout=25)
            if r.status_code != 200:
                return None
            info = r.json().get("info", {})
            candidates = [info.get("home_page") or ""]
            candidates += list((info.get("project_urls") or {}).values())
            for c in candidates:
                slug = normalise_github(c or "")
                if slug:
                    return slug
        elif kind == "bioconductor":
            m = BIOC_RE.search(url)
            if not m:
                return None
            pkg = m.group(1)
            r = session.get(f"https://bioconductor.org/packages/release/bioc/html/{pkg}.html", timeout=25)
            if r.status_code != 200:
                return None
            for c in GH_REPO_RE.finditer(r.text):
                slug = normalise_github(c.group(0))
                if slug:
                    return slug
        elif kind == "cran":
            m = CRAN_RE.search(url)
            if not m:
                return None
            r = session.get(f"https://crandb.r-pkg.org/{m.group(1)}", timeout=25)
            if r.status_code != 200:
                return None
            blob = json.dumps(r.json())
            for c in GH_REPO_RE.finditer(blob):
                slug = normalise_github(c.group(0))
                if slug:
                    return slug
    except (requests.RequestException, ValueError):
        return None
    return None


# ---------------------------------------------------------------------------
# GitHub
# ---------------------------------------------------------------------------
def github_token() -> str | None:
    for var in ("GITHUB_TOKEN", "GH_TOKEN"):
        if os.environ.get(var):
            return os.environ[var]
    try:
        out = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=15)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def fetch_github(session: requests.Session, slug: str) -> dict | None:
    try:
        r = session.get(f"{GITHUB_API}/repos/{slug}", timeout=30)
    except requests.RequestException:
        return None
    if r.status_code == 404:
        return {"status": "not_found"}
    if r.status_code == 403 and "rate limit" in r.text.lower():
        reset = int(r.headers.get("X-RateLimit-Reset", 0))
        wait = max(0, reset - int(time.time())) + 5
        print(f"    rate limited; sleeping {wait}s", file=sys.stderr)
        time.sleep(min(wait, 900))
        return fetch_github(session, slug)
    if r.status_code != 200:
        return {"status": f"http_{r.status_code}"}
    d = r.json()
    return {
        "status": "ok",
        "slug": d.get("full_name"),
        "stars": d.get("stargazers_count"),
        "forks": d.get("forks_count"),
        "open_issues": d.get("open_issues_count"),
        "archived": d.get("archived"),
        "language": d.get("language"),
        "license": ((d.get("license") or {}) or {}).get("spdx_id"),
        "created_at": (d.get("created_at") or "")[:10],
        "pushed_at": (d.get("pushed_at") or "")[:10],
        "topics": d.get("topics") or [],
        "description": d.get("description"),
    }


# ---------------------------------------------------------------------------
# Citations (OpenAlex)
# ---------------------------------------------------------------------------
def oa_paths(key: str) -> tuple:
    """Both spellings of a stored work: legacy plain .json and current .json.gz."""
    return OA_DIR / f"{key}.json.gz", OA_DIR / f"{key}.json"


def read_openalex_work(key: str) -> dict:
    """The stored OpenAlex work for one identifier key, or {} if absent.

    Reads either spelling, so the 823 plain-JSON files from the original harvest
    keep working alongside anything written since.
    """
    gz, plain = oa_paths(key)
    for path, opener in ((gz, gzip.open), (plain, open)):
        if not path.exists():
            continue
        try:
            with opener(path, "rt", encoding="utf-8") as fh:
                results = json.load(fh).get("results") or []
        except (ValueError, OSError):
            return {}
        return results[0] if results else {}
    return {}


def save_openalex_work(key: str, payload: dict) -> None:
    """Persist the FULL response for one identifier, gzipped.

    The whole object is kept rather than the four fields the citation column
    happens to need. Re-deriving anything else later - abstract, venue, open
    access, concepts - is otherwise a second pass over ~3,700 identifiers
    against a metered daily budget, for data that was already in the response
    we threw away. Gzip costs nothing and buys 6.6x: ~20 MB rather than ~130 MB
    for a full sweep. The directory is gitignored; citation_cache.csv stays the
    small tracked product.
    """
    OA_DIR.mkdir(parents=True, exist_ok=True)
    gz, plain = oa_paths(key)
    tmp = gz.with_suffix(".gz.tmp")
    try:
        with gzip.open(tmp, "wt", encoding="utf-8") as fh:
            json.dump(payload, fh)
        tmp.replace(gz)
        # Drop a legacy uncompressed copy so the two cannot drift apart.
        if plain.exists():
            plain.unlink()
    except OSError:
        tmp.unlink(missing_ok=True)


def abstract_text(work: dict) -> str:
    """Rebuild an abstract from OpenAlex's inverted index, or "" if absent.

    OpenAlex ships abstracts as {word: [positions]} rather than as prose, so it
    has to be reassembled. Coverage measured on a 60-paper sample of this
    catalog: 97% of resolvable works.
    """
    inv = work.get("abstract_inverted_index")
    if not isinstance(inv, dict):
        return ""
    words = sorted((pos, word) for word, poss in inv.items()
                   for pos in poss if isinstance(pos, int))
    return " ".join(word for _, word in words)


def load_citation_cache() -> dict[str, int]:
    cache: dict[str, int] = {}
    if CITE_CACHE.exists():
        with CITE_CACHE.open() as fh:
            for row in csv.reader(fh):
                if len(row) >= 2 and row[0] not in ("identifier", "pmid"):
                    try:
                        cache[row[0]] = int(row[1])
                    except ValueError:
                        continue
    # Seed from any per-work OpenAlex response already on disk.
    if OA_DIR.exists():
        for path in list(OA_DIR.glob("*.json")) + list(OA_DIR.glob("*.json.gz")):
            key = path.name.removesuffix(".gz").removesuffix(".json").rstrip(".")
            if key in cache:
                continue
            work = read_openalex_work(key)
            if work:
                cache[key] = work.get("cited_by_count", 0)
    return cache


def save_citation_cache(cache: dict[str, int]) -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    with CITE_CACHE.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["identifier", "citations"])
        for k, v in sorted(cache.items()):
            w.writerow([k, v])


def pub_identifiers(tool: dict) -> list[str]:
    ids = []
    for pub in tool.get("publication") or []:
        pmid = pub.get("pmid")
        doi = pub.get("doi")
        meta = pub.get("metadata") or {}
        if not pmid and meta:
            pmid = meta.get("pmid")
        if pmid and str(pmid).lower() not in ("none", "null", ""):
            ids.append(f"pmid:{pmid}")
        elif doi:
            ids.append(f"doi:{doi.strip().removeprefix('https://doi.org/')}")
    return ids


def openalex_lookup(session: requests.Session, ident: str,
                    cache: dict[str, int]) -> tuple[int | None, dict]:
    """Citation count for one identifier, or None if it could not be resolved.

    A failed lookup must NOT be cached as 0. Doing so made a network error or an
    unindexed DOI indistinguishable from a genuinely uncited paper, and left 410
    such zeros in the cache hiding real counts - JASPAR 2018 sat at 0 against a
    true 1,615. Worse, the zeros suppressed the ranking signal that would have
    exposed three out-of-scope records sitting in the top 15. Leaving the key
    absent costs one retry next run and keeps "unknown" distinct from "uncited".
    """
    kind, _, value = ident.partition(":")
    key = f"{kind}_{value}".replace("/", "_").replace(":", "_")
    if key in cache:
        return cache[key], {}
    filt = f"ids.pmid:{value}" if kind == "pmid" else f"doi:{value}"
    try:
        r = session.get(OPENALEX_API, params=openalex_params({"filter": filt}), timeout=30)
        # A 429 here is a spent daily budget, not a slow moment: OpenAlex meters
        # credits and resets at midnight UTC, so Retry-After is measured in hours
        # (21,746 seconds when this was hit). Retrying is futile and continuing
        # is worse, because every remaining identifier would come back empty and
        # the run would look like a catalog with no citations. Stop and say so.
        if r.status_code == 429:
            wait = r.headers.get("Retry-After", "?")
            hrs = f"{int(wait)/3600:.1f}h" if str(wait).isdigit() else wait
            raise SystemExit(
                f"\nOpenAlex returned 429: the daily budget is spent.\n"
                f"  retry after {wait}s ({hrs}); the allowance resets at midnight UTC\n"
                f"  this run was {openalex_tier()}\n"
                f"  nothing already cached is lost - rerun after the reset to continue.")
        results = r.json().get("results") or [] if r.status_code == 200 else []
    except (requests.RequestException, ValueError):
        results = []
    if not results:
        return None, {}
    w = results[0]
    # Keep the whole response, not just the fields this stage reads. It cost a
    # request either way, and the daily budget makes a second pass expensive.
    save_openalex_work(key, r.json())
    cache[key] = w.get("cited_by_count") or 0
    return cache[key], {"title": w.get("title"), "year": w.get("publication_year"),
                        "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name")}


def ident_key(ident: str) -> str:
    kind, _, value = ident.partition(":")
    return f"{kind}_{value}".replace("/", "_").replace(":", "_")


def backfill_works(session: requests.Session, idents: list[str]) -> None:
    """Fetch the full OpenAlex response for identifiers that have none stored.

    A citation count already in citation_cache.csv makes openalex_lookup() return
    without touching the network, so the full response is never seen again. That
    is right for the citation column and wrong for anything that needs the rest
    of the record, so the backfill is its own explicit pass rather than a silent
    re-fetch inside a normal `make enrich` - the daily budget is metered and a
    surprise 3,700-request sweep would spend most of it.
    """
    todo = [i for i in dict.fromkeys(idents) if not read_openalex_work(ident_key(i))]
    if not todo:
        print("  every identifier already has its full OpenAlex response stored")
        return
    print(f"  {len(todo)} identifiers have no stored response ({openalex_tier()})")
    got = 0
    for n, ident in enumerate(todo, 1):
        kind, _, value = ident.partition(":")
        filt = f"ids.pmid:{value}" if kind == "pmid" else f"doi:{value}"
        try:
            r = session.get(OPENALEX_API, params=openalex_params({"filter": filt}),
                            timeout=30)
            if r.status_code == 429:
                wait = r.headers.get("Retry-After", "?")
                print(f"    stopped at {n}/{len(todo)}: daily budget spent, "
                      f"retry after {wait}s; {got} stored so far", file=sys.stderr)
                return
            if r.status_code != 200 or not (r.json().get("results") or []):
                continue
            save_openalex_work(ident_key(ident), r.json())
            got += 1
        except (requests.RequestException, ValueError):
            continue
        if n % 100 == 0:
            print(f"    {n}/{len(todo)}  stored {got}", flush=True)
    print(f"  stored {got} full responses")


def check_identifiers(session: requests.Session) -> None:
    """Cross-check every bio.tools record that states BOTH a PMID and a DOI.

    `pub_identifiers()` prefers the PMID and discards the DOI, so the DOI is an
    unused second witness to the same paper, recorded independently upstream. If
    the two resolve to different OpenAlex works, one of them was mistyped.

    KNOWN LIMIT, stated up front: this does NOT catch the case that motivated it.
    NOBAI carried `pmid:18449469`, one digit from its real `18448469`, resolving
    to "Ellipsoidal particles at fluid interfaces" and taking that paper's 146
    citations against a true 15 - and bio.tools records the matching physics DOI
    too, so the two identifiers AGREE. They are not independent witnesses: the
    DOI was evidently populated from the bad PMID. Only reading the paper against
    the tool finds that class, which is what `paper_matches` in the describe job
    is for.

    What this check does catch is a genuinely mistyped identifier, where one side
    was entered by hand and the other was not, plus OpenAlex holding two work
    records for one paper with different citation counts.

    Compare WORK IDs, never identifier strings: a PMID and a DOI for one paper
    are not a disagreement, which is the trap the citation audit already hit.
    """
    enriched = read_json(ENRICHED)["list"]
    pairs = []
    for rec in enriched:
        for pub in rec.get("publication") or []:
            md = pub.get("metadata") or {}
            pmid = pub.get("pmid") or md.get("pmid")
            doi = (pub.get("doi") or "").strip().removeprefix("https://doi.org/")
            if pmid and doi:
                pairs.append((rec.get("biotoolsID"), rec.get("name"), str(pmid), doi))
    print(f"{len(pairs)} publication entries state both a PMID and a DOI")

    def work_id(ident):
        key = ident_key(ident)
        w = read_openalex_work(key)
        if w:
            return w.get("id"), (w.get("title"), w.get("cited_by_count")), False
        kind, _, value = ident.partition(":")
        filt = f"ids.pmid:{value}" if kind == "pmid" else f"doi:{value}"
        try:
            r = session.get(OPENALEX_API, params=openalex_params({"filter": filt}), timeout=30)
            if r.status_code == 429:
                raise SystemExit("  OpenAlex daily budget spent; rerun after midnight UTC")
            results = r.json().get("results") or [] if r.status_code == 200 else []
        except (requests.RequestException, ValueError):
            return None, None, True
        if not results:
            return None, None, True
        save_openalex_work(key, r.json())
        return (results[0].get("id"),
                (results[0].get("title"), results[0].get("cited_by_count")), True)

    rows, unresolved, fetched = [], 0, 0
    for n, (bid, name, pmid, doi) in enumerate(pairs, 1):
        pw, pt, f1 = work_id(f"pmid:{pmid}")
        dw, dt, f2 = work_id(f"doi:{doi}")
        fetched += f1 + f2
        if not pw or not dw:
            unresolved += 1
            continue
        if pw != dw:
            # Same title on both sides is OpenAlex holding two work records for
            # one paper, not a mistyped identifier - a different problem with a
            # different fix, and the counts usually differ. Segway is the known
            # case: the PMID copy has 290 citations, the Nature Methods DOI 663.
            ptitle, pcites = pt or ("?", None)
            dtitle, dcites = dt or ("?", None)
            same = (ptitle or "").strip().lower() == (dtitle or "").strip().lower()
            rows.append((bid, name, pmid, ptitle, pcites, doi, dtitle, dcites,
                         "duplicate record" if same else "DIFFERENT PAPER"))
        if n % 200 == 0:
            print(f"  {n}/{len(pairs)}  mismatches {len(rows)}  network calls {fetched}",
                  flush=True)

    dupes = sum(1 for r in rows if r[-1] == "duplicate record")
    print(f"\n  {len(rows)} records where the PMID and the DOI are different works")
    print(f"    {dupes} are one paper held twice by OpenAlex (same title)")
    print(f"    {len(rows) - dupes} resolve to genuinely different papers")
    print(f"  {unresolved} could not be resolved on one side or the other")
    doc = DATA.parent / "docs" / "identifier-check.md"
    out = ["# PMID and DOI disagreement check", "",
           "GENERATED by `pipeline/enrich.py --check-identifiers`. Proposals, not",
           "decisions: promote a correction into `curation/overlay.yaml: publications`.",
           "",
           "bio.tools states both a PMID and a DOI for many records, and the pipeline uses",
           "only the PMID. Where the two resolve to different OpenAlex works, one of them",
           "is mistyped. A PMID typo is silent because PMIDs are dense sequential integers,",
           "so the wrong number is still somebody's paper; a DOI typo 404s.", "",
           "This check has a known blind spot. NOBAI's PMID was one digit out, and",
           "bio.tools records the matching wrong DOI alongside it, so the two agree and",
           "nothing here fires. The identifiers are not independent: the DOI appears to",
           "have been filled in from the bad PMID. Catching that needs the paper read",
           "against the tool, which is `paper_matches` in the describe job.", "",
           f"{len(pairs)} entries checked, {len(rows)} disagree, {unresolved} unresolvable.",
           "",
           "`duplicate record` means both identifiers name the SAME paper and OpenAlex",
           "holds two work entries for it; the fix is to link whichever copy carries the",
           "true citation count. `DIFFERENT PAPER` means one identifier is wrong.", ""]
    if rows:
        out += ["| tool | kind | PMID | resolves to | cites | DOI | resolves to | cites |",
                "| --- | --- | --- | --- | ---: | --- | --- | ---: |"]
        for bid, name, pmid, pt, pc, doi, dt, dc, kind in rows:
            out.append(f"| `{bid}` {name} | {kind} | {pmid} | {(pt or '?')[:58]} | "
                       f"{pc if pc is not None else '?'} | {doi} | {(dt or '?')[:58]} | "
                       f"{dc if dc is not None else '?'} |")
    else:
        out.append("No disagreements found.")
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text("\n".join(out) + "\n")
    print(f"  -> {doc}")


def displayed_identifiers() -> list[str]:
    """Publications the build will show that no harvested record mentions.

    Two sources, together accounting for 148 blank citation cells:

    - `seeds.yaml`. Hand-written entries never appear in the sweep, so iterating
      the harvest alone skips their papers entirely. TOBIAS is a featured tool
      with 251 stars and showed no count for this reason.
    - `publication_map.json`. resolve_pubs.py upgrades a bio.tools preprint DOI
      to the published version, and build.py displays the upgrade, but only the
      preprint is in the harvest. bio.tools records Sierra as bioRxiv
      `10.1101/867309`; the catalog links its Genome Biology paper, whose count
      was never fetched.

    publication_map.json is written by a later stage, so a brand-new upgrade is
    picked up on the following run. Everything already resolved is covered now.
    """
    out: list[str] = []
    seeds_path = CURATION / "seeds.yaml"
    if seeds_path.exists():
        seeds = yaml.safe_load(seeds_path.read_text()) or {}
        for seed in seeds.get("tools") or []:
            if seed.get("pmid"):
                out.append(f"pmid:{seed['pmid']}")
            elif seed.get("doi"):
                out.append(f"doi:{seed['doi']}")
    pubmap_path = CACHE / "publication_map.json"
    if pubmap_path.exists():
        try:
            blob = json.loads(pubmap_path.read_text())
        except ValueError:
            blob = {}
        for entry in blob.values():
            if entry.get("published_doi"):
                out.append(f"doi:{entry['published_doi']}")
    overlay_path = CURATION / "overlay.yaml"
    if overlay_path.exists():
        overlay = yaml.safe_load(overlay_path.read_text()) or {}
        out.extend((overlay.get("publications") or {}).values())
        for entry in (overlay.get("verified_publications") or {}).values():
            out.extend(entry.get("papers") or [])
    return list(dict.fromkeys(out))


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--no-github", action="store_true")
    ap.add_argument("--no-citations", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="process only N records (debug)")
    ap.add_argument("--check-identifiers", action="store_true",
                    help="cross-check records stating both a PMID and a DOI; a "
                         "disagreement means one was mistyped. Writes "
                         "docs/identifier-check.md, then exits")
    ap.add_argument("--backfill-works", action="store_true",
                    help="fetch and store the full OpenAlex response for every "
                         "displayed identifier that has none yet, then exit")
    args = ap.parse_args()

    if args.check_identifiers:
        http = requests.Session()
        http.headers.update({"User-Agent": user_agent(), "Accept": "application/json"})
        check_identifiers(http)
        return

    if args.backfill_works:
        http = requests.Session()
        http.headers.update({"User-Agent": user_agent(), "Accept": "application/json"})
        sweep = read_json(SELECTED)
        idents = [i for t in sweep["list"] for i in pub_identifiers(t)]
        idents += displayed_identifiers()
        print(f"Backfilling full OpenAlex responses for {len(set(idents))} identifiers")
        backfill_works(http, idents)
        return

    sweep = read_json(SELECTED)
    tools = sweep["list"][: args.limit] if args.limit else sweep["list"]
    print(f"Enriching {len(tools)} records")

    http = requests.Session()
    http.headers.update({"User-Agent": user_agent(), "Accept": "application/json"})

    gh = requests.Session()
    gh.headers.update({"Accept": "application/vnd.github+json",
                       "User-Agent": user_agent()})
    token = None if args.no_github else github_token()
    if token:
        gh.headers["Authorization"] = f"Bearer {token}"
        print("  GitHub: authenticated (5000 req/h)")
    elif not args.no_github:
        print("  GitHub: unauthenticated (60 req/h) - set GITHUB_TOKEN or run `gh auth login`")

    gh_cache: dict[str, dict] = json.loads(GH_CACHE.read_text()) if GH_CACHE.exists() else {}
    cite_cache = load_citation_cache()
    print(f"  citation cache: {len(cite_cache)} entries; github cache: {len(gh_cache)} repos")
    if not args.no_citations:
        print(f"  OpenAlex: {openalex_tier()}")

    out = []
    for i, tool in enumerate(tools, 1):
        urls = record_urls(tool)
        buckets = classify_urls(urls)

        slug = None
        for kind, url in buckets["code"]:
            if kind == "github":
                slug = normalise_github(url)
                if slug:
                    break
        repo_source = "biotools" if slug else None
        if not slug:
            for kind, url in buckets["registries"].items():
                slug = resolve_registry_repo(http, kind, url)
                if slug:
                    repo_source = kind
                    break

        gh_info = None
        if slug and not args.no_github:
            if slug not in gh_cache:
                gh_cache[slug] = fetch_github(gh, slug) or {"status": "error"}
            gh_info = gh_cache[slug]
            if gh_info.get("status") == "not_found":
                gh_info = None

        citations, ids, pubmeta = 0, pub_identifiers(tool), {}
        if not args.no_citations:
            for ident in ids:
                n, meta = openalex_lookup(http, ident, cite_cache)
                citations += n or 0        # an unresolved lookup returns None
                if meta and not pubmeta:
                    pubmeta = meta

        other_code = [u for k, u in buckets["code"] if k != "github"]
        out.append({
            **tool,
            "_urls": urls,
            "_repo_slug": slug,
            "_repo_source": repo_source,
            "_repo_other": other_code,
            "_registries": buckets["registries"],
            "_github": gh_info,
            "_identifiers": ids,
            "_citations": citations,
            "_pubmeta": pubmeta,
        })

        if i % 100 == 0:
            print(f"  {i}/{len(tools)}", flush=True)
            GH_CACHE.write_text(json.dumps(gh_cache, indent=1))
            save_citation_cache(cite_cache)

    # Repositories named in seeds.yaml. enrich.py walks the bio.tools sweep, so a
    # curated entry's repo was never queried and every seed showed no stars, no
    # activity, no licence and no language - Enformer, BPNet, DeepSEA, pySCENIC
    # and FIMO among them. Same shape as the citation gap: fetch for what the
    # catalog DISPLAYS, not for what the harvest happens to contain.
    if not args.no_github:
        seeds_path = CURATION / "seeds.yaml"
        slugs = []
        if seeds_path.exists():
            for seed in (yaml.safe_load(seeds_path.read_text()) or {}).get("tools") or []:
                slug = (seed.get("repo") or "").strip().strip("/")
                if slug and slug.count("/") == 1 and slug not in gh_cache:
                    slugs.append(slug)
        if slugs:
            print(f"  {len(slugs)} seed repositories not yet queried")
            for n, slug in enumerate(dict.fromkeys(slugs), 1):
                gh_cache[slug] = fetch_github(gh, slug) or {"status": "error"}
                if n % 20 == 0:
                    print(f"    {n}/{len(slugs)}", flush=True)
                    GH_CACHE.write_text(json.dumps(gh_cache, indent=1))

    GH_CACHE.write_text(json.dumps(gh_cache, indent=1))

    # Papers the catalog displays that the harvest never mentions: seed entries
    # and preprints upgraded to their published version. Skipping these left 148
    # tools with a blank citation cell, TOBIAS and Sierra among them.
    if not args.no_citations:
        extra = [i for i in displayed_identifiers()
                 if f"{i.partition(':')[0]}_{i.partition(':')[2]}"
                 .replace("/", "_").replace(":", "_") not in cite_cache]
        if extra:
            print(f"  {len(extra)} displayed publications not yet in the cache")
            for n_done, ident in enumerate(extra, 1):
                openalex_lookup(http, ident, cite_cache)
                if n_done % 50 == 0:
                    print(f"    {n_done}/{len(extra)}", flush=True)
                    save_citation_cache(cite_cache)

    save_citation_cache(cite_cache)
    write_json(ENRICHED, {"count": len(out), "list": out})

    with_repo = sum(1 for t in out if t["_repo_slug"])
    resolved = sum(1 for t in out if t["_repo_source"] and t["_repo_source"] != "biotools")
    print(f"\n{len(out)} records -> {ENRICHED}")
    print(f"  GitHub repo found: {with_repo} ({with_repo/max(len(out),1):.0%}), "
          f"of which {resolved} recovered via package registries")


if __name__ == "__main__":
    main()
