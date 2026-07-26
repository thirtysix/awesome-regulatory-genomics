#!/usr/bin/env python3
"""Stage 3 - assemble the catalog.

Merges enriched bio.tools records with hand-written seeds, assigns categories,
applies the curation overlay, and writes the two artefacts everything else is
generated from:

    data/catalog.json   full records, one object per tool
    data/catalog.tsv    flat table, one row per tool

    python pipeline/build.py
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import date

import yaml

from collections import Counter

from jsonio import read_json
from config import (CATEGORY_KEYS, CURATION, DATA, DB_TOOLTYPES, OP_CATEGORY,
                    RAW, TEXT_CATEGORY, TOPIC_CATEGORY)

ENRICHED = RAW / "enriched.json.gz"
SEEDS = CURATION / "seeds.yaml"
OVERLAY = CURATION / "overlay.yaml"
PROPOSALS = CURATION / "llm_proposals.yaml"
CATALOG_JSON = DATA / "catalog.json"
CATALOG_TSV = DATA / "catalog.tsv"

TEXT_CATEGORY_RE = {k: [re.compile(p, re.I) for p in v] for k, v in TEXT_CATEGORY.items()}

COLUMNS = [
    "id", "name", "description", "categories", "primary_category", "tier",
    "homepage", "repo_url", "repo_stars", "repo_pushed", "repo_archived",
    "repo_language", "repo_license", "tool_type", "topics", "languages",
    "license", "maturity", "cost", "citations", "citation_note", "year", "publication",
    "biotools_id", "biotools_url", "last_update", "source", "tags", "featured",
]


# ---------------------------------------------------------------------------
def operations(tool: dict) -> set[str]:
    return {op["term"]
            for fn in tool.get("function") or []
            for op in fn.get("operation") or []}


def topic_terms(tool: dict) -> list[str]:
    return [t["term"] for t in tool.get("topic") or []]


def assign_categories(tool: dict) -> list[str]:
    """Derive categories from EDAM operations, topics, tool type and text.

    Multi-label by design: HOMER is motif discovery *and* peak annotation, and
    forcing a single bucket is what makes most tool tables hard to search.
    """
    found: set[str] = set()
    for op in operations(tool):
        found.update(OP_CATEGORY.get(op, []))
    for term in topic_terms(tool):
        found.update(TOPIC_CATEGORY.get(term, []))

    blob = f"{tool.get('name', '')}. {tool.get('description', '')}"
    for key, patterns in TEXT_CATEGORY_RE.items():
        if any(p.search(blob) for p in patterns):
            found.add(key)

    # A database portal that scored a motif or ChIP category is a *resource*,
    # not a method - reclassify so users can filter the two apart.
    tool_types = set(tool.get("toolType") or [])
    if tool_types & DB_TOOLTYPES:
        if found & {"motif-scanning", "motif-discovery", "tfbs-prediction"}:
            found.add("motif-databases")
        if found & {"peak-calling", "peak-annotation", "nucleosome-chromatin"}:
            found.add("chip-resources")

    return [k for k in CATEGORY_KEYS if k in found]


def first_sentence(text: str) -> str:
    """First sentence, without splitting on e.g./i.e./etc./vs. abbreviations.

    Same rule as the dissertation's filter_results.001.py, kept so the
    Description_short column remains comparable.
    """
    if not text:
        return ""
    parts = re.split(r"(?<!e\.g)(?<!i\.e)(?<!etc)(?<!vs)(?<!cf)\.\s+", text.strip())
    return re.sub(r"<[^>]+>", "", parts[0]).strip()


def pub_year(tool: dict) -> str:
    meta = tool.get("_pubmeta") or {}
    if meta.get("year"):
        return str(meta["year"])
    for pub in tool.get("publication") or []:
        md = pub.get("metadata") or {}
        if md.get("date"):
            m = re.search(r"\b(19|20)\d{2}\b", str(md["date"]))
            if m:
                return m.group()
    return ""


def load_citation_counts() -> dict[str, int]:
    """Per-identifier citation counts from the enrichment cache."""
    counts: dict[str, int] = {}
    path = DATA / "cache" / "citation_cache.csv"
    if path.exists():
        with path.open() as fh:
            for row in csv.reader(fh):
                if len(row) >= 2 and row[0] != "identifier":
                    try:
                        counts[row[0]] = int(row[1])
                    except ValueError:
                        continue
    return counts


def cache_key(ident: str) -> str:
    kind, _, value = ident.partition(":")
    return f"{kind}_{value}".replace("/", "_").replace(":", "_")


def load_publication_map() -> dict[str, str]:
    """preprint DOI -> published DOI, from pipeline/resolve_pubs.py."""
    path = DATA / "cache" / "publication_map.json"
    if not path.exists():
        return {}
    try:
        blob = json.loads(path.read_text())
    except ValueError:
        return {}
    return {d: e["published_doi"] for d, e in blob.items() if e.get("published_doi")}


PREPRINT_PREFIXES = ("10.1101/", "10.21203/", "10.31234/", "10.20944/")


def primary_identifier(tool: dict, pubmap: dict[str, str] | None = None) -> str:
    """The tool's own paper: the one bio.tools marks Primary, else the first.

    Summing every linked publication - what the dissertation's script did - is
    badly wrong, because bio.tools attaches a suite's paper to each of its
    member tools. The EMBOSS paper is linked to dozens of EMBOSS commands and
    the Bioconductor paper to 23 packages here, so summing hands each member
    the whole suite's citation count and the ranking becomes meaningless.
    """
    pubmap = pubmap or {}
    pubs = tool.get("publication") or []
    ordered = sorted(pubs, key=lambda p: 0 if "Primary" in (p.get("type") or []) else 1)

    candidates = []
    for pub in ordered:
        pmid = pub.get("pmid") or (pub.get("metadata") or {}).get("pmid")
        if pmid and str(pmid).lower() not in ("none", "null", ""):
            candidates.append(f"pmid:{pmid}")
            continue
        doi = (pub.get("doi") or "").strip().removeprefix("https://doi.org/")
        if doi:
            # Prefer the peer-reviewed version where Crossref records one.
            candidates.append("doi:" + pubmap.get(doi, doi))

    # A PubMed-indexed or journal DOI beats a preprint, even if bio.tools lists
    # the preprint first: TOBIAS's record carries only the bioRxiv DOI, and
    # linking a reader to a 2019 preprint when the Nature Communications paper
    # exists is a worse citation, not just an older one.
    for ident in candidates:
        if not ident.removeprefix("doi:").startswith(PREPRINT_PREFIXES):
            return ident
    return candidates[0] if candidates else ""


def norm_name(name: str) -> str:
    """Loose name key, so a seed does not duplicate a bio.tools record.

    bio.tools spells the same tool several ways - "Cluster Buster" vs
    "Cluster-Buster", "SCENIC+" vs "scenicplus" - and an exact lowercase match
    lets both into the catalog.
    """
    return re.sub(r"[^a-z0-9]", "", name.lower())


def repo_url(tool: dict) -> str:
    if tool.get("_repo_slug"):
        return f"https://github.com/{tool['_repo_slug']}"
    for u in tool.get("_repo_other") or []:
        return u
    return ""


# ---------------------------------------------------------------------------
def from_biotools(tool: dict, cites: dict[str, int], shared: dict[str, int],
                  pubmap: dict[str, str]) -> dict:
    gh = tool.get("_github") or {}
    ids = tool.get("_identifiers") or []
    primary = primary_identifier(tool, pubmap)
    n_sharing = shared.get(primary, 0)
    # A publication linked by several tools is a suite paper, not this tool's
    # own. We genuinely do not know the member's individual impact, so record
    # nothing rather than something misleading.
    if primary and n_sharing >= 3:
        citations, note = None, f"primary publication shared by {n_sharing} tools"
    else:
        citations, note = cites.get(cache_key(primary), 0) if primary else 0, ""
    return {
        "id": tool["biotoolsID"],
        "name": tool["name"],
        "description": first_sentence(tool.get("description") or ""),
        "categories": assign_categories(tool),
        "tier": tool.get("_tier", "core"),
        "homepage": tool.get("homepage") or "",
        "repo_url": repo_url(tool),
        "repo_stars": gh.get("stars") if gh.get("status") == "ok" else None,
        "repo_pushed": gh.get("pushed_at") or "" if gh.get("status") == "ok" else "",
        "repo_archived": bool(gh.get("archived")) if gh.get("status") == "ok" else None,
        "repo_language": gh.get("language") or "" if gh.get("status") == "ok" else "",
        "repo_license": gh.get("license") or "" if gh.get("status") == "ok" else "",
        "tool_type": tool.get("toolType") or [],
        "topics": topic_terms(tool),
        "languages": tool.get("language") or [],
        "license": tool.get("license") or "",
        "maturity": tool.get("maturity") or "",
        "cost": tool.get("cost") or "",
        "citations": citations,
        "citation_note": note,
        "year": pub_year(tool),
        "publication": primary or (ids[0] if ids else ""),
        "biotools_id": tool["biotoolsID"],
        "biotools_url": f"https://bio.tools/{tool['biotoolsID']}",
        "last_update": (tool.get("lastUpdate") or "")[:10],
        "source": "bio.tools",
        "tags": [],
        "_operations": sorted(operations(tool)),
        "_select_reason": tool.get("_select_reason", ""),
        "_identifiers": ids,
        "_registries": tool.get("_registries") or {},
    }


def from_seed(seed: dict) -> dict:
    ident = ""
    if seed.get("pmid"):
        ident = f"pmid:{seed['pmid']}"
    elif seed.get("doi"):
        ident = f"doi:{seed['doi']}"
    return {
        "id": seed["name"],
        "name": seed["name"],
        "description": seed.get("description", ""),
        "categories": [c for c in CATEGORY_KEYS if c in set(seed.get("categories") or [])],
        "tier": "seed",
        "homepage": seed.get("url", ""),
        "repo_url": f"https://github.com/{seed['repo']}" if seed.get("repo") else "",
        "repo_stars": None, "repo_pushed": "", "repo_archived": None,
        "repo_language": "", "repo_license": "",
        "tool_type": [], "topics": [], "languages": [],
        "license": "", "maturity": "", "cost": "",
        "citations": None, "citation_note": "", "year": "",
        "publication": ident,
        "biotools_id": "", "biotools_url": "",
        "last_update": "",
        "source": "curated",
        "tags": seed.get("tags") or [],
        "_operations": [], "_select_reason": "curated seed",
        "_identifiers": [ident] if ident else [],
        "_registries": {},
    }


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--no-llm", action="store_true",
                    help="ignore curation/llm_proposals.yaml (pure deterministic build)")
    ap.add_argument("--apply-scope", action="store_true",
                    help="also drop records that TWO models independently judged "
                         "out of scope (curation/llm_proposals.yaml: "
                         "out_of_scope_confirmed). Off by default - removing a "
                         "record is destructive, so it stays an explicit choice.")
    args = ap.parse_args()

    enriched = read_json(ENRICHED)["list"]
    cites = load_citation_counts()
    pubmap = load_publication_map()
    # How many catalog tools claim each publication as their primary one.
    shared = Counter(p for p in (primary_identifier(t, pubmap) for t in enriched) if p)
    seeds = yaml.safe_load(SEEDS.read_text()) or {}
    overlay = yaml.safe_load(OVERLAY.read_text()) or {}

    featured = overlay.get("featured") or {}
    corrections = overlay.get("corrections") or {}
    excluded = overlay.get("exclude") or {}
    aliases = overlay.get("aliases") or {}
    pub_overrides = overlay.get("publications") or {}
    alias_targets = {bid for ids in aliases.values() for bid in ids}

    proposed, llm_out_of_scope = {}, {}
    if PROPOSALS.exists() and not args.no_llm:
        blob = yaml.safe_load(PROPOSALS.read_text()) or {}
        if args.apply_scope:
            # Two independent out-of-scope votes, from whichever pass produced
            # them. Both sources require agreement between different models.
            llm_out_of_scope = dict(blob.get("out_of_scope_confirmed") or {})
            llm_out_of_scope.update(blob.get("majority_out_of_scope") or {})
        for key, entry in (blob.get("categories") or {}).items():
            if entry.get("in_scope") and entry.get("confidence") in ("high", "medium"):
                proposed.setdefault(key, {})["categories"] = entry["categories"]
        for key, entry in (blob.get("descriptions") or {}).items():
            proposed.setdefault(key, {})["description"] = entry["description"]


    rows = []
    seen_names: dict[str, str] = {}

    # Hand-vetted records are immune to the automated scope drop. A record that
    # someone deliberately featured, or added to SEED_BIOTOOLS_IDS because no
    # query reached it, has already had human judgement applied - and models do
    # get these wrong. Both judged MAST out of scope on a protein-flavoured
    # bio.tools description; it is a MEME Suite motif scanner.
    protected = set(featured) | {
        t["biotoolsID"] for t in enriched
        if t.get("_select_reason", "").startswith("curated")
    }

    for tool in enriched:
        bid = tool["biotoolsID"]
        if bid in excluded or bid in alias_targets:
            continue
        if bid in llm_out_of_scope and bid not in protected:
            continue
        rows.append(from_biotools(tool, cites, shared, pubmap))
        seen_names[norm_name(tool["name"])] = bid

    seeded = 0
    for seed in seeds.get("tools") or []:
        if norm_name(seed["name"]) in seen_names:
            continue          # bio.tools already has it; the harvested record wins
        rows.append(from_seed(seed))
        seeded += 1

    # LLM proposals, applied BELOW the hand-written overlay so a human
    # correction always wins. Only accepted when the model was confident and
    # kept the tool in scope; everything else stays visible in the proposals
    # file for review rather than being silently dropped.
    for row in rows:
        if row["id"] in proposed:
            row.update(proposed[row["id"]])
            row["_llm_applied"] = sorted(proposed[row["id"]])

    # curation overlay
    for row in rows:
        key = row["id"]
        if key in corrections:
            fix = dict(corrections[key])
            extra = fix.pop("add_categories", None)
            if extra:
                row["categories"] = [c for c in CATEGORY_KEYS
                                     if c in set(row["categories"]) | set(extra)]
            row.update(fix)
        if key in pub_overrides:
            row["publication"] = pub_overrides[key]
        if key in featured:
            row["featured"] = featured[key]
        else:
            row["featured"] = ""
        row["primary_category"] = row["categories"][0] if row["categories"] else "uncategorised"

    rows.sort(key=lambda r: (-int(r["citations"] or 0), r["name"].lower()))

    meta = {
        "generated": date.today().isoformat(),
        "count": len(rows),
        "from_biotools": len(rows) - seeded,
        "curated_seeds": seeded,
        "featured": sum(1 for r in rows if r["featured"]),
        "with_repo": sum(1 for r in rows if r["repo_url"]),
        "llm_assisted": sum(1 for r in rows if r.get("_llm_applied")),
        "llm_scope_dropped": len(llm_out_of_scope),
    }
    CATALOG_JSON.write_text(json.dumps({"meta": meta, "tools": rows}, indent=1))

    with CATALOG_TSV.open("w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(COLUMNS)
        for r in rows:
            w.writerow([
                "|".join(r[c]) if isinstance(r[c], list) else
                ("" if r[c] is None else r[c])
                for c in COLUMNS
            ])

    print(f"catalog: {meta['count']} tools "
          f"({meta['from_biotools']} bio.tools + {meta['curated_seeds']} curated seeds)")
    print(f"  featured: {meta['featured']}   with repository: {meta['with_repo']} "
          f"({meta['with_repo']/max(meta['count'],1):.0%})"
          + (f"   llm-assisted: {meta['llm_assisted']}" if meta["llm_assisted"] else ""))
    cats = Counter(c for r in rows for c in r["categories"])
    for k in CATEGORY_KEYS:
        print(f"    {k:22s} {cats.get(k, 0):4d}")
    print(f"    {'(uncategorised)':22s} {sum(1 for r in rows if not r['categories']):4d}")
    print(f"-> {CATALOG_JSON.name}, {CATALOG_TSV.name}")


if __name__ == "__main__":
    main()
