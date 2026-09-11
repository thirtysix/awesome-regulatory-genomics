#!/usr/bin/env python3
"""Decide whether a flagged record really is carrying the wrong paper.

The describe stage records `paper_mismatch` as a free side-observation: while
reading a tool's description and its paper it says whether the two look like
the same thing. 61 records were flagged that way and nothing ever acted on
them, which was right, because that flag is ONE sample from ONE model and this
repository has been burned by exactly that.

A wrong paper is not cosmetic. The citation count follows the link, so a
mis-attached paper inflates the catalog's headline ordering: vulcan once
carried VIPER's 1,079 citations, and MoonlightR a spine-surgery review.

WHAT THIS DOES THAT --recheck-flagged DOES NOT
`discover_pubs.py --recheck-flagged` asks each tool what to cite and writes a
report for a human. It resolves 8 of 61; for the rest the tool declares
nothing. Worse, a declared citation is evidence and not truth: PINTS is a 2022
tool whose page declares a 2016 Nature Protocols paper, and applying that
blindly would replace a right answer with a wrong one. So both directions are
checked here - is the RECORDED paper this tool's, and if not, is the DECLARED
candidate any better - and neither is believed on one sample.

GROUND TRUTH IS REAL HERE, NOT SYNTHETIC
`overlay.yaml: verified_publications` holds 38 tool/paper pairs a human
checked. Those are the positive controls. Negatives are built by cross-pairing
them - give one tool another's paper - which is a known-wrong pair by
construction. Catch rate on the cross-pairs and false-positive rate on the
verified pairs; the audit refuses to run unless both clear their bar.

THE REMEDY, AND WHY IT POINTS THIS WAY
A confirmed-wrong paper with no better candidate has its publication and
citation count removed. An absent citation count is a gap; a wrong one is a
false claim that actively reorders the catalog. So `unstable` resolves to
KEEPING the existing link here - removing a real paper loses verifiable data -
while a CONFIRMED mismatch is removed even with nothing to replace it.

    python pipeline/audit_publications.py --calibrate
    python pipeline/audit_publications.py --apply
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

import yaml

from audit_descriptions import MAX_FALSE_POSITIVE, MIN_CATCH, load_votes, save_votes
from config import CURATION, DATA, DOCS
from llm_assist import call, paper_context, parse_json

PROPOSALS = CURATION / "llm_proposals.yaml"
OVERLAY = CURATION / "overlay.yaml"
CATALOG = DATA / "catalog.json"
REPORT = DOCS / "publication-audit.md"
VOTES = DATA / "cache" / "publication_votes.json"

BULK = "deepseek-ai/DeepSeek-V4-Flash"
SECOND = "zai-org/GLM-5"

JUDGE_SYSTEM = """You decide whether a scientific paper is the paper that introduces or describes a given software tool.

You are given the tool's name and description, and a paper's title and abstract.

Answer YES when the paper announces the tool, describes it as its subject, or is a release or version paper for it. A paper that introduces the tool under a different name, or as part of a named suite, is still YES. A later release paper from the same project is YES.

Answer NO when the paper is about something else: a different tool, a protocol or assay the tool merely supports, a biological study that used the tool, a review, or a paper from the same lab about a different piece of software. A paper that only CITES or USES the tool is NO - the question is whether the paper is ABOUT the tool.

If the abstract is missing, judge on the title alone and say so by lowering confidence.

Reply with JSON only:
{"is_the_tools_paper": true, "confidence": "high|medium|low", "reason": "one short clause"}"""


def judge(model: str, tool: dict, paper: dict, api_key: str) -> bool | None:
    prompt = "\n".join([
        f"Tool: {tool['name']}",
        f"Tool description: {(tool.get('description') or '')[:600]}",
        "",
        f"Paper title: {paper.get('title') or '(none)'}",
        f"Paper abstract: {(paper.get('abstract') or '')[:1600] or '(none)'}",
    ])
    try:
        text, cost, _ = call(model, JUDGE_SYSTEM, prompt, api_key, max_tokens=280)
    except Exception:                                            # noqa: BLE001
        return None
    COST[0] += cost
    res = parse_json(text)
    if not res or not isinstance(res.get("is_the_tools_paper"), bool):
        return None
    return res["is_the_tools_paper"]


COST = [0.0]


def vote(tool: dict, paper: dict, samples: int, api_key: str) -> dict:
    by_model = {}
    for model in (BULK, SECOND):
        by_model[model] = [v for v in
                           (judge(model, tool, paper, api_key) for _ in range(samples))
                           if v is not None]
    flat = [v for vs in by_model.values() for v in vs]
    if not flat:
        return {"n": 0, "mismatch": False, "family_unanimous": False}
    n_no = sum(1 for v in flat if v is False)
    return {"n": len(flat), "n_no": n_no,
            "mismatch": n_no == len(flat),
            "family_unanimous": any(vs and all(v is False for v in vs)
                                    for vs in by_model.values())}


def load_catalog() -> dict:
    return {r["id"]: r for r in json.loads(CATALOG.read_text())["tools"]}


def calibrate(rows: dict, args, api_key: str) -> bool:
    """Positive controls are human-verified pairs; negatives are cross-pairings."""
    overlay = yaml.safe_load(OVERLAY.read_text()) or {}
    verified = [k for k in (overlay.get("verified_publications") or {}) if k in rows]
    usable = [k for k in verified if paper_context(rows[k]).get("title")]
    if len(usable) < 8:
        print(f"  only {len(usable)} verified pairs have a resolvable paper; "
              f"cannot calibrate")
        return False
    rng = random.Random(args.seed)
    n = min(args.fixtures, len(usable))
    controls = rng.sample(usable, n)
    # A cross-pairing is wrong by construction: this tool, that tool's paper.
    shuffled = controls[:]
    while True:
        rng.shuffle(shuffled)
        if all(a != b for a, b in zip(controls, shuffled)):
            break
    print(f"calibrate: {n} verified pairs, {n} cross-pairings, {args.runs} runs, "
          f"{args.samples} samples x 2 models")
    catches, fps = [], []
    for run in range(args.runs):
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            good = list(pool.map(
                lambda k: vote(rows[k], paper_context(rows[k]), args.samples, api_key),
                controls))
            bad = list(pool.map(
                lambda ab: vote(rows[ab[0]], paper_context(rows[ab[1]]), args.samples,
                                api_key),
                list(zip(controls, shuffled))))
        catch = sum(1 for v in bad if v["mismatch"]) / max(len(bad), 1)
        fp = sum(1 for v in good if v["mismatch"]) / max(len(good), 1)
        catches.append(catch); fps.append(fp)
        print(f"  run {run + 1}: catch {catch:.0%}  false-positive {fp:.0%}")
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
    ap.add_argument("--fixtures", type=int, default=16)
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--samples", type=int, default=3)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--seed", type=int, default=23)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    api_key = os.environ.get("DEEPINFRA_API_KEY") or os.environ.get("DEEPINFRA_TOKEN")
    if not api_key:
        sys.exit("DEEPINFRA_API_KEY is not set.")

    rows = load_catalog()
    flagged = list((yaml.safe_load(PROPOSALS.read_text()) or {}).get("paper_mismatch") or {})
    flagged = [k for k in flagged if k in rows]
    print(f"{len(flagged)} records flagged as carrying an unrelated paper\n")

    if not args.no_calibrate:
        if not calibrate(rows, args, api_key):
            print(f"\nspend ${COST[0]:.4f}")
            sys.exit("\nRefusing to audit: the judge did not clear its own bar.")
        print()
    if args.calibrate:
        print(f"spend ${COST[0]:.4f}")
        return

    judged, no_paper = [], []
    for key in flagged:
        paper = paper_context(rows[key])
        (judged if paper.get("title") else no_paper).append(key)
    print(f"audit: {len(judged)} have a resolvable paper to judge; "
          f"{len(no_paper)} have none and the flag cannot be tested")
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        results = list(pool.map(
            lambda k: vote(rows[k], paper_context(rows[k]), args.samples, api_key), judged))

    confirmed, cleared, unstable = {}, [], 0
    for key, res in zip(judged, results):
        if res["mismatch"]:
            confirmed[key] = {"name": rows[key]["name"],
                              "publication": rows[key].get("publication") or "",
                              "paper": paper_context(rows[key]).get("title", ""),
                              "citations": rows[key].get("citations") or 0,
                              "votes": f"{res.get('n_no', 0)}/{res['n']}"}
        elif res["family_unanimous"]:
            unstable += 1
        else:
            cleared.append(key)
    print(f"  {len(confirmed)} confirmed wrong, {len(cleared)} the flag was wrong about, "
          f"{unstable} split")
    lost = sum(v["citations"] for v in confirmed.values())
    print(f"  removing them takes {lost} citations off the catalog")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    out = ["# Publication audit", "",
           f"{len(flagged)} records were flagged by the describe stage as carrying a paper",
           f"that is not theirs. {len(judged)} had a resolvable paper to test the flag against.",
           "", f"- **{len(confirmed)}** confirmed: every sample from both model families says",
           "  the paper is not about the tool. The link and its citation count are removed.",
           f"- **{len(cleared)}** cleared: the flag was wrong and the paper stands.",
           f"- **{unstable}** split: one family only. The link stands - removing a real paper",
           "  loses verifiable data, so an unproven flag does not get to act.",
           f"- **{len(no_paper)}** unresolvable: no paper text exists to test against.",
           "", "| tool | recorded | paper title | votes | citations lost |",
           "| --- | --- | --- | --- | --- |"]
    for key, v in sorted(confirmed.items(), key=lambda x: -x[1]["citations"]):
        out.append(f"| {v['name']} | {v['publication']} | {v['paper'][:56]} | "
                   f"{v['votes']} | {v['citations']} |")
    REPORT.write_text("\n".join(out) + "\n")
    print(f"  -> {REPORT}")

    if args.apply:
        overlay = yaml.safe_load(OVERLAY.read_text()) or {}
        na = overlay.setdefault("no_article", {})
        pubs = overlay.setdefault("publications", {})
        for key, v in confirmed.items():
            # Empty override retracts the link AND the count; no_article then
            # supplies the note explaining why the row shows no citations.
            pubs[key] = ""
            na[key] = (f"paper audit {v['votes']}: recorded {v['publication']} is not "
                       f"this tool's paper")
        OVERLAY.write_text(yaml.safe_dump(overlay, sort_keys=False, width=100,
                                          allow_unicode=True))
        blob = yaml.safe_load(PROPOSALS.read_text()) or {}
        pm = blob.get("paper_mismatch") or {}
        for key in cleared:
            pm.pop(key, None)
        blob["paper_mismatch"] = pm
        PROPOSALS.write_text(yaml.safe_dump(blob, sort_keys=False, width=100,
                                            allow_unicode=True))
        print(f"  {len(confirmed)} added to overlay no_article; "
              f"{len(cleared)} cleared flags dropped")
    print(f"\nspend ${COST[0]:.4f}")


if __name__ == "__main__":
    main()
