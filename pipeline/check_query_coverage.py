#!/usr/bin/env python3
"""Check that the sweep asks for what the filter admits.

The harvest queries bio.tools by EDAM annotation and a short list of free-text
phrases. `select_domain.classify()` admits a record whose *description* matches
STRONG_TEXT_PATTERNS. Those two lists are maintained independently, and when
they drift the failure is silent: a tool whose description is squarely in scope
and whose EDAM terms are not is never fetched, so it is never judged, so it
never appears anywhere - not in the catalog, not in the exclusions, not in any
report. Nothing looks wrong.

That drift is measurable. An exhaustive pass over all 34,379 bio.tools records
on 2026-09-03 found 405 the sweep had never seen; 200 of the 212 later confirmed
in scope had been admitted on a text rule and 2 on an EDAM operation. At the
time, 49 of the 71 alternatives in STRONG_TEXT_PATTERNS had no query that would
surface them.

This compares the two lists directly. An alternative counts as covered when some
query string matches it - if the sweep asks for "DNA methylation", records whose
description says "DNA methylation" arrive to be judged.

    python pipeline/check_query_coverage.py            # report
    python pipeline/check_query_coverage.py --strict   # exit 1 if anything is uncovered
"""
from __future__ import annotations

import argparse
import re
import sys

from config import (QUERY_FREETEXT, QUERY_OPERATIONS, QUERY_TOPICS,
                    STRONG_TEXT_PATTERNS)

# Alternatives deliberately left unqueried, with the reason. A bare term that
# would flood the sweep with out-of-domain records belongs here rather than in
# QUERY_FREETEXT: the filter would drop them anyway, but the harvest still pays
# for every page.
ACCEPTED_GAPS = {
    r"\bDMRs?\b": "three letters; matches unrelated acronyms as a phrase query",
    r"\bDMPs?\b": "three letters; matches unrelated acronyms as a phrase query",
    r"\bPWM\b": "queried as 'position weight matrix', the spelled-out form",
    r"\bPFM\b": "queried as 'position frequency matrix'",
    r"\bPSSM\b": "queried as 'position specific scoring matrix'",
    r"\b[a-z]{1,3}QTLs?\b": "a regex class, not a phrase; the named QTL types are queried",
    r"\bB[iS]S?-?seq\b": "a regex class; 'bisulfite sequencing' covers the same records",
    r"\bH[1-4](K|R)\d+(me|ac|ub|ph)\d*\b": "mark nomenclature is a pattern; 'histone modification' is queried",
    r"\bdiscriminative .{0,12}motif": "wildcard span; 'motif discovery' reaches the same tools",
    r"\bmotifs? in DNA": "phrasing variant of 'DNA motif', which is queried",
    r"\bcalls? peaks\b": "verb phrasing of 'peak calling', which is queried",
}


def alternatives(pattern: str) -> list[str]:
    """Split a regex on top-level | only, leaving grouped alternations intact."""
    out, depth, cur = [], 0, ""
    for ch in pattern:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "|" and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return [a for a in out if a.strip()]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 when an alternative is uncovered and unexcused")
    args = ap.parse_args()

    queries = list(QUERY_FREETEXT) + list(QUERY_OPERATIONS) + list(QUERY_TOPICS)
    covered, accepted, missing = [], [], []
    for pattern in STRONG_TEXT_PATTERNS:
        for alt in alternatives(pattern):
            try:
                rx = re.compile(alt, re.I)
            except re.error:
                continue
            hit = next((q for q in queries if rx.search(q)), None)
            if hit:
                covered.append((alt, hit))
            elif alt in ACCEPTED_GAPS:
                accepted.append((alt, ACCEPTED_GAPS[alt]))
            else:
                missing.append(alt)

    total = len(covered) + len(accepted) + len(missing)
    print(f"{len(queries)} queries against {total} admission alternatives")
    print(f"  covered by a query : {len(covered)}")
    print(f"  accepted gaps      : {len(accepted)}")
    print(f"  UNCOVERED          : {len(missing)}")
    if accepted:
        print("\naccepted, with reasons:")
        for alt, why in accepted:
            print(f"  {alt[:44]:46s} {why}")
    if missing:
        print("\nuncovered - the filter admits these, the sweep never asks for them:")
        for alt in missing:
            print(f"  {alt}")
        print("\nAdd a phrase to QUERY_FREETEXT, or an entry to ACCEPTED_GAPS saying why not.")
    if missing and args.strict:
        sys.exit(1)


if __name__ == "__main__":
    main()
