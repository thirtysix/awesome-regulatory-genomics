#!/usr/bin/env python3
"""Stage 5 - measure recall against a hand-written benchmark.

Turns "does this list contain the obvious tools?" into a number that moves when
the selection rules change. Every miss is a bug in either `pipeline/config.py`
(if the tool is in bio.tools) or `curation/seeds.yaml` (if it is not); passing
``--probe`` asks bio.tools which of the two it is.

Writes docs/coverage.md.

    python pipeline/audit_coverage.py [--probe]
"""
from __future__ import annotations

import argparse
import json
import re
import time
from datetime import date

import requests
import yaml

from jsonio import read_json
from config import BIOTOOLS_API, CURATION, DATA, DOCS, RAW, user_agent
from mdutil import cell

CATALOG = DATA / "catalog.json"
BENCHMARK = CURATION / "benchmark.yaml"
REPORT = DOCS / "coverage.md"


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def build_index(tools: list[dict]) -> dict[str, dict]:
    index: dict[str, dict] = {}
    for t in tools:
        for key in (t["name"], t.get("biotools_id") or ""):
            if key:
                index.setdefault(norm(key), t)
    return index


def lookup(entry: dict, index: dict[str, dict]) -> dict | None:
    names = [entry["name"], *(entry.get("aka") or [])]
    for n in names:
        hit = index.get(norm(n))
        if hit:
            return hit
    # Allow a short suffix, so "MEME" matches "MEME Suite" but not "MEMEChIP".
    for n in names:
        k = norm(n)
        if len(k) < 4:
            continue
        for key, tool in index.items():
            if key.startswith(k) and len(key) <= len(k) + 6:
                return tool
    return None


def probe_biotools(session: requests.Session, name: str) -> str | None:
    """Is this tool in bio.tools at all? Distinguishes a rule bug from a gap.

    **This matches on the name, so the answer is a lead and not a fact.**
    Checked by hand, three of the eight hits from one run were different tools
    that merely share a name: `Thor` is a spatial-transcriptomics package
    rather than the RGT differential peak caller, and `inps` and `maestro` are
    protein-stability predictors rather than the nucleosome and single-cell
    tools meant here. Acting on this output without opening the record is how
    the FiMO error reached the README (see docs/provenance.md), so the report
    states the caveat rather than presenting the ID as settled.
    """
    try:
        r = session.get(BIOTOOLS_API, params={"name": f'"{name}"', "format": "json"}, timeout=25)
        for tool in r.json().get("list", []):
            if norm(tool["name"]) == norm(name):
                return tool["biotoolsID"]
    except (requests.RequestException, ValueError):
        return None
    return None


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--probe", action="store_true",
                    help="query bio.tools for each miss to classify it")
    args = ap.parse_args()

    catalog = json.loads(CATALOG.read_text())
    index = build_index(catalog["tools"])
    benchmark = yaml.safe_load(BENCHMARK.read_text())

    # Distinguishing "never harvested" from "harvested then rejected" is the
    # whole point: the two failures need opposite fixes.
    sweep_path, reject_path = RAW / "biotools_sweep.json.gz", RAW / "rejected.json"
    swept = ({t["biotoolsID"] for t in read_json(sweep_path)["list"]}
             if sweep_path.exists() else set())
    rejected = ({t["biotoolsID"]: t["reason"] for t in read_json(reject_path)["list"]}
                if reject_path.exists() else {})

    session = requests.Session()
    session.headers.update({"Accept": "application/json",
                            "User-Agent": user_agent()})

    sections, hits, total, misses = [], 0, 0, []
    for group, entries in benchmark.items():
        rows = []
        for entry in entries:
            total += 1
            found = lookup(entry, index)
            if found:
                hits += 1
                via = "curated seed" if found["source"] == "curated" else "bio.tools"
                rows.append((entry["name"], "yes", found["name"], via))
            else:
                reason = "not found"
                if args.probe:
                    probe = probe_biotools(session, entry["name"])
                    time.sleep(0.12)
                    if not probe:
                        reason = "absent from bio.tools; add to `seeds.yaml`"
                    elif probe in rejected:
                        reason = (f"harvested as `{probe}`, then rejected "
                                  f"({rejected[probe]}); selection rule too strict")
                    elif probe in swept:
                        reason = f"harvested as `{probe}` but not selected; check `select_domain.py`"
                    else:
                        reason = (f"a bio.tools record is *named* `{probe}` but was never "
                                  "harvested. **Open it before acting**: the match is on "
                                  "name alone, and roughly a third of these are a "
                                  "different tool. If it is the right one, add it to "
                                  "`SEED_BIOTOOLS_IDS`; if not, it belongs in `seeds.yaml`")
                rows.append((entry["name"], "no", "", reason))
                misses.append((group, entry["name"], reason))
        sections.append((group, rows))

    pct = hits / max(total, 1)
    out = []
    A = out.append
    A("# Coverage audit")
    A("")
    A(f"Generated {date.today().isoformat()} by `make audit`, against "
      f"[`curation/benchmark.yaml`](../curation/benchmark.yaml).")
    A("")
    A("The benchmark is a hand-written list of resources the field treats as "
      "standard. It is not a ranking and not exhaustive. It exists so that "
      "\"did the pipeline find the obvious things?\" is a measurement rather "
      "than an impression.")
    A("")
    A(f"**{hits} of {total} benchmark tools present ({pct:.0%}).** "
      f"Catalog size: {catalog['meta']['count']} tools.")
    A("")
    if misses:
        A("## Misses")
        A("")
        A("Each of these is a bug, and the diagnosis says which kind. "
          "*Never harvested* means no query reaches the record, so widen "
          "`QUERY_TOPICS` or `QUERY_FREETEXT`. *Rejected* means the selection "
          "rules in `pipeline/config.py` are too strict. *Absent from "
          "bio.tools* means it belongs in `curation/seeds.yaml`.")
        A("")
        A("| Group | Tool | Diagnosis |")
        A("| --- | --- | --- |")
        for group, name, reason in misses:
            A(f"| {cell(group)} | {cell(name)} | {cell(reason)} |")
        A("")
    else:
        A("No misses.")
        A("")

    A("## Full results")
    A("")
    for group, rows in sections:
        got = sum(1 for r in rows if r[1] == "yes")
        A(f"### {group}: {got}/{len(rows)}")
        A("")
        A("| Benchmark tool | Present | Catalog entry | Source / diagnosis |")
        A("| --- | :---: | --- | --- |")
        for name, present, entry, note in rows:
            mark = "✅" if present == "yes" else "❌"
            A(f"| {cell(name)} | {mark} | {cell(entry)} | {cell(note)} |")
        A("")

    DOCS.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(out))
    print(f"benchmark recall: {hits}/{total} ({pct:.0%}) -> {REPORT}")
    for group, name, reason in misses:
        print(f"  MISS  {name:22s} {reason}")


if __name__ == "__main__":
    main()
