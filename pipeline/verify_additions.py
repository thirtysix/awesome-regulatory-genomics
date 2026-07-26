#!/usr/bin/env python3
"""Independent check on records admitted by hand or by a loosened rule.

Removing a record already needs two models to agree (``verify-scope``). Adding
one had no equivalent check, which is the weaker half: the catalog grew by
several hundred entries on the strength of an adjudication pass by a single
model plus my own reading, and records listed in ``SEED_BIOTOOLS_IDS`` are
deliberately immune to every automated filter.

This asks a DIFFERENT model, one not used for the adjudication, whether each
such record belongs. It decides nothing: disagreements are written to
docs/addition-review.md for a human to settle. The asymmetry is intentional -
a wrongly included tool is visible and reportable, a wrongly excluded one is
invisible, so the bar for adding stays lower than the bar for removing.

    export DEEPINFRA_API_KEY=...
    python pipeline/verify_additions.py [--model zai-org/GLM-5]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

import yaml

from config import CURATION, DATA, DOCS, RAW, SEED_BIOTOOLS_IDS
from jsonio import read_json
from llm_assist import CATEGORISE_SYSTEM, call, digest, parse_json, tool_prompt
from mdutil import cell

ENRICHED = RAW / "enriched.json.gz"
CACHE = DATA / "cache" / "llm.json"
REPORT = DOCS / "addition-review.md"
PROPOSALS = CURATION / "llm_proposals.yaml"

# Deliberately not the adjudication model, and not its escalation target: an
# independent third opinion is worth more than a rerun of either.
DEFAULT_MODEL = "zai-org/GLM-5"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--workers", type=int, default=10)
    args = ap.parse_args()

    api_key = os.environ.get("DEEPINFRA_API_KEY") or os.environ.get("DEEPINFRA_TOKEN")
    if not api_key:
        sys.exit("DEEPINFRA_API_KEY is not set.")

    # Read the SELECTED records, not the built catalog. build.py drops what this
    # stage votes out, so voting on its output oscillates: with the records
    # dropped there is nothing left to vote against, the next build restores
    # them, the next run votes them out again, and the catalog flips by ~57
    # tools on every cycle. Judging the pre-drop set makes the verdict a
    # function of the data rather than of the previous run.
    tools = [{"id": t["biotoolsID"],
              "name": t["name"],
              "description": t.get("description") or "",
              "_select_reason": t.get("_select_reason", ""),
              "_operations": sorted({op["term"]
                                     for fn in t.get("function") or []
                                     for op in fn.get("operation") or []}),
              "topics": [x["term"] for x in t.get("topic") or []],
              "tool_type": t.get("toolType") or [],
              "biotools_url": f"https://bio.tools/{t['biotoolsID']}",
              "homepage": t.get("homepage") or ""}
             for t in read_json(ENRICHED)["list"]]
    curated = set(SEED_BIOTOOLS_IDS)
    # Records admitted by hand, or by a text rule rather than an ontology term.
    # Those admitted by a STRONG EDAM operation are left alone: they were not
    # part of the loosening.
    targets = [t for t in tools
               if t["id"] in curated
               or t.get("_select_reason", "").startswith(("text:", "curated"))]
    print(f"checking {len(targets)} admitted records with {args.model}")

    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    lock = threading.Lock()
    spend = {"total": 0.0}

    def check(t):
        key = f"verify-add:{args.model}:{digest(t['name'], t.get('description') or '')}"
        with lock:
            if key in cache:
                return t, cache[key]
        try:
            text, cost, _ = call(args.model, CATEGORISE_SYSTEM, tool_prompt(t), api_key)
        except Exception:                                    # noqa: BLE001
            return t, None
        with lock:
            spend["total"] += cost
        res = parse_json(text)
        if not (res and isinstance(res.get("in_scope"), bool)):
            return t, None
        with lock:
            cache[key] = res
        return t, res

    disputed, checked = [], 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for fut in as_completed([pool.submit(check, t) for t in targets]):
            t, res = fut.result()
            checked += 1
            if res and not res["in_scope"]:
                disputed.append((t, res))
            if checked % 100 == 0:
                print(f"  {checked}/{len(targets)}  ${spend['total']:.3f}", flush=True)
                CACHE.write_text(json.dumps(cache))

    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache))

    # Majority verdict across every independent opinion already on record:
    # the bulk categoriser, the verify-scope second opinion, and this third
    # model. Two out-of-scope votes from different models is a stronger signal
    # than any single pass, and it costs nothing extra to compute.
    majority = {}
    for t in tools:
        d = digest(t["name"], t.get("description") or "")
        opinions = {}
        cat_key = ("categorise:deepseek-ai/DeepSeek-V4-Flash:"
                   + digest(t["name"], t.get("description") or "",
                            ",".join(t.get("_operations") or [])))
        for name, key in (("bulk", cat_key),
                          ("second", f"verify-scope:deepseek-ai/DeepSeek-V3.1-Terminus:{d}"),
                          ("third", f"verify-add:{args.model}:{d}")):
            got = cache.get(key)
            if got is not None and isinstance(got.get("in_scope"), bool):
                opinions[name] = got["in_scope"]
        against = [k for k, ok in opinions.items() if ok is False]
        if len(against) >= 2:
            majority[t["id"]] = {"name": t["name"], "against": against,
                                 "description": (t.get("description") or "")[:160]}

    props = yaml.safe_load(PROPOSALS.read_text()) if PROPOSALS.exists() else {}
    props = props or {}
    props["majority_out_of_scope"] = majority
    PROPOSALS.write_text(
        "# GENERATED by pipeline/llm_assist.py and pipeline/verify_additions.py.\n"
        "# Proposals, not decisions. build.py merges this BELOW curation/overlay.yaml,\n"
        "# so any hand-written correction always wins.\n\n"
        + yaml.safe_dump(props, sort_keys=True, width=100, allow_unicode=True))
    print(f"majority out-of-scope (>=2 independent votes): {len(majority)}")

    disputed.sort(key=lambda x: x[0]["name"].lower())
    out = ["# Addition review", "",
           f"Generated {date.today().isoformat()} by `pipeline/verify_additions.py` "
           f"using `{args.model}`, a model used for neither the adjudication nor its "
           "escalation.", "",
           "Removing a record needs two models to agree. Adding one had no equivalent "
           "check, so this asks an independent third model about every record admitted "
           "by hand or by a text rule rather than an ontology term.", "",
           f"**{len(targets)} records checked, {len(disputed)} disputed "
           f"({len(disputed)/max(len(targets),1):.0%}).**", "",
           "Nothing here is applied. A dispute is a prompt to re-read the entry, not a "
           "verdict: the model sees only the bio.tools name and description, which is "
           "exactly the text that was misleading in the first place. It has been right "
           "and wrong here: it correctly caught that bio.tools' `mast` is the "
           "single-cell package rather than the MEME Suite scanner, and it "
           "wrongly objects to plainly in-scope entries whose descriptions are "
           "terse.", ""]
    if disputed:
        out += ["| Tool | Admitted because | Model's objection |", "| --- | --- | --- |"]
        for t, res in disputed:
            why = "hand-listed by ID" if t["id"] in curated else t.get("_select_reason", "")[:44]
            out.append(f"| [{cell(t['name'])}]({t['biotools_url'] or t['homepage']}) "
                       f"| {cell(why, 46)} | confidence {cell(res.get('confidence', '?'))}, "
                       f"categories {cell(', '.join(res.get('categories') or []) or 'none')} |")
        out.append("")

    DOCS.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(out))
    print(f"\n{len(disputed)}/{len(targets)} disputed  (${spend['total']:.3f}) -> {REPORT}")


if __name__ == "__main__":
    main()
