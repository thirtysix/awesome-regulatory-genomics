#!/usr/bin/env python3
"""Test the categories the LLM pass assigned, one (tool, category) pair at a time.

558 catalog rows display categories the categorise job proposed rather than the
ones `assign_categories()` derived from EDAM terms and text. Nothing had checked
them. A wrong category is not as costly as a wrong citation - it misfiles a tool
rather than crediting it with someone else's work - but it decides what a reader
browsing by category ever sees, and a tool filed nowhere useful is invisible.

BOTH DIRECTIONS ARE WRONG, SO BOTH ARE JUDGED
The pass removed categories as often as it added them: of the 558 rows, 174 were
removals only, 166 additions only and 218 a replacement. So this judges the
categories the catalog now SHOWS, and separately the rule-derived categories the
pass DISCARDED. Auditing only what is displayed would confirm the additions and
never notice a correct category quietly dropped.

GROUND TRUTH IS HAND-WRITTEN AND GENUINELY INDEPENDENT
curation/seeds.yaml carries 795 tools whose categories a human assigned, and the
categorise job never touches them - it runs only on bio.tools rows. So they were
not produced by the thing under test. Positives are (seed tool, its own
category); negatives pair a seed tool with a category it was not given.

That negative construction has a known weakness worth stating: a human list is
not exhaustive, so an unlisted category is occasionally still correct, and the
checker is right to say so. That shows up as a lower catch rate rather than as a
hidden error, which is the safe way for a flaw to appear.

REMEDY
A category judged wrong is removed. A discarded category judged correct is put
back. A row left with nothing falls back to the rule-derived set rather than
being published bare, and `unstable` keeps whatever the catalog already shows.

    python pipeline/audit_categories.py --calibrate
    python pipeline/audit_categories.py --apply
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from concurrent.futures import ThreadPoolExecutor

import yaml

from audit_descriptions import MAX_FALSE_POSITIVE, MIN_CATCH
from config import CATEGORIES, CATEGORY_DESC, CATEGORY_KEYS, CURATION, DATA, DOCS
from llm_assist import call, parse_json

PROPOSALS = CURATION / "llm_proposals.yaml"
SEEDS = CURATION / "seeds.yaml"
CATALOG = DATA / "catalog.json"
REPORT = DOCS / "category-audit.md"
VOTES = DATA / "cache" / "category_votes.json"

BULK = "deepseek-ai/DeepSeek-V4-Flash"
SECOND = "zai-org/GLM-5"
COST = [0.0]

JUDGE_SYSTEM = """You decide whether one category fits one bioinformatics tool.

You are given a tool's name and description, and a single category with its definition. Answer only about that category; other categories the tool might also belong to are irrelevant here.

Answer YES when the tool does the work the category names, or is a database serving it. A tool that does several things belongs to each category it covers, so do not answer NO merely because the category is not the tool's main purpose.

Answer NO when the tool does not do that work: the category describes a different analysis, or the connection is only shared vocabulary, or the tool merely consumes output from that kind of analysis.

Reply with JSON only:
{"fits": true, "confidence": "high|medium|low", "reason": "one short clause"}"""


def judge(model: str, name: str, description: str, key: str, api_key: str,
          operations: str = "") -> bool | None:
    prompt = "\n".join([
        f"Tool: {name}",
        f"Description: {(description or '')[:600]}",
        # The categorise job assigns from name + description + EDAM operations.
        # Judging on name + description alone rejects assignments using LESS
        # evidence than was used to make them, and it shows: Signac lost
        # peak-calling because its one-line description says only "extends
        # Seurat for analyzing single-cell chromatin data", though the tool
        # does call peaks. Give the judge what the assigner had.
        f"EDAM operations (registry annotations, often wrong): {operations or 'none'}",
        "",
        f"Category: {key}",
        f"Category means: {CATEGORY_DESC.get(key, key)}",
    ])
    try:
        text, cost, _ = call(model, JUDGE_SYSTEM, prompt, api_key, max_tokens=250)
    except Exception:                                            # noqa: BLE001
        return None
    COST[0] += cost
    res = parse_json(text)
    if not res or not isinstance(res.get("fits"), bool):
        return None
    return res["fits"]


def vote(name: str, description: str, key: str, samples: int, api_key: str,
         operations: str = "") -> dict:
    by_model = {}
    for model in (BULK, SECOND):
        by_model[model] = [v for v in
                           (judge(model, name, description, key, api_key, operations)
                            for _ in range(samples)) if v is not None]
    flat = [v for vs in by_model.values() for v in vs]
    if not flat:
        return {"n": 0, "fits": None, "unanimous_no": False, "family_no": False}
    n_no = sum(1 for v in flat if v is False)
    return {"n": len(flat), "n_no": n_no,
            "unanimous_no": n_no == len(flat),
            "unanimous_yes": n_no == 0,
            "family_no": any(vs and all(v is False for v in vs) for vs in by_model.values())}


def calibrate(args, api_key: str) -> bool:
    seeds = [s for s in (yaml.safe_load(SEEDS.read_text()) or {}).get("tools") or []
             if s.get("categories") and s.get("description")]
    if len(seeds) < args.fixtures:
        print(f"  only {len(seeds)} usable seeds"); return False
    rng = random.Random(args.seed)
    picked = rng.sample(seeds, args.fixtures)
    positives = [(s["name"], s["description"], rng.choice(s["categories"])) for s in picked]
    negatives = []
    for s in picked:
        spare = [k for k in CATEGORY_KEYS if k not in set(s["categories"])]
        negatives.append((s["name"], s["description"], rng.choice(spare)))
    print(f"calibrate: {len(positives)} hand-assigned pairs, {len(negatives)} unassigned "
          f"pairs, {args.runs} runs, {args.samples} samples x 2 models")
    catches, fps = [], []
    for run in range(args.runs):
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            pos = list(pool.map(lambda p: vote(*p, args.samples, api_key), positives))
            neg = list(pool.map(lambda p: vote(*p, args.samples, api_key), negatives))
        catch = sum(1 for v in neg if v["unanimous_no"]) / max(len(neg), 1)
        fp = sum(1 for v in pos if v["unanimous_no"]) / max(len(pos), 1)
        catches.append(catch); fps.append(fp)
        print(f"  run {run + 1}: rejects unassigned {catch:.0%}  "
              f"wrongly rejects hand-assigned {fp:.0%}")
    print(f"\n  catch {min(catches):.0%}-{max(catches):.0%}   "
          f"false-positive {min(fps):.0%}-{max(fps):.0%}")
    ok = min(catches) >= MIN_CATCH and max(fps) <= MAX_FALSE_POSITIVE
    print(f"  bar: catch >= {MIN_CATCH:.0%}, false-positive <= {MAX_FALSE_POSITIVE:.0%}"
          f"  -> {'PASS' if ok else 'FAIL'}")
    return ok


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--calibrate", action="store_true")
    ap.add_argument("--no-calibrate", action="store_true")
    ap.add_argument("--fixtures", type=int, default=25)
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--samples", type=int, default=3)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--seed", type=int, default=31)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    api_key = os.environ.get("DEEPINFRA_API_KEY") or os.environ.get("DEEPINFRA_TOKEN")
    if not api_key:
        sys.exit("DEEPINFRA_API_KEY is not set.")

    if not args.no_calibrate:
        if not calibrate(args, api_key):
            print(f"\nspend ${COST[0]:.4f}")
            sys.exit("\nRefusing to audit: the judge did not clear its own bar.")
        print()
    if args.calibrate:
        print(f"spend ${COST[0]:.4f}"); return

    blob = yaml.safe_load(PROPOSALS.read_text()) or {}
    props = blob.get("categories") or {}
    rows = {r["id"]: r for r in json.loads(CATALOG.read_text())["tools"]}
    targets = [k for k in props if k in rows
               and "categories" in (rows[k].get("_llm_applied") or [])]
    targets = targets[: args.limit] if args.limit else targets

    jobs = []
    for key in targets:
        row, entry = rows[key], props[key]
        shown = list(entry.get("categories") or [])
        dropped = [c for c in (entry.get("was") or []) if c not in shown]
        for cat in shown:
            jobs.append((key, cat, "shown"))
        for cat in dropped:
            jobs.append((key, cat, "dropped"))
    print(f"audit: {len(targets)} rows, {len(jobs)} (tool, category) pairs "
          f"({sum(1 for j in jobs if j[2] == 'shown')} shown, "
          f"{sum(1 for j in jobs if j[2] == 'dropped')} dropped by the pass)")

    # Votes are cached and flushed as they arrive. 8,580 calls do not fit in one
    # sitting: the first attempt was killed at 28 minutes and lost everything,
    # because results were only written at the end. A long pass must be
    # resumable, and the thing worth persisting is the evidence, not the verdict
    # - the decision rule has changed under every audit in this pipeline so far.
    cached = json.loads(VOTES.read_text()) if VOTES.exists() else {}
    def vkey(j):
        # v2 carries the EDAM operations now in the prompt. A cache key must
        # cover every input or a changed prompt silently returns the old answer.
        return f"v2|{j[0]}|{j[1]}|{args.samples}"
    todo = [j for j in jobs if vkey(j) not in cached]
    print(f"  {len(jobs) - len(todo)} already voted, {len(todo)} to call")
    CHUNK = 200
    for start in range(0, len(todo), CHUNK):
        batch = todo[start:start + CHUNK]
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            got = list(pool.map(
                lambda j: vote(rows[j[0]].get("name", ""),
                               rows[j[0]].get("description", ""), j[1],
                               args.samples, api_key,
                               ", ".join(rows[j[0]].get("_operations") or [])), batch))
        for j, v in zip(batch, got):
            cached[vkey(j)] = v
        VOTES.parent.mkdir(parents=True, exist_ok=True)
        VOTES.write_text(json.dumps(cached, indent=1, sort_keys=True))
        print(f"    {min(start + CHUNK, len(todo))}/{len(todo)} judged "
              f"(${COST[0]:.3f})", flush=True)
    results = [cached[vkey(j)] for j in jobs]

    fixes: dict[str, dict] = {}
    for (key, cat, kind), res in zip(jobs, results):
        if kind == "shown" and res["unanimous_no"]:
            fixes.setdefault(key, {"name": rows[key]["name"], "remove": [], "restore": []})
            fixes[key]["remove"].append(cat)
        elif kind == "dropped" and res.get("unanimous_yes"):
            fixes.setdefault(key, {"name": rows[key]["name"], "remove": [], "restore": []})
            fixes[key]["restore"].append(cat)
    n_rm = sum(len(v["remove"]) for v in fixes.values())
    n_rs = sum(len(v["restore"]) for v in fixes.values())
    print(f"  {n_rm} assigned categories rejected, {n_rs} discarded categories restored, "
          f"across {len(fixes)} rows")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    out = ["# Category audit", "",
           f"{len(targets)} rows display categories the LLM pass assigned; "
           f"{len(jobs)} (tool, category) pairs were judged.", "",
           f"- **{n_rm}** assigned categories every sample from both families rejected.",
           f"- **{n_rs}** categories the pass discarded that both families restore.",
           "- A row left with nothing falls back to the rule-derived set.", "",
           "| tool | removed | restored |", "| --- | --- | --- |"]
    for key, v in sorted(fixes.items(), key=lambda x: x[1]["name"].lower()):
        out.append(f"| {v['name']} | {', '.join(v['remove']) or '-'} | "
                   f"{', '.join(v['restore']) or '-'} |")
    REPORT.write_text("\n".join(out) + "\n")
    print(f"  -> {REPORT}")

    if args.apply:
        bare = 0
        for key, v in fixes.items():
            entry = props[key]
            now = [c for c in (entry.get("categories") or []) if c not in v["remove"]]
            now += [c for c in v["restore"] if c not in now]
            if not now:
                # Never publish a row with no category at all: the rule-derived
                # set is weaker evidence than a checked one, but it is evidence,
                # and an uncategorised row is reachable by no filter.
                now = list(entry.get("was") or [])
                bare += 1
            entry["categories"] = [c for c in CATEGORY_KEYS if c in set(now)]
            entry["audited"] = True
        blob["categories"] = props
        PROPOSALS.write_text(yaml.safe_dump(blob, sort_keys=False, width=100,
                                            allow_unicode=True))
        print(f"  written; {bare} rows fell back to the rule-derived set")
    print(f"\nspend ${COST[0]:.4f}")


if __name__ == "__main__":
    main()
