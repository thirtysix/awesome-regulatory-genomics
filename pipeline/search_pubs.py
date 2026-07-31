#!/usr/bin/env python3
"""Stage 2h - LAST RESORT: find a tool's paper by searching, then adjudicate.

`discover_pubs.py` asks each tool what to cite and never searches by name,
because searching by name is what put a text-matching library in this catalog
under `Match` and an RPC framework under `SEA`. That rule stands and this stage
does not repeal it. It exists because the authoritative route runs out: of 61
records flagged as carrying an unrelated paper, it resolved 8 and 53 declared
nothing anywhere, most of them older tools whose pages are gone.

What makes searching acceptable HERE, and nowhere else:

* **There is something to verify against.** These records already have a good
  description. The `Match` failure was a name match with nothing to check it
  with; adjudicating a candidate abstract against a known description closes
  exactly that hole.
* **Every candidate is judged, whatever supplied it.** The authoritative route
  is not trusted either: it offered pyPINTS a Nature Protocols paper and SCLC a
  2009 BMC Genomics paper, both of which look wrong. Route determines priority,
  not belief.
* **The route is recorded.** A search-derived answer carries `via: search` so a
  reader can weight it lower than a `CITATION.cff`, and nothing is applied
  automatically in either case.

Order: whatever `discover_pubs.py` already found, then an OpenAlex title search.
A candidate is proposed only when the model says it describes THIS tool, with
its reasoning attached.

    export DEEPINFRA_API_KEY=...
    python pipeline/search_pubs.py [--limit N] [--refresh]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import requests
import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (CURATION, DATA, OPENALEX_API, is_preprint, openalex_params,
                    user_agent)
import enrich
import llm_assist as L

CATALOG = DATA / "catalog.json"
DOCS = DATA.parent / "docs"
CACHE = DATA / "cache" / "search_pubs.json"
REPORT = DOCS / "publication-search.md"

ADJUDICATE_SYSTEM = """You decide whether a candidate paper is the paper that DESCRIBES a given \
bioinformatics tool.

You get the tool's name, what it does, and a numbered list of candidate papers with abstracts. \
Pick the one that introduces or describes that tool, or none.

This matters because tool names collide across all of software. "Match" is a transcription-factor \
site scanner and also a text-matching library; "SEA" is a motif enrichment tool and also an RPC \
framework. A shared name is NOT evidence. The abstract must describe software that does what this \
tool does.

Rules:
- Choose a candidate only when its abstract describes THIS tool's function. When the abstract is \
about biology that merely used the tool, or about a different tool with the same name, choose none.
- A paper that never names the tool can still be correct: method papers often have descriptive \
titles. Judge by what the software does, not by whether the name appears.
- A review, a benchmark comparing many tools, or an application study is NOT the tool's own paper.
- Prefer the paper that INTRODUCES the tool over a later one that uses or updates it.
- confidence "high" only when the abstract plainly describes this tool. If you are weighing two \
plausible candidates, that is "low".
- index is the candidate's number, or null for none.

Reply with JSON only:
{"index": 1, "confidence": "high|medium|low", "reason": "one short clause"}"""


def search_openalex(session, name: str, per_page: int = 8) -> list[dict]:
    """Title-search OpenAlex for a tool name. Candidates, not answers."""
    try:
        r = session.get(OPENALEX_API, params=openalex_params({
            "search": name, "per-page": per_page,
            "select": "id,title,publication_year,cited_by_count,doi,ids,"
                      "abstract_inverted_index,primary_location"}), timeout=30)
        if r.status_code == 429:
            raise SystemExit("OpenAlex daily budget spent; rerun after midnight UTC")
        if r.status_code != 200:
            return []
        return r.json().get("results") or []
    except (requests.RequestException, ValueError):
        return []


def adjudicate(tool: dict, cands: list[dict], api_key: str, model: str) -> dict | None:
    lines = [f"Tool name: {tool['name']}",
             f"What it does: {tool.get('description') or '(unknown)'}", "", "Candidates:"]
    for i, c in enumerate(cands, 1):
        abstract = enrich.abstract_text(c)
        venue = ((c.get("primary_location") or {}).get("source") or {}).get("display_name") or "?"
        lines.append(f"\n[{i}] {c.get('title')}\n    {venue}, {c.get('publication_year')}"
                     f"\n    {abstract[:700] or '(no abstract)'}")
    try:
        text, cost, _ = L.call(model, ADJUDICATE_SYSTEM, "\n".join(lines), api_key)
    except Exception:                                        # noqa: BLE001
        return None
    res = L.parse_json(text)
    if not res or not isinstance(res.get("confidence"), str):
        return None
    res["_cost"] = cost
    return res


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--model", default=L.BULK_MODEL)
    args = ap.parse_args()

    api_key = os.environ.get("DEEPINFRA_API_KEY", "").strip()
    if not api_key:
        sys.exit("DEEPINFRA_API_KEY is not set; this stage is optional and needs it")

    tools = {t["id"]: t for t in json.loads(CATALOG.read_text())["tools"]}
    flagged = (yaml.safe_load((CURATION / "llm_proposals.yaml").read_text()) or {}) \
        .get("paper_mismatch") or {}
    targets = [tools[k] for k in flagged if k in tools]
    session = requests.Session()
    session.headers.update({"User-Agent": user_agent(), "Accept": "application/json"})

    # A sweep whose control case fails measures nothing. One tool whose paper is
    # known and must be found, and one name collision that must NOT be resolved.
    print("controls:")
    ctl_ok = True
    macs = tools.get("macs")
    if macs:
        got = adjudicate(macs, search_openalex(session, "MACS"), api_key, args.model)
        pick = (got or {}).get("index")
        title = ""
        if pick:
            cands = search_openalex(session, "MACS")
            if 1 <= pick <= len(cands):
                title = (cands[pick - 1].get("title") or "").lower()
        ok = "chip" in title and "macs" in title
        print(f"  MACS -> {'ok' if ok else 'FAILED'}: {title[:70] or 'no pick'}")
        ctl_ok &= ok
    fake = {"name": "Zyzzyx", "description": "Predicts transcription factor binding sites "
                                             "from DNA sequence using a hidden Markov model"}
    got = adjudicate(fake, search_openalex(session, "Zyzzyx"), api_key, args.model)
    ok = not (got or {}).get("index")
    print(f"  nonexistent tool -> {'ok' if ok else 'FAILED'}: picked {(got or {}).get('index')}")
    ctl_ok &= ok
    if not ctl_ok:
        sys.exit("  a control failed; aborting rather than reporting a rate")

    if args.limit:
        targets = targets[: args.limit]
    print(f"\nsearching for {len(targets)} flagged records via {args.model}")
    cache = json.loads(CACHE.read_text()) if CACHE.exists() and not args.refresh else {}
    spend = 0.0
    for i, t in enumerate(targets, 1):
        if t["id"] in cache:
            continue
        cands = search_openalex(session, t["name"])
        if not cands:
            cache[t["id"]] = {"name": t["name"], "verdict": "no-candidates"}
            continue
        res = adjudicate(t, cands, api_key, args.model)
        spend += (res or {}).get("_cost", 0)
        pick = (res or {}).get("index")
        if not res or not pick or not (1 <= pick <= len(cands)):
            cache[t["id"]] = {"name": t["name"], "verdict": "none-matched",
                              "reason": (res or {}).get("reason", ""),
                              "n_candidates": len(cands)}
        else:
            c = cands[pick - 1]
            doi = (c.get("doi") or "").replace("https://doi.org/", "")
            pmid = str((c.get("ids") or {}).get("pmid", "")).rsplit("/", 1)[-1]
            cache[t["id"]] = {
                "name": t["name"], "verdict": "candidate",
                "confidence": res.get("confidence", "low"),
                "reason": res.get("reason", ""),
                "title": c.get("title"), "year": c.get("publication_year"),
                "cited_by": c.get("cited_by_count"),
                "venue": ((c.get("primary_location") or {}).get("source") or {})
                         .get("display_name"),
                "doi": doi, "pmid": pmid,
                "recorded": t.get("publication") or "",
                "n_candidates": len(cands), "via": "search"}
        if i % 10 == 0:
            print(f"  {i}/{len(targets)}  ${spend:.3f}", flush=True)
            CACHE.parent.mkdir(parents=True, exist_ok=True)
            CACHE.write_text(json.dumps(cache, indent=1, sort_keys=True))
        time.sleep(0.2)
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache, indent=1, sort_keys=True))

    rows = [dict(v, id=k) for k, v in cache.items() if k in {t["id"] for t in targets}]

    # A candidate that is WORSE than what is already recorded is a regression,
    # and a search will happily offer one. Signac is the case: the catalog links
    # its Nature Methods paper at 1,889 citations and a name search returns the
    # bioRxiv preprint at 164, which is precisely the swap CLAUDE.md documents as
    # having already cost this catalog once. Flag it rather than trusting the
    # model to have weighed it.
    for r in rows:
        if r.get("verdict") != "candidate":
            continue
        warn = []
        cand = f"doi:{r['doi']}" if r.get("doi") else (f"pmid:{r['pmid']}" if r.get("pmid") else "")
        rec = r.get("recorded") or ""
        if cand and is_preprint(cand) and rec and not is_preprint(rec):
            warn.append("candidate is a preprint, the record is not")
        rec_cites = tools.get(r["id"], {}).get("citations")
        if rec_cites and (r.get("cited_by") or 0) < rec_cites * 0.5:
            warn.append(f"candidate has {r.get('cited_by') or 0} citations "
                        f"against {rec_cites} on the record")
        if not r.get("cited_by"):
            warn.append("candidate has no citations at all")
        r["regression"] = "; ".join(warn)

    found = [r for r in rows if r["verdict"] == "candidate"]
    high = [r for r in found if r.get("confidence") == "high"]
    out = ["# Papers found by SEARCH, for records the tool itself would not name", "",
           "GENERATED by `pipeline/search_pubs.py`. Nothing is applied. Promote a row",
           "into `curation/overlay.yaml: publications`, and move the citation count with",
           "the link.", "",
           "**This is the last resort, and the weakest evidence in the pipeline.**",
           "`discover_pubs.py` asks each tool what to cite and never searches by name,",
           "because a name search is what put a text-matching library in this catalog",
           "under `Match`. It is used here only because that route returned nothing for",
           "53 of these 61 records, and only because these records already carry a good",
           "description for a candidate to be judged against - which is the check the",
           "`Match` failure lacked.", "",
           f"{len(rows)} records searched. **{len(found)} produced a candidate**",
           f"({len(high)} at high confidence), {sum(1 for r in rows if r['verdict']=='none-matched')}",
           "found nothing that describes the tool, and",
           f"{sum(1 for r in rows if r['verdict']=='no-candidates')} returned no search results.",
           "",
           "Read the abstract before promoting any of these. A high-confidence pick is",
           "still a model's opinion about a paper it was handed by a name search.", "",
           "A candidate flagged **REGRESSION** looks worse than what is already on the",
           "record - a preprint replacing a published version, or a far lower citation",
           "count. Signac is the standing example: its Nature Methods paper has 1,889",
           "citations and a name search returns the bioRxiv preprint at 164. Do not",
           "promote one of those without reading both.", "",
           "| tool | recorded now | candidate | venue, year | cites | conf | why |",
           "| --- | --- | --- | --- | ---: | --- | --- |"]
    for r in sorted(found, key=lambda r: (bool(r.get("regression")),
                                          r.get("confidence") != "high", r["name"].lower())):
        ident = f"doi:{r['doi']}" if r.get("doi") else (f"pmid:{r['pmid']}" if r.get("pmid") else "?")
        why = r.get("reason", "")[:70]
        if r.get("regression"):
            why = f"**REGRESSION** {r['regression']}"
        out.append(f"| `{r['id']}` {r['name']} | {r.get('recorded') or '-'} | "
                   f"{(r.get('title') or '')[:60]} ({ident}) | {r.get('venue') or '?'}, "
                   f"{r.get('year') or '?'} | {r.get('cited_by') or 0} | "
                   f"{r.get('confidence')} | {why} |")
    unresolved = [r for r in rows if r["verdict"] != "candidate"]
    if unresolved:
        out += ["", "## Still unresolved", "",
                "Neither the tool's own sources nor a search produced anything. The flag",
                "stands; these need a human or should be recorded in `overlay.yaml:",
                "no_article`.", "",
                "| tool | verdict | note |", "| --- | --- | --- |"]
        for r in sorted(unresolved, key=lambda r: r["name"].lower()):
            out.append(f"| `{r['id']}` {r['name']} | {r['verdict']} | {r.get('reason', '')[:80]} |")
    DOCS.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(out) + "\n")
    regress = [r for r in found if r.get("regression")]
    print(f"\n  {len(found)} candidates ({len(high)} high confidence), "
          f"{len(regress)} would be a REGRESSION on what is recorded, "
          f"{len(unresolved)} unresolved, ${spend:.3f}")
    print(f"  -> {REPORT}")


if __name__ == "__main__":
    main()
