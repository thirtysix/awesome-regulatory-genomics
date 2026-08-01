#!/usr/bin/env python3
"""Stage 2i - NEGATIVE RESULT. Kept so the approach is not re-derived.

This scores 1/4 against papers established by hand, the same as every other
automated route tried. Do not reach for it expecting better; read the ceiling
below first.

Searching by tool NAME does not work for this problem, and that is measured
rather than assumed. Against four papers established by hand:

    OpenAlex, name only            0/4
    OpenAlex, name + description   1/4, that one at rank 10
    local corpus, name scan        1/4 clean

The reason is structural: a genomics tool is usually not named in its own paper's
abstract. NRLcalc is introduced in the methods of "CTCF-dependent chromatin
boundaries formed by asymmetric nucleosome arrays"; asSeq's method paper names no
software at all. So this stage queries what the tool DOES. On the hardest of those
Every variant scored 1/4:

    OpenAlex, name only                        0/4
    OpenAlex, name + description               1/4, that one at rank 10
    local corpus, name scan                    1/4 clean
    local corpus, description + boolean AND    1/4
    local corpus, description + weighted rank  1/4   (this file)

**The ceiling is the corpus, not the ranking.** For NRL the pool is correct -
"nucleosome repeat length" does retrieve the right paper - but nothing can rank
it, because the description's distinguishing terms (`phasograms`, `NucTools`)
appear in no abstract at all, while the shared term is common to hundreds of
chromatin papers. There is no signal left to discriminate on.

A manual Google search of the same descriptions found 4/4. That is not a better
query, it is a richer corpus: Google indexes tool homepages, third-party tool
directories and paper full text, which is where the statement "this page
describes tool X and cites paper Y" actually lives. A title-and-abstract corpus
does not contain it. To automate this, automate a web search, not this.

Boolean AND over description terms was the first attempt here and scored 1/4 as
well: a tool's description and its paper's abstract overlap only partly, so
requiring every term returns nothing. NRL's description names `phasograms` and
`NucTools`, neither of which appears in its paper's abstract. Weighted OR - one
broad scan on the most distinctive term, then ranking the rest by overlap - is
what BM25 actually does and degrades gracefully when a term is absent.

Corpus: `pubmed_rag_2026` on the local PostgreSQL, 21.9M articles, title and
abstract only, 2000 onward. Two limits follow from that and are not fixable here:
a tool named only in a methods section cannot be found by name whatever the query,
and anything published before 2000 is absent (tfscan, 1996).

Read-only. `chunks` carries no text index, so each query is a sequential scan of
roughly a minute; this runs a handful per tool, not one per candidate.

    export DEEPINFRA_API_KEY=...
    python pipeline/search_pubs_local.py [--validate] [--limit N]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import CURATION, DATA
from search_pubs import adjudicate
import llm_assist as L

CATALOG = DATA / "catalog.json"
DOCS = DATA.parent / "docs"
CACHE = DATA / "cache" / "search_pubs_local.json"
REPORT = DOCS / "publication-search-local.md"
DB = "pubmed_rag_2026"

# Words that carry no retrieval signal here: every tool in this catalog analyses
# sequence data, so "sequence" and "analysis" select nothing.
GENERIC = set("""a an the of for and or to in on with from by as at is are be it its this that
using use used uses via into data based approach method methods tool tools software package web
server provides provide analysis analyses analysing analyzing analyze analyzes sequence sequences
sequencing genomic genome genomics gene genes dataset datasets file files user users interface
identify identifies identifying detect detects detecting predict predicts predicting compute
computes calculating calculates generate generates providing across between within their them
high low large small new novel multiple various different several including include includes
results result study studies research""".split())

# Phrases worth keeping whole: splitting them loses the discrimination.
PHRASES = [
    "nucleosome repeat length", "transcription factor binding", "chromatin accessibility",
    "gene regulatory network", "cis-regulatory element", "transcription start site",
    "position weight matrix", "allele-specific expression", "core promoter",
    "differential binding", "peak calling", "copy number", "topologically associating",
    "chromatin immunoprecipitation", "nascent transcript", "enhancer promoter",
    "regulatory element", "binding site", "motif discovery", "DNase I", "single-cell",
    "histone modification", "DNA methylation", "quantitative trait", "read count",
]


def terms(description: str) -> list[str]:
    """Distinctive query terms from a tool description, most specific first."""
    low = description.lower()
    found = [p for p in PHRASES if p.lower() in low]
    rest = low
    for p in found:
        rest = rest.replace(p.lower(), " ")
    words = [w for w in re.findall(r"[a-z][a-z0-9-]{3,}", rest) if w not in GENERIC]
    # longer words discriminate better than short ones in this vocabulary
    words.sort(key=len, reverse=True)
    return found + words


def query(broad: str, limit: int = 400) -> list[dict]:
    """Articles whose abstract matches ONE broad term, with the text for scoring."""
    pat = broad.replace("'", "''")
    sql = (f"select a.pmid, a.pub_year, a.journal, a.title, "
           f"replace(string_agg(c.chunk_text, ' '), E'\n', ' ') "
           f"from articles a join chunks c on c.pmid = a.pmid "
           f"where a.pmid in (select pmid from chunks where chunk_text ~* '{pat}') "
           f"group by a.pmid, a.pub_year, a.journal, a.title limit {limit};")
    try:
        out = subprocess.run(["psql", "-d", DB, "-Atc", sql],
                             capture_output=True, text=True, timeout=900)
    except subprocess.SubprocessError:
        return []
    rows = []
    for line in out.stdout.splitlines():
        parts = line.split("|", 4)
        if len(parts) == 5 and parts[0].isdigit():
            rows.append({"pmid": parts[0], "year": parts[1], "journal": parts[2],
                         "title": parts[3], "text": parts[4]})
    return rows


def score(row: dict, ts: list[str]) -> float:
    """BM25-lite: weighted overlap between the description's terms and the abstract.

    Boolean AND over description terms was the first attempt and it failed, because
    a tool's description and its paper's abstract only partly overlap. NRL's
    description names `phasograms` and `NucTools`, which appear nowhere in the
    paper's abstract, so ANDing them returned nothing at all. Weighted OR is what
    BM25 actually does, and it degrades gracefully when a term is absent.
    """
    blob = (row["title"] + " " + row["text"]).lower()
    total = 0.0
    for i, t in enumerate(ts):
        if t.lower() in blob:
            # earlier terms are the more distinctive ones; phrases count double
            total += (len(ts) - i) * (2.0 if " " in t else 1.0)
    return total


def retrieve(tool: dict, want: int = 20) -> tuple[list[dict], list[str]]:
    """One broad scan on the most distinctive term, then rank by the rest."""
    ts = terms(tool.get("description") or "")
    if not ts:
        return [], []
    rows = []
    for broad in ts[:3]:              # try the top terms until one returns rows
        rows = query(broad)
        if rows:
            break
    if not rows:
        return [], ts[:1]
    ranked = sorted(rows, key=lambda r: -score(r, ts))
    return ranked[:want], ts[:5]


def as_candidates(rows: list[dict]) -> list[dict]:
    """Shape local rows like the OpenAlex works the adjudicator expects."""
    out = []
    for r in rows:
        w = {"title": r["title"], "publication_year": r["year"],
             "primary_location": {"source": {"display_name": r["journal"]}},
             "ids": {"pmid": r["pmid"]}, "cited_by_count": None, "_pmid": r["pmid"]}
        # hand the adjudicator the real abstract rather than an empty index
        w["_abstract"] = r.get("text", "")[:700]
        out.append(w)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--validate", action="store_true",
                    help="score retrieval against the four papers established by hand")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--model", default=L.BULK_MODEL)
    args = ap.parse_args()

    api_key = os.environ.get("DEEPINFRA_API_KEY", "").strip()
    tools = {t["id"]: t for t in json.loads(CATALOG.read_text())["tools"]}

    if args.validate:
        TRUTH = {"ep3": "18096745", "pyPINTS": "35177836",
                 "NRL": "31665434", "asseq": "21838806"}
        hits = 0
        for tid, want in TRUTH.items():
            t = tools.get(tid)
            if not t:
                print(f"{tid}: not in catalog"); continue
            rows, pats = retrieve(t)
            rank = next((i for i, r in enumerate(rows, 1) if r["pmid"] == want), None)
            hits += bool(rank)
            print(f"{t['name']:<10} {'rank ' + str(rank) if rank else 'NOT FOUND':<12} "
                  f"{len(rows):>3} candidates   terms={pats}")
        print(f"\nretrieval found the known paper {hits}/{len(TRUTH)}")
        return

    flagged = (yaml.safe_load((CURATION / "llm_proposals.yaml").read_text()) or {}) \
        .get("paper_mismatch") or {}
    prior = json.loads((DATA / "cache" / "search_pubs.json").read_text())
    targets = [tools[k] for k in flagged if k in tools
               and prior.get(k, {}).get("verdict") != "candidate"]
    if args.limit:
        targets = targets[: args.limit]
    if not api_key:
        sys.exit("DEEPINFRA_API_KEY is not set; needed to adjudicate")
    print(f"{len(targets)} records to search by description against {DB}")

    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    for i, t in enumerate(targets, 1):
        if t["id"] in cache:
            continue
        rows, pats = retrieve(t)
        if not rows:
            cache[t["id"]] = {"name": t["name"], "verdict": "no-candidates", "terms": pats}
        else:
            res = adjudicate(t, as_candidates(rows), api_key, args.model)
            pick = (res or {}).get("index")
            if not res or not pick or not (1 <= pick <= len(rows)):
                cache[t["id"]] = {"name": t["name"], "verdict": "none-matched",
                                  "terms": pats, "n": len(rows),
                                  "reason": (res or {}).get("reason", "")}
            else:
                r = rows[pick - 1]
                cache[t["id"]] = {"name": t["name"], "verdict": "candidate",
                                  "terms": pats, "n": len(rows),
                                  "confidence": res.get("confidence", "low"),
                                  "reason": res.get("reason", ""),
                                  "pmid": r["pmid"], "title": r["title"],
                                  "year": r["year"], "journal": r["journal"],
                                  "recorded": t.get("publication") or ""}
        print(f"  {i}/{len(targets)} {t['name']:<22} {cache[t['id']]['verdict']}", flush=True)
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(cache, indent=1, sort_keys=True))

    rows = [dict(v, id=k) for k, v in cache.items() if k in {t["id"] for t in targets}]
    found = [r for r in rows if r["verdict"] == "candidate"]
    out = ["# Papers found by searching what a tool DOES", "",
           "GENERATED by `pipeline/search_pubs_local.py`. Nothing is applied.", "",
           "Queries a local PubMed corpus (`pubmed_rag_2026`, 21.9M articles, title and",
           "abstract, 2000 onward) with terms from the tool's own description, then has a",
           "model adjudicate the candidates. Searching by tool NAME was measured at 1/4",
           "against papers established by hand, because a genomics tool is usually not",
           "named in its own paper's abstract.", "",
           "Two limits: a tool named only in a methods section is unreachable, and",
           "anything published before 2000 is not in the corpus.", "",
           f"{len(rows)} searched, **{len(found)} produced a candidate**.", "",
           "| tool | recorded now | candidate | journal, year | conf | why | query terms |",
           "| --- | --- | --- | --- | --- | --- | --- |"]
    for r in sorted(found, key=lambda r: (r.get("confidence") != "high", r["name"].lower())):
        out.append(f"| `{r['id']}` {r['name']} | {r.get('recorded') or '-'} | "
                   f"{r['title'][:56]} (pmid:{r['pmid']}) | {(r.get('journal') or '?')[:28]}, "
                   f"{r.get('year')} | {r.get('confidence')} | {r.get('reason','')[:60]} | "
                   f"{', '.join(r.get('terms') or [])[:44]} |")
    rest = [r for r in rows if r["verdict"] != "candidate"]
    if rest:
        out += ["", "## Nothing found", "", "| tool | verdict | query terms | note |",
                "| --- | --- | --- | --- |"]
        for r in sorted(rest, key=lambda r: r["name"].lower()):
            out.append(f"| `{r['id']}` {r['name']} | {r['verdict']} | "
                       f"{', '.join(r.get('terms') or [])[:44]} | {r.get('reason','')[:60]} |")
    DOCS.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(out) + "\n")
    print(f"\n  {len(found)} candidates, {len(rest)} without\n  -> {REPORT}")


if __name__ == "__main__":
    main()
