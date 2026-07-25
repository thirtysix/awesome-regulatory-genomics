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
import json
import os
import re
import subprocess
import sys
import time
from urllib.parse import urlparse

import requests

from jsonio import read_json, write_json
from config import CACHE, CODE_HOSTS, GITHUB_API, OPENALEX_API, RAW, REGISTRY_HOSTS

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
    # Seed from any per-work OpenAlex JSON already on disk.
    if OA_DIR.exists():
        for path in OA_DIR.glob("*.json"):
            key = path.stem
            if key in cache:
                continue
            try:
                results = json.loads(path.read_text()).get("results") or []
            except (ValueError, OSError):
                continue
            if results:
                cache[key] = results[0].get("cited_by_count", 0)
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


def openalex_lookup(session: requests.Session, ident: str, cache: dict[str, int]) -> tuple[int, dict]:
    kind, _, value = ident.partition(":")
    key = f"{kind}_{value}".replace("/", "_").replace(":", "_")
    if key in cache:
        return cache[key], {}
    filt = f"ids.pmid:{value}" if kind == "pmid" else f"doi:{value}"
    try:
        r = session.get(OPENALEX_API, params={"filter": filt,
                                              "mailto": "contact@example.org"}, timeout=30)
        results = r.json().get("results") or [] if r.status_code == 200 else []
    except (requests.RequestException, ValueError):
        results = []
    if not results:
        cache[key] = 0
        return 0, {}
    w = results[0]
    cache[key] = w.get("cited_by_count", 0)
    return cache[key], {"title": w.get("title"), "year": w.get("publication_year"),
                        "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name")}


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--no-github", action="store_true")
    ap.add_argument("--no-citations", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="process only N records (debug)")
    args = ap.parse_args()

    sweep = read_json(SELECTED)
    tools = sweep["list"][: args.limit] if args.limit else sweep["list"]
    print(f"Enriching {len(tools)} records")

    http = requests.Session()
    http.headers.update({"User-Agent": "awesome-regulatory-genomics/1.0",
                         "Accept": "application/json"})

    gh = requests.Session()
    gh.headers.update({"Accept": "application/vnd.github+json",
                       "User-Agent": "awesome-regulatory-genomics/1.0"})
    token = None if args.no_github else github_token()
    if token:
        gh.headers["Authorization"] = f"Bearer {token}"
        print("  GitHub: authenticated (5000 req/h)")
    elif not args.no_github:
        print("  GitHub: unauthenticated (60 req/h) - set GITHUB_TOKEN or run `gh auth login`")

    gh_cache: dict[str, dict] = json.loads(GH_CACHE.read_text()) if GH_CACHE.exists() else {}
    cite_cache = load_citation_cache()
    print(f"  citation cache: {len(cite_cache)} entries; github cache: {len(gh_cache)} repos")

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
                citations += n
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

    GH_CACHE.write_text(json.dumps(gh_cache, indent=1))
    save_citation_cache(cite_cache)
    write_json(ENRICHED, {"count": len(out), "list": out})

    with_repo = sum(1 for t in out if t["_repo_slug"])
    resolved = sum(1 for t in out if t["_repo_source"] and t["_repo_source"] != "biotools")
    print(f"\n{len(out)} records -> {ENRICHED}")
    print(f"  GitHub repo found: {with_repo} ({with_repo/max(len(out),1):.0%}), "
          f"of which {resolved} recovered via package registries")


if __name__ == "__main__":
    main()
