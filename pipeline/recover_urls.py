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
import time
from pathlib import Path

import requests

from config import user_agent
from jsonio import read_json, write_json
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


def from_registries(http: requests.Session, name: str) -> tuple[str, str]:
    for fn, label in ((from_pypi, "pypi"), (from_bioconda, "bioconda"),
                      (from_bioconductor, "bioconductor"), (from_cran, "cran")):
        try:
            got = fn(http, name)
        except Exception:
            got = None
        if got:
            url = next((x for x in got if isinstance(x, str) and x.startswith("http")), "")
            if url:
                return url, label
    return "", ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True,
                    help="json with a list of {name, description, url?}")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--search-budget", type=int, default=40,
                    help="GitHub search calls; the API allows 30/min")
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

    out = {}
    for t in rows:
        name, found, how = t["name"], "", ""
        url, why = from_registries(http, name)
        if url:
            found, how = url, f"registry:{why}"
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
