#!/usr/bin/env python3
"""Benchmark candidate models on THIS task before picking one.

A general intelligence ranking does not predict performance on a narrow
structured-classification task, and the cheapest model has a documented habit
of blanking enum fields. Both facts make measurement cheaper than assumption -
the whole benchmark costs a few cents.

What it measures, on a fixed sample drawn from the built catalog:

  json_ok        fraction of calls returning parseable JSON
  enum_ok        fraction returning ONLY valid taxonomy keys (the known failure
                 mode: an empty or invented enum silently mis-files a tool)
  agreement      Jaccard overlap with the rule-derived categories - a sanity
                 signal, not ground truth; the rules are what we hope to beat
  gold_f1        F1 against hand-labelled tools, where we do have ground truth:
                 the featured entries and curated seeds
  cost / latency per 100 tools, extrapolated

    export DEEPINFRA_API_KEY=...
    python pipeline/bench_models.py --n 40
    python pipeline/bench_models.py --n 40 --models deepseek-ai/DeepSeek-V4-Flash,zai-org/GLM-5
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import sys
from datetime import date

import yaml

from config import CATEGORY_KEYS, CURATION, DATA, DOCS
from llm_assist import CATEGORISE_SYSTEM, call, parse_json, tool_prompt

CATALOG = DATA / "catalog.json"
SEEDS = CURATION / "seeds.yaml"
REPORT = DOCS / "model-benchmark.md"

CANDIDATES = [
    "deepseek-ai/DeepSeek-V4-Flash",        # bulk tier: cheapest by far
    "deepseek-ai/DeepSeek-V3.1-Terminus",   # quality tier: best instruction-following
    "zai-org/GLM-5",                        # smarter on general benchmarks
]


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b) if (a | b) else 0.0


def prf(pred: set, gold: set) -> tuple[float, float, float]:
    if not pred and not gold:
        return 1.0, 1.0, 1.0
    tp = len(pred & gold)
    p = tp / len(pred) if pred else 0.0
    r = tp / len(gold) if gold else 0.0
    f = 2 * p * r / (p + r) if (p + r) else 0.0
    return p, r, f


def build_sample(n: int) -> tuple[list[dict], dict[str, set]]:
    """A stratified sample, plus hand-labelled gold where it exists.

    Gold comes from curated seeds (categories written by hand) and featured
    entries. Everything else is scored against the rules only, as agreement.
    """
    tools = json.loads(CATALOG.read_text())["tools"]
    seeds = yaml.safe_load(SEEDS.read_text()) or {}
    gold = {s["name"]: set(s.get("categories") or [])
            for s in seeds.get("tools") or [] if s.get("categories")}

    by_name = {t["name"]: t for t in tools}
    # Cap the hand-labelled share. Seeds are the entries whose descriptions and
    # categories were written by hand, so they are unrepresentatively clean; let
    # them dominate the sample and the benchmark measures agreement with its own
    # author on easy records rather than performance on the catalog.
    gold_quota = max(1, n // 3)
    gold_tools = [by_name[k] for k in gold if k in by_name][:gold_quota]

    biotools = [t for t in tools if t["source"] == "bio.tools"]
    # Spread across the catalog rather than taking the head, which is all
    # highly-cited suites and far easier than the average record.
    uncategorised = [t for t in biotools if not t["categories"]][:5]
    remaining = max(n - len(gold_tools) - len(uncategorised), 1)
    step = max(1, len(biotools) // remaining)
    spread = biotools[::step]

    sample, seen = [], set()
    for t in gold_tools + uncategorised + spread:
        if t["id"] not in seen:
            seen.add(t["id"])
            sample.append(t)
        if len(sample) >= n:
            break
    return sample, {t["name"]: gold[t["name"]] for t in sample if t["name"] in gold}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=40, help="tools to sample")
    ap.add_argument("--models", default=",".join(CANDIDATES))
    args = ap.parse_args()

    api_key = os.environ.get("DEEPINFRA_API_KEY") or os.environ.get("DEEPINFRA_TOKEN")
    if not api_key:
        sys.exit("DEEPINFRA_API_KEY is not set.")

    models = [m.strip() for m in args.models.split(",") if m.strip()]
    sample, gold = build_sample(args.n)
    valid = set(CATEGORY_KEYS)
    print(f"benchmarking {len(models)} models on {len(sample)} tools "
          f"({len(gold)} with hand-labelled categories)\n")

    results = {}
    for model in models:
        json_ok = enum_ok = 0
        agreements, f1s, costs, times, failures = [], [], [], [], []
        print(f"== {model}")
        for i, t in enumerate(sample, 1):
            try:
                text, cost, secs = call(model, CATEGORISE_SYSTEM, tool_prompt(t), api_key)
            except Exception as exc:                      # noqa: BLE001 - report, don't abort
                failures.append(f"{t['name']}: {type(exc).__name__}")
                continue
            costs.append(cost)
            times.append(secs)
            parsed = parse_json(text)
            if not parsed:
                failures.append(f"{t['name']}: unparseable {text[:60]!r}")
                continue
            json_ok += 1
            cats = parsed.get("categories")
            if not isinstance(cats, list) or any(c not in valid for c in cats):
                failures.append(f"{t['name']}: bad enum {cats!r}")
                continue
            enum_ok += 1
            pred = set(cats)
            agreements.append(jaccard(pred, set(t["categories"])))
            if t["name"] in gold:
                f1s.append(prf(pred, gold[t["name"]])[2])
            if i % 10 == 0:
                print(f"   {i}/{len(sample)}", flush=True)

        n = len(sample)
        results[model] = {
            "json_ok": json_ok / n, "enum_ok": enum_ok / n,
            "agreement": statistics.mean(agreements) if agreements else 0.0,
            "gold_f1": statistics.mean(f1s) if f1s else None,
            "cost_per_100": sum(costs) / max(len(costs), 1) * 100,
            "median_latency": statistics.median(times) if times else 0.0,
            "failures": failures[:10], "n_failures": len(failures),
        }
        r = results[model]
        print(f"   json_ok {r['json_ok']:.0%}  enum_ok {r['enum_ok']:.0%}  "
              f"agreement {r['agreement']:.2f}  "
              f"gold_F1 {r['gold_f1']:.2f}" if r["gold_f1"] is not None else "")
        print(f"   ${r['cost_per_100']:.3f}/100 tools  {r['median_latency']:.1f}s median\n")

    out = ["# Model benchmark", "",
           f"Generated {date.today().isoformat()} by `pipeline/bench_models.py` on "
           f"{len(sample)} sampled tools ({len(gold)} hand-labelled).", "",
           "A general intelligence ranking does not predict performance on a narrow "
           "structured-classification task, so the model is chosen by measurement. "
           "`agreement` is Jaccard overlap with the rule-derived categories: a sanity "
           "signal, not ground truth, since beating the rules is the point. `gold_F1` "
           "is scored against hand-labelled tools and is the number that matters.", "",
           "| Model | JSON ok | Enum ok | Agreement | Gold F1 | $/100 tools | Median latency |",
           "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for model, r in results.items():
        f1 = f"{r['gold_f1']:.2f}" if r["gold_f1"] is not None else "n/a"
        out.append(f"| `{model}` | {r['json_ok']:.0%} | {r['enum_ok']:.0%} | "
                   f"{r['agreement']:.2f} | {f1} | ${r['cost_per_100']:.3f} | "
                   f"{r['median_latency']:.1f}s |")
    out += ["", f"Full catalog is {json.loads(CATALOG.read_text())['meta']['count']} tools, "
                "so multiply the per-100 cost by roughly 17 for a full pass.", ""]
    for model, r in results.items():
        if r["failures"]:
            out += [f"### Failures in `{model}` ({r['n_failures']})", ""]
            out += [f"- {f}" for f in r["failures"]]
            out.append("")

    DOCS.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(out))
    print(f"-> {REPORT}")


if __name__ == "__main__":
    main()
