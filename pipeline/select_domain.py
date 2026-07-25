#!/usr/bin/env python3
"""Stage 1b - select in-domain records from the wide sweep.

The sweep trades precision for recall. This step restores precision, and it is
where the scope of the resource is actually decided. Admission is tiered:

  ``core``      a STRONG EDAM operation - specific enough to stand alone.
  ``extended``  a WEAK operation, or a text match, corroborated by a domain
                topic. This is the escape hatch for bio.tools' annotation gaps:
                FIMO is filed under "Genotyping", HOCOMOCO under "Data
                handling", and peak callers like gcapc, Q and CCAT carry no
                usable operation at all.

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
                    KEEP_TEXT_PATTERNS, RAW, STRONG_OPERATIONS,
                    STRONG_TEXT_PATTERNS, WEAK_OPERATIONS)

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


def classify(tool: dict) -> tuple[str | None, str]:
    """Return (tier, reason). tier is None when the record is rejected."""
    blob = text_blob(tool)
    ops = operations(tool)

    # A hard exclusion names another field's core object and beats everything.
    for rx in HARD_RE:
        if rx.search(blob):
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
    # Hand-vetted records fetched by ID skip the filter by construction.
    forced = set(sweep.get("forced") or [])

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
