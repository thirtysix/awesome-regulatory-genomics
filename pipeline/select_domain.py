#!/usr/bin/env python3
"""Stage 1b - select in-domain records from the wide sweep.

The sweep trades precision for recall. This step restores precision, and it is
where the scope of the resource is actually decided. Admission is tiered:

  ``core``      a STRONG EDAM operation - specific enough to stand alone.
  ``extended``  a WEAK operation, or a text match, corroborated by a domain
                topic. This is the escape hatch for bio.tools' annotation gaps:
                HOCOMOCO is filed under "Data handling", SICER under "Sequence
                contamination filtering", and peak callers like gcapc, Q and
                CCAT carry no usable operation at all.

Every record is then tested against EXCLUDE_TEXT_PATTERNS, which removes
neighbouring fields that share vocabulary - mass spectrometry "peak detection",
protein "structural motifs", RNA "secondary structure motifs".

Rejected records are written to rejected.json so the boundary can be reviewed
rather than taken on trust.

    python pipeline/select_domain.py
"""
from __future__ import annotations

import json
import re
from collections import Counter

from jsonio import read_json, write_json
from config import (DOMAIN_TOPICS, EXCLUDE_TEXT_PATTERNS, HARD_EXCLUDE_PATTERNS,
                    KEEP_TEXT_PATTERNS, RAW, SEED_BIOTOOLS_IDS,
                    STRONG_OPERATIONS, STRONG_TEXT_PATTERNS, WEAK_OPERATIONS)

SWEEP = RAW / "biotools_sweep.json.gz"
SELECTED = RAW / "selected.json.gz"
REJECTED = RAW / "rejected.json"

KEEP_RE = [re.compile(p, re.I) for p in KEEP_TEXT_PATTERNS]
STRONG_RE = [re.compile(p, re.I) for p in STRONG_TEXT_PATTERNS]
HARD_RE = [re.compile(p, re.I) for p in HARD_EXCLUDE_PATTERNS]
EXCLUDE_RE = [re.compile(p, re.I) for p in EXCLUDE_TEXT_PATTERNS]


def operations(tool: dict) -> set[str]:
    return {op["term"]
            for fn in tool.get("function") or []
            for op in fn.get("operation") or []}


def topics(tool: dict) -> set[str]:
    return {t["term"] for t in tool.get("topic") or []}


def text_blob(tool: dict) -> str:
    return f"{tool.get('name', '')}. {tool.get('description', '')}"


def lead_blob(tool: dict, sentences: int = 2) -> str:
    """Name plus the opening sentences: what the tool actually is.

    bio.tools descriptions often concatenate the tool's own summary with a lab
    or portal blurb ("We are the Providers of ... Drug design software"), or
    with a second record joined by " | ". Hard exclusions are matched against
    this leading portion so a footer cannot disqualify the tool.
    """
    desc = (tool.get("description") or "").split(" | ")[0]
    parts = re.split(r"(?<!e\.g)(?<!i\.e)(?<!etc)(?<!vs)\.\s+", desc.strip())
    return f"{tool.get('name', '')}. " + ". ".join(parts[:sentences])


def classify(tool: dict) -> tuple[str | None, str]:
    """Return (tier, reason). tier is None when the record is rejected."""
    blob = text_blob(tool)
    ops = operations(tool)

    # A hard exclusion names another field's core object and beats everything,
    # but it is tested only against the LEADING description, not the whole
    # record. bio.tools entries frequently append institutional boilerplate:
    # SEProm, a prokaryotic promoter predictor, carries "We are the Providers
    # of ... Protein structure prediction tool ... Drug design software" from
    # its host lab, and matching that would exclude the tool on the strength of
    # its web page footer.
    for rx in HARD_RE:
        if rx.search(lead_blob(tool)):
            return None, f"hard-excluded:{rx.pattern[:30]}"

    # An unambiguous domain phrase settles it, and beats the soft exclusions: those
    # name neighbouring FIELDS, and a record that plainly says what it does in
    # this field is not made out of scope by mentioning a phylogenetic tree or
    # a proteomics dataset alongside.
    for rx in STRONG_RE:
        if rx.search(blob):
            return "core", f"text:{rx.pattern[:36]}"

    # Otherwise hard exclusions win over everything, including a STRONG
    # operation. bio.tools mis-assigns those too - KEGG carries "Gene
    # regulatory network analysis", Geneious "Sequence motif discovery" - so
    # trusting the ontology here readmits whole neighbouring fields.
    for rx in EXCLUDE_RE:
        if rx.search(blob):
            return None, f"excluded:{rx.pattern[:32]}"

    if ops & STRONG_OPERATIONS:
        return "core", "operation:" + sorted(ops & STRONG_OPERATIONS)[0]

    has_topic = bool(topics(tool) & DOMAIN_TOPICS)
    if ops & WEAK_OPERATIONS:
        if has_topic:
            return "extended", "weak-operation+topic"
        for rx in KEEP_RE:
            if rx.search(blob):
                return "extended", "weak-operation+text"
        return None, "weak-operation, no corroboration"

    for rx in KEEP_RE:
        if rx.search(blob):
            if has_topic:
                return "extended", f"text+topic:{rx.pattern[:32]}"
            return None, "text match, no domain topic"

    return None, "no-match"


def main() -> None:
    sweep = read_json(SWEEP)
    provenance = sweep.get("provenance", {})
    # Hand-vetted records skip the filter by construction. config is the single
    # source of truth, NOT the sweep's stored copy: unioning the two made
    # additions work but silently ignored removals, so a record deleted from
    # SEED_BIOTOOLS_IDS stayed curated until the next re-harvest. That is how
    # bio.tools' `mast` (the single-cell package, not the MEME Suite scanner)
    # survived being taken off the list.
    forced = set(SEED_BIOTOOLS_IDS)

    kept, dropped, why = [], [], Counter()
    for tool in sweep["list"]:
        if tool["biotoolsID"] in forced:
            tier, reason = "core", "curated: fetched by ID"
        else:
            tier, reason = classify(tool)
        if tier:
            tool["_tier"] = tier
            tool["_select_reason"] = reason
            tool["_queries"] = provenance.get(tool["biotoolsID"], [])
            kept.append(tool)
            why[tier] += 1
        else:
            dropped.append({"biotoolsID": tool["biotoolsID"], "name": tool["name"],
                            "reason": reason,
                            "description": (tool.get("description") or "")[:200],
                            "operations": sorted(operations(tool))})
            why[reason.split(":")[0]] += 1

    write_json(SELECTED, {"count": len(kept), "list": kept})
    write_json(REJECTED, {"count": len(dropped), "list": dropped})

    print(f"swept    {sweep['count']:5d}")
    print(f"selected {len(kept):5d}  ({len(kept)/max(sweep['count'],1):.0%})")
    for reason, n in why.most_common():
        print(f"    {reason:32s} {n:5d}")
    print(f"rejected {len(dropped):5d} -> {REJECTED.name}")


if __name__ == "__main__":
    main()
