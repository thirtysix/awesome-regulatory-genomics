#!/usr/bin/env python3
"""Stage 1 - harvest candidate records from bio.tools.

Recall comes from a wide sweep (EDAM operation queries + free-text queries);
precision comes from a later filter on the annotations a record actually
carries. Writes every raw record to data/raw/biotools_sweep.json together with
a provenance log of which query surfaced it.

    python pipeline/harvest.py [--max-pages N] [--refresh]
"""
from __future__ import annotations

import argparse
import json
import sys
import time

import requests

from jsonio import read_json, write_json
from config import (BIOTOOLS_API, user_agent, QUERY_FREETEXT, QUERY_OPERATIONS,
                    QUERY_TOPICS, RAW, SEED_BIOTOOLS_IDS)

SWEEP = RAW / "biotools_sweep.json.gz"


def make_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "Accept": "application/json",
        "User-Agent": user_agent(),
    })
    return s


def paged_query(session: requests.Session, param: str, value: str, max_pages: int) -> dict:
    """Fetch every page for one bio.tools query.

    Values are always quoted. Unquoted terms are tokenised by the API, so a
    query like ``q=cis-regulatory`` matches anything containing "cis" or
    "regulatory" and returns thousands of off-domain records.
    """
    found: dict[str, dict] = {}
    page = 1
    term = f'"{value}"'
    while page <= max_pages:
        try:
            r = session.get(
                BIOTOOLS_API,
                params={param: term, "format": "json", "page": page},
                timeout=45,
            )
            r.raise_for_status()
            payload = r.json()
        except (requests.RequestException, ValueError) as exc:
            print(f"    ! {param}={value!r} page {page}: {exc}", file=sys.stderr)
            break
        batch = payload.get("list") or []
        if not batch:
            break
        for tool in batch:
            found[tool["biotoolsID"]] = tool
        if not payload.get("next"):
            break
        page += 1
        time.sleep(0.1)
    return found


def fetch_by_id(session: requests.Session, biotools_id: str) -> dict | None:
    """Fetch one record directly, for tools no query reaches."""
    try:
        r = session.get(f"{BIOTOOLS_API}{biotools_id}/", params={"format": "json"}, timeout=30)
        r.raise_for_status()
        return r.json()
    except (requests.RequestException, ValueError) as exc:
        print(f"    ! id={biotools_id}: {exc}", file=sys.stderr)
        return None


def harvest(max_pages: int) -> dict:
    session = make_session()
    records: dict[str, dict] = {}
    provenance: dict[str, list[str]] = {}
    log: list[dict] = []

    plan = ([("operation", v) for v in QUERY_OPERATIONS]
            + [("topic", v) for v in QUERY_TOPICS]
            + [("q", v) for v in QUERY_FREETEXT])
    for param, value in plan:
        hits = paged_query(session, param, value, max_pages)
        new = 0
        for bid, tool in hits.items():
            if bid not in records:
                records[bid] = tool
                new += 1
            provenance.setdefault(bid, []).append(f"{param}={value}")
        log.append({"param": param, "value": value, "hits": len(hits),
                    "new": new, "cumulative": len(records)})
        print(f"  {param:9s} {value[:46]:46s} hits={len(hits):5d} new={new:5d} "
              f"cum={len(records):5d}", flush=True)

    # `forced` lists every curated ID present in the sweep, not only the ones
    # fetched here. A record can be harvested by a query and still fail the
    # selection filter (uniprobe carries no domain topic), so being curated has
    # to override the filter regardless of how the record arrived.
    fetched = []
    for biotools_id in SEED_BIOTOOLS_IDS:
        if biotools_id in records:
            continue
        record = fetch_by_id(session, biotools_id)
        if record:
            records[biotools_id] = record
            provenance.setdefault(biotools_id, []).append("id (curated)")
            fetched.append(biotools_id)
            time.sleep(0.1)
    forced = [i for i in SEED_BIOTOOLS_IDS if i in records]
    print(f"  curated by ID: {len(forced)} ({len(fetched)} needed a direct fetch)", flush=True)

    return {"count": len(records), "queries": log, "forced": forced,
            "provenance": provenance, "list": list(records.values())}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--max-pages", type=int, default=60,
                    help="page cap per query (bio.tools returns 10/page)")
    ap.add_argument("--allow-shrink", action="store_true",
                    help="write the sweep even if it is far smaller than last time")
    ap.add_argument("--refresh", action="store_true",
                    help="re-run even if a sweep already exists")
    args = ap.parse_args()

    if SWEEP.exists() and not args.refresh:
        print(f"{SWEEP} exists; pass --refresh to re-harvest.")
        return

    RAW.mkdir(parents=True, exist_ok=True)
    print(f"Sweeping bio.tools: {len(QUERY_OPERATIONS)} operation, "
          f"{len(QUERY_TOPICS)} topic, {len(QUERY_FREETEXT)} free-text queries")
    result = harvest(args.max_pages)
    # A harvest that collapses must not be written. On 2026-08-02 bio.tools
    # search returned count=0 for every query, including a bare unfiltered one,
    # while direct fetches by ID still worked. 70 records got through, the
    # pipeline built a 204-tool catalog from them without complaint, and the
    # monthly job opened a pull request proposing it: 1,763 tools down to 204.
    # The outage was upstream and brief. Accepting its output silently was ours.
    previous = 0
    if SWEEP.exists():
        try:
            previous = read_json(SWEEP).get("count", 0)
        except Exception:                                    # noqa: BLE001
            previous = 0
    floor = int(previous * 0.75)
    if previous and result["count"] < floor and not args.allow_shrink:
        sys.exit(
            f"\nHarvest collapsed: {result['count']} records against {previous} "
            f"last time (floor {floor}).\n"
            f"  Nothing was written; the previous sweep is intact.\n"
            f"  Check the upstream API before re-running: a bare\n"
            f"  https://bio.tools/api/tool/?format=json should report a non-zero count.\n"
            f"  Override with --allow-shrink once you know why it shrank.")

    write_json(SWEEP, result)
    print(f"\n{result['count']} unique records -> {SWEEP}")


if __name__ == "__main__":
    main()
