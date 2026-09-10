#!/usr/bin/env python3
"""Check LLM-written catalog descriptions against the inputs they were built from.

1,628 catalog rows display a description the describe stage rewrote rather than
the text bio.tools supplied. The failure that matters is a claim in the line
that appears in neither the registry description nor the tool's paper: it is
public, it reads authoritatively, and nothing on the page contradicts it.

WHY THIS CARRIES ITS OWN CALIBRATION
An LLM checker is a noisy instrument, and this repository has twice been misled
by treating one as a stable one. Measured 2026-09-07, the scope pass scored
21/20/18 on 26 fixtures across three identical runs, and called MACS out of
scope on one sample. So `--calibrate` is not a development convenience: it
builds ground truth by corrupting known-good descriptions in known ways, scores
catch rate on the mutants AND false-positive rate on untouched controls, repeats
the whole thing `--runs` times, and REFUSES to run the real audit unless the
instrument clears its bar. Neither rate means anything alone - a checker that
flags everything catches 100% of mutants and is useless.

Ground truth is built by corruption rather than by hand, because hand-labelling
descriptions is the same fallible judgement the checker is meant to replace:
label them by hand and the labels become the thing under test.

THE REMEDY SETS THE BAR, AND IT IS NOT THE SAME BAR AS A SCOPE DROP
A bad description reverts to the harvested registry text, which is always
available and always safe. So `unstable` resolves to REVERT here, where in
build.py's scope rule it resolves to KEEP. Reverting costs polish; keeping a
hallucination costs accuracy. Do not copy one rule to the other by analogy.

    python pipeline/audit_descriptions.py --calibrate       # prove the checker
    python pipeline/audit_descriptions.py                   # audit for real
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

import yaml

from config import CURATION, DATA, DOCS
from llm_assist import call, paper_context, parse_json, source_descriptions

PROPOSALS = CURATION / "llm_proposals.yaml"
CATALOG = DATA / "catalog.json"
REPORT = DOCS / "description-audit.md"
# Raw per-model votes, keyed by (id, candidate text). The decision RULE has
# already changed once - the first version reverted on a single dissenting
# sample - and re-deciding must not cost another 3,200 API calls. So what is
# stored is the evidence, not the verdict: cache the input to the decision, not
# the decision. Bump nothing when the rule changes; the votes stay valid.
VOTES = DATA / "cache" / "description_votes.json"

BULK = "deepseek-ai/DeepSeek-V4-Flash"
SECOND = "zai-org/GLM-5"

# Catch rate on mutants and false-positive rate on clean controls. A checker
# that misses half the planted faults cannot certify 400 real rows, and one that
# flags a fifth of clean text will bury the real findings.
MIN_CATCH = 0.70
MAX_FALSE_POSITIVE = 0.20

CHECK_SYSTEM = """You check whether a one-line tool description is supported by its sources.

You are given a tool's registry description, usually its paper title and abstract, and a candidate one-line description written from them.

Report any claim in the candidate that neither source supports. A claim is supported if the sources state it or plainly imply it; ordinary paraphrase, summary and reordering are supported. Synonyms and morphological variants are supported: "analyses" for "analysis", "identifies" for "detection".

These are NOT supported, and are what you are looking for:
- a capability, assay, data type or algorithm the sources never mention
- a different assay from the one the sources name
- a scope qualifier the sources do not carry, such as "genome-wide", "single-cell" or "multi-species"
- an organism the sources do not name
- a function belonging to some other tool

Judge only support, not style or quality. A description that is vague, or that drops detail the sources contain, is still SUPPORTED - losing detail is not the same as inventing it.

Reply with JSON only:
{"supported": true, "unsupported": ["the offending phrase, verbatim"], "confidence": "high|medium|low"}"""

# Longest first, so "ization" is not eaten by "ion". "is" and "es" are both
# here on purpose: analysis/analyses is the pair this exists for, and without
# both endings the two forms still look like different words.
SUFFIXES = tuple(sorted(
    ("ational", "isation", "ization", "ments", "ment", "tion", "sion", "ity",
     "ing", "ers", "er", "ors", "or", "al", "ic", "ly", "ed", "es", "is", "s"),
    key=len, reverse=True))


def stem(word: str) -> str:
    """Crude suffix stripping, enough to stop morphology looking like invention.

    Without it "analyses" against a source saying "analysis" reads as a novel
    word, and 989 of 1,628 rows flag on nothing but grammar.
    """
    for suffix in SUFFIXES:
        if len(word) > len(suffix) + 3 and word.endswith(suffix):
            return word[: -len(suffix)]
    return word


STOP = set("the a an of and or for to in on with from by using is are this that its it "
           "as at into be can which we our based than such also these those their between "
           "across within has have both each other more most many".split())


def content(text: str) -> set[str]:
    return {stem(w) for w in re.findall(r"[a-z0-9-]+", (text or "").lower())
            if w not in STOP and len(w) > 2}


def _related(word: str, pool: set[str]) -> bool:
    """Does `word` plausibly derive from something in `pool`?

    Stem equality is not enough. Single-pass suffix stripping leaves
    predicts -> predict against prediction -> predic, and identifies against
    identification, so the two forms still read as different words. Sharing a
    five-character prefix catches those without a real morphological analyser.

    Five, not four: at four "meth" ties "method" to "methylation", which is a
    real false negative in this domain. Five keeps predict/prediction,
    identifies/identification and visualises/visualisation together while
    holding those two apart. It is a heuristic and it will still miss a
    suppletive pair; the LLM check behind it is what catches those.
    """
    if word in pool:
        return True
    if len(word) < 5:
        return False
    head = word[:5]
    return any(p.startswith(head) or word.startswith(p[:5]) for p in pool if len(p) >= 5)


def untraceable(description: str, *sources: str) -> set[str]:
    legit: set[str] = set()
    for s in sources:
        legit |= content(s)
    return {w for w in content(description) if not _related(w, legit)}


# --- corruption, for building ground truth ---------------------------------
ASSAYS = ["ChIP-seq", "ATAC-seq", "Hi-C", "bisulfite sequencing", "CUT&RUN",
          "MPRA", "single-cell ATAC-seq", "DNase-seq"]
CAPABILITIES = [
    "and predicts three-dimensional chromatin loops",
    "and calls differentially methylated regions",
    "and performs motif enrichment against JASPAR",
    "and reconstructs gene regulatory networks",
]
QUALIFIERS = ["genome-wide", "single-cell", "multi-species", "pan-cancer"]


def mutate(description: str, kind: str, rng: random.Random,
           donors: list[str]) -> str | None:
    """Introduce one known, detectable fault. None when it does not apply."""
    if kind == "add_capability":
        return description + " " + rng.choice(CAPABILITIES)
    if kind == "swap_assay":
        for assay in ASSAYS:
            if assay.lower() in description.lower():
                other = rng.choice([a for a in ASSAYS if a != assay])
                return re.sub(re.escape(assay), other, description, count=1,
                              flags=re.I)
        return None
    if kind == "add_qualifier":
        words = description.split()
        if len(words) < 4:
            return None
        pos = rng.randrange(1, min(4, len(words)))
        return " ".join(words[:pos] + [rng.choice(QUALIFIERS)] + words[pos:])
    if kind == "swap_function":
        donor = rng.choice(donors)
        head = " ".join(donor.split()[:5])
        return head + " " + " ".join(description.split()[3:])
    return None


# --- the checker ------------------------------------------------------------
_lock = threading.Lock()
_spend = [0.0]


def check(model: str, name: str, source: str, paper: dict, candidate: str,
          api_key: str) -> dict | None:
    prompt = "\n".join([
        f"Tool: {name}",
        f"Registry description: {source[:1200] or '(none)'}",
        f"Paper title: {paper.get('title', '') or '(none)'}",
        f"Paper abstract: {(paper.get('abstract') or '')[:1800] or '(none)'}",
        "",
        f"Candidate description: {candidate}",
    ])
    try:
        text, cost, _ = call(model, CHECK_SYSTEM, prompt, api_key, max_tokens=300)
    except Exception:                                            # noqa: BLE001
        return None
    with _lock:
        _spend[0] += cost
    res = parse_json(text)
    if not res or not isinstance(res.get("supported"), bool):
        return None
    return res


def vote(models: list[str], samples: int, item: dict, api_key: str) -> dict:
    """All samples from all models. `flagged` only when every one agrees."""
    verdicts, phrases = [], []
    by_model: dict[str, list] = {m: [] for m in models}
    for model in models:
        for _ in range(samples):
            res = check(model, item["name"], item["source"], item["paper"],
                        item["candidate"], api_key)
            if res is None:
                continue
            verdicts.append(res["supported"])
            by_model[model].append(res["supported"])
            phrases += [p for p in (res.get("unsupported") or []) if isinstance(p, str)]
    if not verdicts:
        return {"flagged": False, "n": 0, "n_bad": 0, "family_unanimous": False,
                "phrases": [], "by_model": {}}
    n_bad = sum(1 for v in verdicts if v is False)
    # Unanimity WITHIN one model family is the signal worth acting on. A lone
    # dissenting sample is not: the first run of this reverted CausalR on 1 of
    # 6 votes, which is noise wearing the word "unstable". A family that says
    # unsupported three times out of three has actually made a claim.
    family_unanimous = any(
        v and all(x is False for x in v) for v in by_model.values())
    return {"flagged": n_bad == len(verdicts), "family_unanimous": family_unanimous,
            "n": len(verdicts), "n_bad": n_bad, "by_model": by_model,
            "phrases": [p for p, _ in Counter(phrases).most_common(3)]}


def load_votes() -> dict:
    if VOTES.exists():
        try:
            return json.loads(VOTES.read_text())
        except Exception:                                        # noqa: BLE001
            return {}
    return {}


def save_votes(votes: dict) -> None:
    VOTES.parent.mkdir(parents=True, exist_ok=True)
    VOTES.write_text(json.dumps(votes, indent=1, sort_keys=True))


def load_rows() -> list[dict]:
    props = (yaml.safe_load(PROPOSALS.read_text()) or {}).get("descriptions") or {}
    catalog = json.loads(CATALOG.read_text())["tools"]
    sources = source_descriptions()
    rows = []
    for row in catalog:
        key = row["id"]
        if "description" not in (row.get("_llm_applied") or []) or key not in props:
            continue
        source = sources.get(row.get("biotools_id"), "")
        rows.append({"id": key, "name": row.get("name", ""), "source": source,
                     "paper": paper_context(row),
                     "candidate": props[key]["description"]})
    return rows


def calibrate(rows: list[dict], args, api_key: str) -> bool:
    """Corrupt known-good descriptions, and score catch and false positives.

    Returns True when the checker clears its bar on every run.
    """
    rng = random.Random(args.seed)
    # Clean pool: rows whose every content word already traces to their inputs.
    # These are the safest available "known good", and they are also where a
    # false positive is least excusable.
    clean = [r for r in rows
             if not untraceable(r["candidate"], r["source"], r["paper"].get("title", ""),
                                r["paper"].get("abstract", ""), r["name"])]
    if len(clean) < args.fixtures * 2:
        print(f"  only {len(clean)} fully-traceable rows; need "
              f"{args.fixtures * 2}. Lower --fixtures.")
        return False
    picked = rng.sample(clean, args.fixtures * 2)
    controls, to_mutate = picked[: args.fixtures], picked[args.fixtures:]
    donors = [r["candidate"] for r in rng.sample(clean, min(40, len(clean)))]

    kinds = ["add_capability", "swap_assay", "add_qualifier", "swap_function"]
    mutants = []
    for row in to_mutate:
        rng.shuffle(kinds)
        for kind in kinds:
            bad = mutate(row["candidate"], kind, rng, donors)
            if bad and bad != row["candidate"]:
                mutants.append({**row, "candidate": bad, "_kind": kind})
                break
    print(f"calibrate: {len(controls)} clean controls, {len(mutants)} mutants, "
          f"{args.runs} runs, {args.samples} samples x {len(args.models)} models")

    catches, fps = [], []
    for run in range(args.runs):
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            mres = list(pool.map(lambda r: vote(args.models, args.samples, r, api_key), mutants))
            cres = list(pool.map(lambda r: vote(args.models, args.samples, r, api_key), controls))
        catch = sum(1 for v in mres if v["flagged"]) / max(len(mres), 1)
        fp = sum(1 for v in cres if v["flagged"]) / max(len(cres), 1)
        catches.append(catch)
        fps.append(fp)
        print(f"  run {run + 1}: catch {catch:.0%}  false-positive {fp:.0%}")
        if run == args.runs - 1:
            by_kind = Counter(m["_kind"] for m, v in zip(mutants, mres) if not v["flagged"])
            if by_kind:
                print(f"    missed by fault type: {dict(by_kind)}")

    spread_c = max(catches) - min(catches)
    spread_f = max(fps) - min(fps)
    print(f"\n  catch {min(catches):.0%}-{max(catches):.0%} (spread {spread_c:.0%})   "
          f"false-positive {min(fps):.0%}-{max(fps):.0%} (spread {spread_f:.0%})")
    ok = min(catches) >= MIN_CATCH and max(fps) <= MAX_FALSE_POSITIVE
    print(f"  bar: catch >= {MIN_CATCH:.0%} and false-positive <= {MAX_FALSE_POSITIVE:.0%}"
          f"  -> {'PASS' if ok else 'FAIL'}")
    return ok


def audit(rows: list[dict], args, api_key: str) -> dict:
    """Judge the rewrites the cheap filter could not clear."""
    suspects = []
    for row in rows:
        novel = untraceable(row["candidate"], row["source"], row["paper"].get("title", ""),
                            row["paper"].get("abstract", ""), row["name"])
        if len(novel) >= args.min_novel:
            suspects.append({**row, "_novel": sorted(novel)})
    print(f"audit: {len(suspects)} of {len(rows)} rows carry >= {args.min_novel} "
          f"untraceable words; judging those")
    cached = load_votes()
    def cache_key(r):
        return f"{r['id']}|{args.samples}|{hash(r['candidate']) & 0xffffffff}"
    todo = [r for r in suspects if cache_key(r) not in cached or args.refresh]
    print(f"  {len(suspects) - len(todo)} already voted, {len(todo)} to call")
    if todo:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            fresh = list(pool.map(lambda r: vote(args.models, args.samples, r, api_key), todo))
        for r, v in zip(todo, fresh):
            cached[cache_key(r)] = v
        save_votes(cached)
    results = [cached[cache_key(r)] for r in suspects]
    revert = {}
    unstable = 0
    for row, res in zip(suspects, results):
        # Unstable resolves to REVERT here. The harvested text is always
        # available, so the cost of reverting is polish and the cost of keeping
        # a hallucination is accuracy. build.py's scope rule resolves the other
        # way for the opposite reason: there, the discarded thing is gone.
        if res["flagged"] or res["family_unanimous"]:
            if not res["flagged"]:
                unstable += 1
            revert[row["id"]] = {"name": row["name"], "was": row["candidate"],
                                 "unsupported": res["phrases"],
                                 "votes": f"{res.get('n_bad', 0)}/{res['n']}",
                                 "both_families": bool(res["flagged"])}
    print(f"  {len(revert)} to revert ({len(revert) - unstable} unanimous across both "
          f"families, {unstable} unanimous within one)")
    return revert


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--calibrate", action="store_true",
                    help="only prove the checker; do not audit or write anything")
    ap.add_argument("--no-calibrate", action="store_true",
                    help="skip the gate. The audit then rests on an instrument "
                         "nobody measured; there is no good reason to pass this")
    ap.add_argument("--fixtures", type=int, default=25, help="controls, and mutants, per run")
    ap.add_argument("--runs", type=int, default=3, help="repeats of the whole calibration")
    ap.add_argument("--samples", type=int, default=3, help="verdicts per model per item")
    ap.add_argument("--min-novel", type=int, default=3,
                    help="untraceable content words before a row is worth judging")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--seed", type=int, default=17)
    ap.add_argument("--refresh", action="store_true", help="ignore cached votes")
    ap.add_argument("--apply", action="store_true", help="write the reverts to the overlay")
    args = ap.parse_args()
    args.models = [BULK, SECOND]

    api_key = os.environ.get("DEEPINFRA_API_KEY") or os.environ.get("DEEPINFRA_TOKEN")
    if not api_key:
        sys.exit("DEEPINFRA_API_KEY is not set.")

    rows = load_rows()
    print(f"{len(rows)} catalog rows display a rewritten description\n")

    if not args.no_calibrate:
        if not calibrate(rows, args, api_key):
            print(f"\nspend ${_spend[0]:.4f}")
            sys.exit("\nRefusing to audit: the checker did not clear its own bar. "
                     "A pass that cannot find planted faults, or that flags clean "
                     "text, cannot certify the real rows either.")
        print()
    if args.calibrate:
        print(f"spend ${_spend[0]:.4f}")
        return

    revert = audit(rows, args, api_key)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Description audit", "",
             f"{len(rows)} rows display a rewritten description; "
             f"{len(revert)} revert to the harvested registry text.", "",
             "| tool | unsupported | votes | reverted line |", "| --- | --- | --- | --- |"]
    for key, entry in sorted(revert.items(), key=lambda x: x[1]["name"].lower()):
        phrases = "; ".join(entry["unsupported"])[:70] or "unstable"
        lines.append(f"| {entry['name']} | {phrases} | {entry['votes']} | {entry['was'][:70]} |")
    REPORT.write_text("\n".join(lines) + "\n")
    print(f"  -> {REPORT}")

    if args.apply:
        blob = yaml.safe_load(PROPOSALS.read_text()) or {}
        props = blob.get("descriptions") or {}
        for key in revert:
            props.pop(key, None)
        blob["descriptions"] = props
        blob["description_reverted"] = revert
        PROPOSALS.write_text(yaml.safe_dump(blob, sort_keys=False, width=100,
                                            allow_unicode=True))
        print(f"  removed {len(revert)} rewrites; rows fall back to the harvested text")
    print(f"\nspend ${_spend[0]:.4f}")


if __name__ == "__main__":
    main()
