#!/usr/bin/env python3
"""Stage 2j - decide which discovered candidates are tools worth adding.

`discover_literature.py` and `discover_registries.py` find candidates without
going near bio.tools. That matters twice over: it grows the catalog independently
of a single upstream, and it is the only discovery work that still functions when
that upstream is down.

The two channels fail differently, so both questions are asked explicitly:

* **Literature.** Europe PMC returns papers, and a paper is not a tool. The top
  hit by citations is ChIPmentation, a wet-lab protocol; ChIP-chip is an assay.
  Both are named like software and neither is software.
* **Registry.** Bioconductor and Galaxy entries are definitely software, so only
  scope is in question.

Two models must agree before anything is proposed, and the run aborts unless
four controls classify correctly first. Output is a review file; nothing is
promoted automatically. Promotion means hand-editing `curation/seeds.yaml`.

    export DEEPINFRA_API_KEY=...
    python pipeline/adjudicate_candidates.py [--limit N] [--refresh]
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DATA, RAW
import llm_assist as L

DOCS = DATA.parent / "docs"
CACHE = DATA / "cache" / "candidate_adjudication.json"
REPORT = DOCS / "candidate-review.md"

SYSTEM = """You decide whether a discovered candidate belongs in a catalog of regulatory-genomics \
SOFTWARE.

Two separate questions, both must be yes.

**1. Is it software?** A tool, package, database, web server or pipeline that someone can run or \
query. NOT a wet-lab protocol, an assay, an experimental technique, a data resource with no \
interface, a consortium, or a review. This is the question that matters most for candidates found \
in the literature, where the name of a method and the name of a program look identical: \
"ChIPmentation" is a library-preparation protocol and "ChIP-chip" is an assay, and neither is \
software however often they are named like it.

**2. Is it in scope?** IN: transcription-factor binding and motifs; promoters, enhancers and \
cis-regulatory elements; DNase/ATAC footprinting; ChIP-seq/ATAC-seq peak calling and annotation; \
chromatin accessibility and nucleosomes; gene-regulatory networks; regulatory variant effect; DNA \
methylation; the 3D genome; histone modifications; reporter assays; molecular QTL; and databases \
serving those.

OUT: general alignment and assembly; RNA secondary structure; protein structure, folding and \
docking; mass spectrometry; proteomics; metabolomics; phylogenetics; generic differential \
expression; single-cell methods with no regulatory component; RNA modification (m6A, m5C, m6Am, \
pseudouridine); protein post-translational modification. Sharing vocabulary is not enough: \
"motif", "peak", "binding" and "regulatory" all appear in out-of-scope work.

confidence "high" only when the text plainly settles both questions.

Reply with JSON only:
{"is_software": true, "in_scope": true, "confidence": "high|medium|low", "reason": "one short clause"}"""


def prompt(c: dict) -> str:
    lines = [f"Name: {c.get('name')}"]
    if c.get("title"):
        lines.append(f"Paper or package title: {c['title']}")
    if c.get("description"):
        lines.append(f"Description: {str(c['description'])[:700]}")
    if c.get("journal"):
        lines.append(f"Journal: {c['journal']} ({c.get('year','?')})")
    if c.get("homepage"):
        lines.append(f"Homepage: {c['homepage']}")
    lines.append(f"Found via: {c.get('source')}")
    return "\n".join(lines)


def ask(c, model, api_key, cache, refresh):
    key = f"cand:{model}:{L.digest(str(c.get('name')), str(c.get('title') or c.get('description'))[:200])}"
    if key in cache and not refresh:
        return cache[key]
    try:
        text, cost, _ = L.call(model, SYSTEM, prompt(c), api_key)
    except Exception:                                        # noqa: BLE001
        return None
    res = L.parse_json(text)
    if not (res and isinstance(res.get("is_software"), bool)
            and isinstance(res.get("in_scope"), bool)):
        return None
    res["_cost"] = cost
    cache[key] = res
    return res


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--model", default=L.BULK_MODEL)
    args = ap.parse_args()

    api_key = os.environ.get("DEEPINFRA_API_KEY", "").strip()
    if not api_key:
        sys.exit("DEEPINFRA_API_KEY is not set")
    second = L.QUALITY_MODEL

    # `known` is only true as of the moment the candidates file was written, and
    # these files are days old. The 2026-07-28 run reported PlantPAN3.0, oPOSSUM-3
    # and TRED as new, correctly: they were added by the very commit that wrote
    # the file. Reading the stored boolean five days later presented eight
    # already-catalogued tools as gaps. Re-check against the live catalog.
    from build import norm_name
    catalog = json.loads((DATA / "catalog.json").read_text())["tools"]
    have = {norm_name(t["name"]) for t in catalog}
    have |= {norm_name(t["biotools_id"]) for t in catalog if t.get("biotools_id")}
    cands, stale = [], 0
    for f in ("literature_candidates.json", "registry_candidates.json"):
        p = RAW / f
        if not p.exists():
            continue
        for c in json.loads(p.read_text())["list"]:
            if norm_name(c.get("name") or "") in have:
                stale += not c.get("known")
                continue
            cands.append(c)
    if stale:
        print(f"  {stale} candidate(s) flagged new in the file are now in the catalog; skipped")
    cache = json.loads(CACHE.read_text()) if CACHE.exists() and not args.refresh else {}

    # A sweep whose control case fails measures nothing. Two that must pass both
    # questions, one that is software but out of scope, and one that is in the
    # domain but is not software at all.
    controls = [
        ({"name": "MACS", "description": "Model-based analysis of ChIP-seq data, calls peaks",
          "source": "control"}, True, True),
        ({"name": "JASPAR", "description": "Open-access database of curated transcription factor "
          "binding profiles", "source": "control"}, True, True),
        ({"name": "AlphaFold", "description": "Predicts three-dimensional protein structure from "
          "sequence", "source": "control"}, True, False),
        ({"name": "ChIPmentation", "description": "Fast, robust, low-input ChIP-seq for histones "
          "and transcription factors. A library preparation protocol combining ChIP with Tn5 "
          "tagmentation.", "source": "control"}, False, None),
    ]
    print("controls:")
    for c, want_sw, want_scope in controls:
        r = ask(c, args.model, api_key, cache, True)
        ok = r and r["is_software"] == want_sw and (want_scope is None or r["in_scope"] == want_scope)
        print(f"  {c['name']:<14} software={r and r['is_software']!s:<6} "
              f"in_scope={r and r['in_scope']!s:<6} {'ok' if ok else 'FAILED'}")
        if not ok:
            sys.exit("  a control failed; aborting rather than reporting a rate")

    if args.limit:
        cands = cands[: args.limit]
    print(f"\nadjudicating {len(cands)} candidates via {args.model}, "
          f"confirming accepts with {second}")
    spend = 0.0
    rows = []
    for i, c in enumerate(cands, 1):
        first = ask(c, args.model, api_key, cache, args.refresh)
        spend += (first or {}).get("_cost", 0)
        if not first:
            continue
        verdict = dict(first)
        # Only an ACCEPT needs a second opinion. A rejection costs nothing to be
        # wrong about here, because the candidate simply stays unpromoted.
        if first["is_software"] and first["in_scope"]:
            conf = ask(c, second, api_key, cache, args.refresh)
            spend += (conf or {}).get("_cost", 0)
            agreed = bool(conf and conf["is_software"] and conf["in_scope"])
            verdict["agreed"] = agreed
        else:
            verdict["agreed"] = False
        rows.append(dict(name=c.get("name"), source=c.get("source"),
                         title=c.get("title") or "", desc=str(c.get("description") or "")[:150],
                         homepage=c.get("homepage") or c.get("url") or "",
                         citations=c.get("citations"), year=c.get("year"), **verdict))
        if i % 50 == 0:
            print(f"  {i}/{len(cands)}  ${spend:.3f}", flush=True)
            CACHE.parent.mkdir(parents=True, exist_ok=True)
            CACHE.write_text(json.dumps(cache, indent=1))
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, indent=1))

    accept = [r for r in rows if r.get("agreed")]
    notsw = [r for r in rows if not r["is_software"]]
    oos = [r for r in rows if r["is_software"] and not r["in_scope"]]
    split = [r for r in rows if r["is_software"] and r["in_scope"] and not r.get("agreed")]

    out = ["# Discovered candidates, adjudicated", "",
           "GENERATED by `pipeline/adjudicate_candidates.py`. Nothing is promoted.",
           "Promote a row by hand into `curation/seeds.yaml`.", "",
           "Candidates come from `discover_literature.py` (Europe PMC) and",
           "`discover_registries.py` (Bioconductor, Galaxy), neither of which touches",
           "bio.tools. Two questions are asked of each: is it software at all, and is it",
           "in scope. The first matters because the literature channel returns papers, and",
           "a paper can be a protocol or an assay named exactly like a program.", "",
           f"{len(rows)} adjudicated. **{len(accept)} accepted by both models.** "
           f"{len(split)} accepted by one and not the other (left out). "
           f"{len(notsw)} are not software. {len(oos)} are software but out of scope.", "",
           "Read before promoting. A model agreeing with itself is not evidence.", "",
           "## Accepted by both models", "",
           "| name | source | cites | why | description |",
           "| --- | --- | ---: | --- | --- |"]
    for r in sorted(accept, key=lambda r: -(int(r["citations"] or 0) if str(r["citations"] or "").isdigit() else 0)):
        out.append(f"| **{r['name']}** | {r['source']} | {r['citations'] or ''} | "
                   f"{r['reason'][:60]} | {r['desc'][:70]} |")
    for label, group in (("Accepted by only one model", split),
                         ("Judged not to be software", notsw),
                         ("Software, but out of scope", oos)):
        out += ["", f"## {label}", "", "| name | source | why |", "| --- | --- | --- |"]
        for r in sorted(group, key=lambda r: r["name"].lower()):
            out.append(f"| {r['name']} | {r['source']} | {r['reason'][:80]} |")
    DOCS.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(out) + "\n")
    print(f"\n  {len(accept)} accepted by both, {len(split)} split, "
          f"{len(notsw)} not software, {len(oos)} out of scope, ${spend:.3f}")
    print(f"  -> {REPORT}")


if __name__ == "__main__":
    main()
