#!/usr/bin/env python3
"""Re-check that changes contributed upstream are still in place.

bio.tools keeps no contribution history. An edit to a record you do not own
appears nowhere in your profile, and the record stores only a `lastUpdate`
timestamp with no editor and no diff. `curation/upstream-log.yaml` is therefore
the only durable record that a change was ever made, and this reads it back
against the live registry.

A reverted change is a result, not a failure. Upstream may disagree, or a later
automated import may overwrite the field, and either is worth knowing. Nothing
here rewrites the log: it reports, and a human decides.

Read-only, no token needed.

    python pipeline/verify_upstream.py [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request

from config import CURATION

import yaml

LOG = CURATION / "upstream-log.yaml"
API = "https://bio.tools/api/tool/{}/?format=json"


def fetch(record: str) -> dict | None:
    try:
        with urllib.request.urlopen(API.format(record), timeout=30) as r:
            return json.load(r)
    except Exception:                                        # noqa: BLE001
        return None


def dig(d: dict, path: str):
    cur = d
    for part in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def check(entry: dict, live: dict | None) -> tuple[str, str]:
    """Returns (verdict, detail). Verdict is holds / REVERTED / pending / unknown."""
    v = entry.get("verify") or {}
    kind = v.get("kind")
    if kind == "exists":
        want = bool(v.get("expect", True))
        got = live is not None
        return ("holds" if got == want else "REVERTED",
                "record present" if got else "record not found")
    if live is None:
        return "unknown", "could not fetch the record"
    if kind == "json-path":
        got = dig(live, v["path"])
        return ("holds" if got == v.get("expect") else "REVERTED",
                f"{v['path']} = {got!r}")
    if kind == "operation-absent":
        ops = [o["term"] for f in live.get("function") or []
               for o in f.get("operation") or []]
        gone = v["operation"] not in ops
        return ("holds" if gone else "REVERTED",
                f"operations = {ops}")
    if kind == "publication-is":
        ids = []
        for p in live.get("publication") or []:
            md = p.get("metadata") or {}
            if p.get("pmid") or md.get("pmid"):
                ids.append("pmid:" + str(p.get("pmid") or md.get("pmid")))
            if p.get("doi"):
                ids.append("doi:" + p["doi"])
        want = v.get("expect", "")
        hit = any(i.lower() == want.lower() for i in ids)
        # A pending proposal that has not been acted on is not a reversion.
        state = entry.get("state")
        if not hit and state == "pending":
            return "pending", f"still {ids}"
        return ("holds" if hit else "REVERTED", f"publication = {ids}")
    return "unknown", "no verify rule"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    entries = (yaml.safe_load(LOG.read_text()) or {}).get("contributions") or []
    out, counts = [], {}
    for e in entries:
        live = fetch(e["record"]) if e.get("registry") == "bio.tools" else None
        verdict, detail = check(e, live)
        counts[verdict] = counts.get(verdict, 0) + 1
        out.append(dict(date=str(e["date"]), record=e["record"], route=e.get("route"),
                        field=e.get("field"), state=e.get("state"),
                        verdict=verdict, detail=detail))

    if args.json:
        print(json.dumps(out, indent=1))
    else:
        print(f"{'date':<12}{'record':<18}{'route':<12}{'verdict':<10}detail")
        for r in out:
            print(f"{r['date']:<12}{r['record']:<18}{str(r['route']):<12}"
                  f"{r['verdict']:<10}{r['detail'][:70]}")
        print("\n" + "  ".join(f"{k}: {v}" for k, v in sorted(counts.items())))
    if counts.get("REVERTED"):
        print("\nSomething that was applied is no longer in place. Read it before "
              "re-applying: upstream may have had a reason.", file=sys.stderr)


if __name__ == "__main__":
    main()
