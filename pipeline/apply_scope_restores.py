#!/usr/bin/env python3
"""Restore tools a drifted scope prompt excluded, by seeding their bio.tools ids.

Decisions arrive as a json map of bio.tools id -> restore | leave, from the
review page's Copy button.

Seeding is the right lever, and it took a wrong turn to understand why. All of
these records already PASS select_domain.classify(); adding them as seeds looks
redundant on that basis, and was reverted once for exactly that reason. But
build.py protects a row whose _select_reason starts with "curated", and only a
protected row survives llm_out_of_scope. The filter admits them and the scope
audit downstream drops them again, so seeding is not about admission - it is
about immunity from the stage that was wrong.

    python pipeline/apply_scope_restores.py --decisions review.json          # dry run
    python pipeline/apply_scope_restores.py --decisions review.json --apply
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "pipeline" / "config.py"
AUDIT = ROOT / "data" / "raw" / "scope_restore_candidates.json"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--decisions", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    marks = json.loads(Path(args.decisions).read_text())
    audit = {r["biotools_id"]: r for r in json.loads(AUDIT.read_text())} if AUDIT.exists() else {}

    sys.path.insert(0, str(ROOT / "pipeline"))
    from config import SEED_BIOTOOLS_IDS
    have = {s.lower() for s in SEED_BIOTOOLS_IDS}

    add, skip = [], []
    for bid, verdict in marks.items():
        if (verdict.get("verdict") if isinstance(verdict, dict) else verdict) != "restore":
            continue
        if bid.lower() in have:
            skip.append((bid, "already seeded")); continue
        add.append(bid)

    print(f"decisions read : {len(marks)}")
    print(f"  to seed      : {len(add)}")
    if skip:
        print(f"  skipped      : {len(skip)}")
        for b, why in skip:
            print(f"      {b[:26]:28s} {why}")
    if not add:
        print("nothing to write"); return

    stamp = dt.date.today().isoformat()
    width = max(len(b) for b in add) + 3
    block = (f"\n    # Restored {stamp}. Each was excluded by the scope audit under a\n"
             f"    # prompt that listed the in-scope domains by hand and had drifted out of\n"
             f"    # sync with CATEGORIES; re-audited with the generated taxonomy and\n"
             f"    # confirmed by a second model that is genuinely a second model, which the\n"
             f"    # original exclusions only appeared to have. They are seeded rather than\n"
             f"    # merely re-admitted because classify() already passes them - it is the\n"
             f"    # scope audit that drops them, and only a curated row is protected.\n")
    for bid in add:
        why = (audit.get(bid, {}).get("bulk_reason") or "").split(".")[0][:66]
        block += f'    "{bid}",'.ljust(width + 8) + (f"# {why}\n" if why else "\n")

    src = CONFIG.read_text()
    i = src.index("SEED_BIOTOOLS_IDS = [")
    j = src.index("\n]\n", i)
    merged = src[:j + 1] + block + src[j + 1:]

    # Parse the result before writing it, and check every id survived.
    # config.py reads __file__ to locate the data directory, so the namespace
    # has to supply it or the check fails on the module rather than the edit.
    ns: dict = {"__file__": str(CONFIG), "__name__": "config_check"}
    try:
        exec(compile(merged, str(CONFIG), "exec"), ns)
    except Exception as e:
        raise SystemExit(f"refusing to write: the edited config does not parse ({e})")
    got = {s.lower() for s in ns.get("SEED_BIOTOOLS_IDS", [])}
    missing = {b.lower() for b in add} - got
    if missing:
        raise SystemExit(f"refusing to write: {sorted(missing)} did not survive the edit")
    if len(ns["SEED_BIOTOOLS_IDS"]) != len(set(ns["SEED_BIOTOOLS_IDS"])):
        raise SystemExit("refusing to write: the edit introduced a duplicate id")
    print(f"config.py parses; SEED_BIOTOOLS_IDS {len(SEED_BIOTOOLS_IDS)} -> {len(got)}")
    print("\n--- would append ---")
    print(block[:900] + ("    ...\n" if len(block) > 900 else ""))

    if not args.apply:
        print("dry run; pass --apply to write")
        return
    CONFIG.write_text(merged)
    print(f"seeded {len(add)} ids into {CONFIG.relative_to(ROOT)}")
    print("run `make build` to rebuild the catalog with them")


if __name__ == "__main__":
    main()
