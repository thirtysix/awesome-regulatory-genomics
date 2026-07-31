#!/usr/bin/env python3
"""Stage 2e - fill the fields the catalog knows but does not say.

Two gaps, both recoverable from data already in hand rather than from new
judgement:

**Year.** 754 tools carry a publication identifier and no year. bio.tools
records a date inconsistently, and a hand-written seed has none at all, but
OpenAlex knows the publication year of every DOI and PMID here. This is the
same lookup the citation counts already use, so the marginal cost is one field.

**Licence.** 85 tools declare no licence while their resolved repository has
one in its metadata. A repository's licence is not the same claim as a declared
one, so it is recorded as such: `license_source` says `declared` or
`repository`, and the fallback never overwrites a declared value.

Both write caches that `build.py` merges, so the fill is reproducible and the
network pass does not have to run on every build.

    python pipeline/fill_metadata.py [--limit N]
"""
from __future__ import annotations

import argparse
import html
import json
import re
import time

import requests

from build import cache_key
from config import CACHE, DATA, OPENALEX_API, openalex_params, user_agent

YEAR_CACHE = CACHE / "pubyear_cache.json"
# Title and venue, kept in their own cache so the year cache's simple
# key -> "YYYY" shape (which build.py reads directly) stays unchanged.
TITLE_CACHE = CACHE / "pubtitle_cache.json"


def load_year_cache() -> dict[str, str]:
    if YEAR_CACHE.exists():
        try:
            return json.loads(YEAR_CACHE.read_text())
        except ValueError:
            return {}
    return {}


def save_year_cache(cache: dict[str, str]) -> None:
    YEAR_CACHE.parent.mkdir(parents=True, exist_ok=True)
    YEAR_CACHE.write_text(json.dumps(cache, indent=1, sort_keys=True))


def load_title_cache() -> dict[str, dict]:
    if TITLE_CACHE.exists():
        try:
            return json.loads(TITLE_CACHE.read_text())
        except ValueError:
            return {}
    return {}


def save_title_cache(cache: dict[str, dict]) -> None:
    TITLE_CACHE.parent.mkdir(parents=True, exist_ok=True)
    TITLE_CACHE.write_text(json.dumps(cache, indent=1, sort_keys=True))


def clean_title(text: str) -> str:
    """Strip the markup OpenAlex leaves in titles.

    Titles arrive with HTML in them - "SArKS: <i>de novo</i> discovery ..." -
    which would be rendered literally in a spreadsheet cell.
    """
    text = re.sub(r"<[^>]+>", "", text or "")
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def openalex_work(session: requests.Session, ident: str) -> dict:
    """Year, title, venue and per-year citation counts, in a single request.

    `counts_by_year` costs nothing extra here and answers the question a total
    cannot: whether a tool is still being used. A 2004 paper with 13,000
    citations and one with 400 look very different once you ask how many arrived
    last year.
    """
    kind, _, value = ident.partition(":")
    filt = f"ids.pmid:{value}" if kind == "pmid" else f"doi:{value}"
    try:
        r = session.get(OPENALEX_API, params=openalex_params(
            {"filter": filt,
             "select": "publication_year,title,primary_location,counts_by_year"}),
            timeout=30)
        results = r.json().get("results") or [] if r.status_code == 200 else []
    except (requests.RequestException, ValueError):
        return {}
    if not results:
        return {}
    w = results[0]
    venue = ((w.get("primary_location") or {}).get("source") or {}).get("display_name") or ""
    by_year = {str(c["year"]): c.get("cited_by_count") or 0
               for c in (w.get("counts_by_year") or []) if c.get("year")}
    return {"year": str(w.get("publication_year") or ""),
            "title": clean_title(w.get("title") or ""),
            "venue": clean_title(venue),
            "by_year": by_year}


def openalex_year(session: requests.Session, ident: str) -> str:
    return openalex_work(session, ident).get("year", "")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, help="look up at most N years this run")
    args = ap.parse_args()

    catalog = json.loads((DATA / "catalog.json").read_text())
    tools = catalog["tools"]

    # --- licence, offline -------------------------------------------------
    fallback = sum(1 for t in tools
                   if not t.get("license") and t.get("repo_license"))
    print(f"licence: {fallback} tools can fall back to their repository's licence "
          "(applied by build.py, no lookup needed)")

    # --- year, from OpenAlex ---------------------------------------------
    cache = load_year_cache()
    want = []
    for tool in tools:
        ident = tool.get("publication")
        if tool.get("year") or not ident:
            continue
        key = cache_key(ident)
        if key not in cache:
            want.append((key, ident))
    # One identifier can be shared by several tools; look it up once.
    seen, todo = set(), []
    for key, ident in want:
        if key not in seen:
            seen.add(key)
            todo.append((key, ident))
    if args.limit:
        todo = todo[:args.limit]

    print(f"year: {len(todo)} publications to look up "
          f"({len(cache)} already cached)")
    if todo:
        session = requests.Session()
        session.headers.update({"User-Agent": user_agent()})
        found = 0
        for i, (key, ident) in enumerate(todo, 1):
            year = openalex_year(session, ident)
            cache[key] = year          # "" is a real answer: do not re-ask
            found += bool(year)
            if i % 100 == 0:
                print(f"  {i}/{len(todo)} (resolved {found})")
                save_year_cache(cache)
            time.sleep(0.11)           # OpenAlex asks for ~10/s at most
        save_year_cache(cache)
        print(f"year: resolved {found}/{len(todo)}")

    # --- title and venue, from OpenAlex ----------------------------------
    # The catalog links a paper as `pmid:18798982`, which tells a reader
    # nothing and is not clickable in a spreadsheet. Caching the title and
    # venue lets build.py carry both, plus a resolvable URL.
    titles = load_title_cache()
    pubs, seen2 = [], set()
    for tool in tools:
        ident = tool.get("publication")
        if not ident:
            continue
        key = cache_key(ident)
        # An entry cached before by_year existed is refetched once.
        if (key in titles and "by_year" in titles[key]) or key in seen2:
            continue
        seen2.add(key)
        pubs.append((key, ident))
    if args.limit:
        pubs = pubs[:args.limit]
    print(f"title: {len(pubs)} publications to look up "
          f"({len(titles)} already cached)")
    if pubs:
        session = requests.Session()
        session.headers.update({"User-Agent": user_agent()})
        got = 0
        for i, (key, ident) in enumerate(pubs, 1):
            rec = openalex_work(session, ident)
            # Cache the miss too, as an empty record, so a paper OpenAlex does
            # not index is not re-queried on every run.
            titles[key] = {"title": rec.get("title", ""),
                           "venue": rec.get("venue", ""),
                           "by_year": rec.get("by_year", {})}
            got += bool(rec.get("title"))
            if i % 100 == 0:
                print(f"  {i}/{len(pubs)} (resolved {got})")
                save_title_cache(titles)
            time.sleep(0.11)
        save_title_cache(titles)
        print(f"title: resolved {got}/{len(pubs)}")


if __name__ == "__main__":
    main()
