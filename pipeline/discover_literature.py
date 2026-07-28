#!/usr/bin/env python3
"""Stage 1d - find tools from the literature that no registry indexes.

Registries lag the literature, and for this field they lag it badly:
`docs/provenance.md` records that the entire sequence-to-function deep-learning
generation is absent from bio.tools. Those methods all have papers. So this
stage looks where the tools are actually announced.

**The trick is the title convention.** Bioinformatics tool papers are titled
"NAME: what it does" with remarkable consistency, which turns tool-name
extraction from an entity-recognition problem into a regular expression. The
name comes from before the colon and the evidence from after it, and the
evidence then goes through `select_domain.classify()` like everything else. A
title with no colon yields nothing, which is the right failure: no name, no
candidate.

Two properties make this worth more than the registry sweep per candidate:

  * Every hit arrives with a DOI, a PMID and a year, so a promoted seed carries
    a real publication rather than a bare link. The registry sweep cannot do
    that; most of its seeds landed with no paper at all.
  * Recency. Europe PMC has the 2024-2026 methods literature that no registry
    has caught up with.

Queries are TITLE-scoped on purpose. Abstract-scoped queries return every paper
that merely uses a tool, and the name before the colon is then the wrong name.

    python pipeline/discover_literature.py [--refresh] [--pages N]
"""
from __future__ import annotations

import argparse
import json
import re
import time
from datetime import date

import requests

from build import norm_name
from config import CACHE, DATA, DOCS, RAW, user_agent
from mdutil import cell
from select_domain import classify

CANDIDATES = RAW / "literature_candidates.json"
REPORT = DOCS / "literature-discovery.md"
LIT_CACHE = CACHE / "literature"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

# Title-scoped, so a hit is a paper *about* the tool rather than one using it.
QUERIES = [
    'TITLE:"transcription factor binding"',
    'TITLE:"transcription factor binding site"',
    'TITLE:"motif discovery"',
    'TITLE:"sequence motif"',
    'TITLE:"motif enrichment"',
    'TITLE:"regulatory element"',
    'TITLE:"cis-regulatory"',
    'TITLE:"enhancer prediction"',
    'TITLE:"promoter prediction"',
    'TITLE:"peak calling"',
    'TITLE:"ChIP-seq"',
    'TITLE:"ATAC-seq"',
    'TITLE:"chromatin accessibility"',
    'TITLE:"gene regulatory network"',
    'TITLE:"regulatory variant"',
    'TITLE:"footprinting"',
    'TITLE:"nucleosome positioning"',
    'TITLE:"single-cell ATAC"',
]

# "NAME: what it does". The name is bounded because a long left-hand side is a
# sentence clause, not a tool: "Regulation of gene expression: a review".
TOOL_TITLE = re.compile(r"^\s*([A-Za-z][A-Za-z0-9._+-]{1,24})\s*:\s+(.{15,})$")

# Left-hand sides that are editorial or structural rather than a tool name.
NOT_A_NAME = {
    "correction", "corrigendum", "erratum", "editorial", "comment", "reply",
    "response", "review", "correspondence", "letter", "note", "commentary",
    "abstract", "introduction", "background", "conclusion", "summary",
    "chapter", "author", "authors", "retraction", "retracted", "withdrawn",
    "expression", "regulation",
    "analysis", "identification", "prediction", "characterization",
    "characterisation", "comparison", "evaluation", "assessment", "study",
    "insights", "advances", "overview", "perspective", "update", "erratum to",
}


def http() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": user_agent()})
    return s


def search(session, query: str, pages: int, refresh: bool) -> list[dict]:
    """Paginate one query, caching the whole result set on disk."""
    LIT_CACHE.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", query.lower()).strip("-")[:60]
    path = LIT_CACHE / f"{slug}.json"
    if path.exists() and not refresh:
        return json.loads(path.read_text())

    results, cursor = [], "*"
    for _ in range(pages):
        r = session.get(EPMC, params={
            "query": f"({query}) AND SRC:MED", "format": "json",
            "pageSize": 1000, "cursorMark": cursor,
        }, timeout=90)
        r.raise_for_status()
        blob = r.json()
        batch = blob.get("resultList", {}).get("result", [])
        results.extend(batch)
        nxt = blob.get("nextCursorMark")
        if not nxt or nxt == cursor or not batch:
            break
        cursor = nxt
        time.sleep(0.35)          # Europe PMC asks for restraint, not a key
    path.write_text(json.dumps(results))
    return results


def candidate_from(paper: dict) -> dict | None:
    title = (paper.get("title") or "").strip().rstrip(".")
    m = TOOL_TITLE.match(title)
    if not m:
        return None
    name, rest = m.group(1).strip(), m.group(2).strip()
    if name.lower() in NOT_A_NAME or name.isdigit():
        return None
    doi = (paper.get("doi") or "").strip()
    pmid = (paper.get("pmid") or "").strip()
    return {
        "name": name,
        "title": title,
        "description": rest,
        "doi": doi,
        "pmid": pmid,
        "year": (paper.get("pubYear") or "").strip(),
        "journal": (paper.get("journalTitle") or "").strip(),
        "citations": paper.get("citedByCount") or 0,
        "url": f"https://doi.org/{doi}" if doi
               else f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "",
        "source": "europepmc",
    }


def as_biotools_record(cand: dict) -> dict:
    """The title after the colon is the description. No EDAM annotation exists."""
    return {"name": cand["name"], "description": cand["description"],
            "function": [], "topic": []}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true", help="re-query Europe PMC")
    ap.add_argument("--pages", type=int, default=3,
                    help="pages of 1000 per query (default 3)")
    args = ap.parse_args()

    catalog = json.loads((DATA / "catalog.json").read_text())
    seen = {norm_name(t["name"]) for t in catalog["tools"]}
    seen |= {norm_name(t["biotools_id"]) for t in catalog["tools"] if t.get("biotools_id")}
    # A paper already cited by the catalog is a tool we already have, whatever
    # it is called. This catches renames and suite members.
    seen_pubs = {t["publication"] for t in catalog["tools"] if t.get("publication")}

    session = http()
    best: dict[str, dict] = {}
    papers = 0
    for query in QUERIES:
        results = search(session, query, args.pages, args.refresh)
        papers += len(results)
        for paper in results:
            cand = candidate_from(paper)
            if not cand:
                continue
            tier, reason = classify(as_biotools_record(cand))
            if not tier:
                continue
            cand["tier"], cand["reason"] = tier, reason
            ident = (f"pmid:{cand['pmid']}" if cand["pmid"]
                     else f"doi:{cand['doi']}" if cand["doi"] else "")
            cand["known"] = (norm_name(cand["name"]) in seen or
                             (ident and ident in seen_pubs))
            # The same tool is announced once; keep the most-cited title if a
            # name recurs, which prefers the tool paper over a later benchmark.
            key = norm_name(cand["name"])
            if key not in best or cand["citations"] > best[key]["citations"]:
                best[key] = cand
        print(f"  {query:44s} {len(results):5d} papers")

    candidates = sorted(best.values(),
                        key=lambda c: (c["known"], -int(c["citations"] or 0),
                                       c["name"].lower()))
    fresh = [c for c in candidates if not c["known"]]
    stats = {"papers_scanned": papers, "named_tools": len(candidates),
             "not_in_catalog": len(fresh)}

    CANDIDATES.parent.mkdir(parents=True, exist_ok=True)
    CANDIDATES.write_text(json.dumps(
        {"generated": date.today().isoformat(), "stats": stats,
         "list": candidates}, indent=1))
    write_report(candidates, stats)
    print(f"\nscanned {papers} papers, {len(candidates)} named tools, "
          f"{len(fresh)} not in the catalog")
    print(f"-> {REPORT.relative_to(DOCS.parent)}")


def write_report(candidates: list[dict], stats: dict) -> None:
    fresh = [c for c in candidates if not c["known"]]
    known = len(candidates) - len(fresh)
    out = [
        "# Literature discovery",
        "",
        f"Generated {date.today().isoformat()} by `make discover-lit`.",
        "",
        "Tools announced in the literature, found by the naming convention of "
        "the field: bioinformatics tool papers are titled *NAME: what it does*. "
        "The name is taken from before the colon and the text after it goes "
        "through the same domain filter the bio.tools records face.",
        "",
        f"- **{stats['papers_scanned']} papers** scanned across "
        f"{len(QUERIES)} title-scoped Europe PMC queries",
        f"- **{stats['named_tools']} named in-domain tools** extracted",
        f"- **{stats['not_in_catalog']} are not in the catalog**; {known} are, "
        "which is the control that the extraction is finding this field rather "
        "than a neighbouring one",
        "",
        "**Nothing here is in the catalog.** Promote a row by adding it to "
        "[`curation/seeds.yaml`](../curation/seeds.yaml). Unlike the registry "
        "sweep, every row carries a DOI and a year, so a promoted entry gets a "
        "real publication and a citation count rather than a bare link.",
        "",
        "Sorted by citation count, so the tools the field actually adopted come "
        "first. A high count here is a reason to look, not evidence of quality.",
        "",
        "| Tool | Cites | Year | What the paper says it does |",
        "| --- | ---: | ---: | --- |",
    ]
    for c in fresh:
        link = f"[{cell(c['name'])}]({c['url']})" if c["url"] else cell(c["name"])
        out.append(f"| {link} | {c['citations']} | {c['year']} | "
                   f"{cell(c['description'][:150])} |")
    out.append("")
    REPORT.write_text("\n".join(out))


if __name__ == "__main__":
    main()
