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
from config import (CATEGORY_KEYS, CURATION, DATA, DB_TOOLTYPES, MONOREPOS,
                    OP_CATEGORY, RAW, SUITE_PUBLICATIONS, TEXT_CATEGORY,
                    TOPIC_CATEGORY, is_preprint)

ENRICHED = RAW / "enriched.json.gz"
SEEDS = CURATION / "seeds.yaml"
OVERLAY = CURATION / "overlay.yaml"
PROPOSALS = CURATION / "llm_proposals.yaml"
CATALOG_JSON = DATA / "catalog.json"
CATALOG_TSV = DATA / "catalog.tsv"

TEXT_CATEGORY_RE = {k: [re.compile(p, re.I) for p in v] for k, v in TEXT_CATEGORY.items()}

COLUMNS = [
    "id", "name", "description", "categories", "primary_category", "tier",
    "homepage", "homepage_status", "repo_url", "repo_status", "repo_origin", "repo_stars", "repo_pushed", "repo_archived",
    "repo_language", "repo_license", "tool_type", "topics", "languages",
    "license", "license_source", "maturity", "cost", "registries", "citations", "citation_note", "year", "publication",
    "citations_total", "citations_papers",
    "publication_is_preprint",
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


def load_repo_map() -> dict[str, str]:
    """bio.tools ID -> repository slug, from pipeline/resolve_repos.py.

    Only entries that passed validation are applied; the rest stay in
    docs/repo-review.md for a human to judge.
    """
    path = DATA / "cache" / "repo_map.json"
    if not path.exists():
        return {}
    try:
        blob = json.loads(path.read_text())
    except ValueError:
        return {}
    return {k: v["slug"] for k, v in blob.items() if v.get("accepted")}


def is_monorepo(url: str) -> bool:
    """Is this link a shared repository holding hundreds of unrelated tools?

    A Galaxy wrapper whose recorded homepage is `github.com/galaxyproject/galaxy`
    does not have a repository; it lives inside someone else's. Accepting it
    credits the tool with the monorepo's stars, activity, licence and language,
    which is how a small wrapper became the most-starred entry in this catalog.
    """
    m = re.match(r"https?://(?:www\.)?github\.com/([^/]+/[^/#?]+)", url or "")
    return bool(m) and m.group(1).rstrip("/").lower() in MONOREPOS


def repo_origin(tool: dict, repomap: dict[str, str]) -> str:
    """Where a repository link came from, because it changes how much to trust it.

    Links recorded upstream are the tool's own statement. Links *inferred* by
    matching a homepage or a GitHub search are our guess, validated but still a
    guess, and those are the ones worth inviting corrections on.
    """
    if tool.get("_repo_slug") or tool.get("_repo_other"):
        return "recorded"          # GitHub, or GitLab/SourceForge/Bitbucket
    if tool.get("biotoolsID", "") in repomap:
        return "inferred"
    return ""


def load_registry_map() -> dict[str, dict[str, str]]:
    """Tool id -> {registry: url}, from pipeline/discover_registries.py.

    Kept separate from the enrichment pass because it answers a different
    question: enrichment records what bio.tools *says* a tool ships as, while
    this records where the package can actually be installed from today. Only
    name-plus-description matches are written, never a name alone.
    """
    path = DATA / "cache" / "registry_map.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except ValueError:
        return {}


def load_year_map() -> dict[str, str]:
    """Publication identifier key -> year, from pipeline/fill_metadata.py."""
    path = DATA / "cache" / "pubyear_cache.json"
    if not path.exists():
        return {}
    try:
        return {k: v for k, v in json.loads(path.read_text()).items() if v}
    except ValueError:
        return {}


def load_homepage_status() -> dict[str, str]:
    """Homepage URL -> state, from pipeline/check_homepages.py.

    Only `dead` (404/410) is carried into the catalog. `unreachable` is a
    timeout or a DNS failure, which is as often a slow institutional host as a
    departed one, and asserting it would repeat the mistake the DOI checker
    made when it called 151 rate-limited requests broken links.
    """
    path = DATA / "cache" / "homepage_check.json"
    if not path.exists():
        return {}
    try:
        blob = json.loads(path.read_text())
    except ValueError:
        return {}
    # Canonicalised, because the same page appears as a homepage and as a
    # repository link with a different scheme or a www prefix: PROBC's record
    # holds `http://www.github.com/seferlab/probc` and
    # `https://github.com/seferlab/probc` for one deleted repository.
    dead = {}
    for url, r in blob.items():
        if r.get("state") == "dead":
            dead[canon_link(url)] = "dead"
    return dead


def canon_link(url: str) -> str:
    return re.sub(r"^https?://(www\.)?", "", (url or "").strip().lower()).rstrip("/")


def load_install_map() -> dict[str, dict[str, str]]:
    """Tool id -> {registry: url}, from pipeline/resolve_installs.py.

    Stronger evidence than the registry sweep: these come from a badge or an
    install command on the tool's OWN repository page, which is the project
    stating where it ships rather than us finding a package of the same name.
    Only routes whose package name matches the tool or its repository are
    written; the rest stay in docs/install-review.md.
    """
    path = DATA / "cache" / "install_map.json"
    if not path.exists():
        return {}
    try:
        blob = json.loads(path.read_text())
    except ValueError:
        return {}
    return {k: v["accepted"] for k, v in blob.items() if v.get("accepted")}


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


def primary_identifier(tool: dict, pubmap: dict[str, str] | None = None) -> str:
    """The tool's own paper: the one bio.tools marks Primary, else the first.

    Summing every linked publication - what the dissertation's script did - is
    badly wrong, because bio.tools attaches a suite's paper to each of its
    member tools. The EMBOSS paper is linked to dozens of EMBOSS commands and
    the Bioconductor paper to 23 packages here, so summing hands each member
    the whole suite's citation count and the ranking becomes meaningless.

    Where a tool genuinely has several of its own papers, the fix is a
    hand-checked list in `verified_publications`, not a rule: see
    apply_verified_publications() for why no rule works.
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
        if not is_preprint(ident):
            return ident
    return candidates[0] if candidates else ""


def norm_name(name: str) -> str:
    """Loose name key, so a seed does not duplicate a bio.tools record.

    bio.tools spells the same tool several ways - "Cluster Buster" vs
    "Cluster-Buster", "SCENIC+" vs "scenicplus" - and an exact lowercase match
    lets both into the catalog.

    ``+`` is spelled out rather than stripped, because stripping it merges a
    successor tool into its predecessor. Bare removal made "SCENIC+" normalise
    to "scenic", so the hand-written SCENIC+ seed was skipped as a duplicate of
    SCENIC - a different tool - while bio.tools' own `scenicplus` record sat in
    the catalog beside it. Naming a successor after its parent plus a symbol is
    a convention here (SCENIC+, Yeastract+, DeltaNeTS+), so this is a family of
    bugs rather than one.
    """
    return re.sub(r"[^a-z0-9]", "", name.lower().replace("+", "plus"))


def repo_url(tool: dict, repomap: dict[str, str] | None = None) -> str:
    if tool.get("_repo_slug"):
        return f"https://github.com/{tool['_repo_slug']}"
    resolved = (repomap or {}).get(tool.get("biotoolsID", ""))
    if resolved:
        return f"https://github.com/{resolved}"
    for u in tool.get("_repo_other") or []:
        return u
    return ""


# ---------------------------------------------------------------------------
def from_biotools(tool: dict, cites: dict[str, int], shared: dict[str, int],
                  pubmap: dict[str, str], repomap: dict[str, str]) -> dict:
    gh = tool.get("_github") or {}
    ids = tool.get("_identifiers") or []
    # A monorepo is not this tool's repository. Drop the link AND everything
    # derived from it, or the stars survive the link that justified them.
    repo = repo_url(tool, repomap)
    if is_monorepo(repo):
        repo, gh = "", {}
    primary = primary_identifier(tool, pubmap)
    n_sharing = shared.get(primary, 0)
    # A publication linked by several tools is a suite paper, not this tool's
    # own. We genuinely do not know the member's individual impact, so record
    # nothing rather than something misleading.
    if primary in SUITE_PUBLICATIONS:
        citations, note = None, "publication is a platform or suite paper"
    elif primary and n_sharing >= 3:
        citations, note = None, f"primary publication shared by {n_sharing} tools"
    else:
        # An identifier we failed to look up is unknown, not zero. Defaulting to
        # 0 made a failed lookup indistinguishable from an uncited paper, and the
        # cache held 410 such failures stored as real zeros.
        citations, note = (cites.get(cache_key(primary)) if primary else None), ""
    return {
        "id": tool["biotoolsID"],
        "name": tool["name"],
        "description": first_sentence(tool.get("description") or ""),
        "categories": assign_categories(tool),
        "tier": tool.get("_tier", "core"),
        "homepage": tool.get("homepage") or "",
        "repo_url": repo,
        "repo_origin": repo_origin(tool, repomap) if repo else "",
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
        "citations_total": None,
        "citations_papers": None,
        "year": pub_year(tool),
        "publication": primary or (ids[0] if ids else ""),
        "publication_is_preprint": is_preprint(primary or ""),
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


def apply_verified_publications(row: dict, papers: list[str], cites: dict[str, int]) -> str:
    """Aggregate a hand-checked list of one tool's own papers.

    `citations` becomes the most-cited paper in the list, so the ranked number
    still points at a single work a reader can open. The sum lands in
    `citations_total` and is only ever displayed as "across N papers"; nothing
    sorts on it, because a total is not comparable with the single-paper counts
    the rest of the catalog carries.

    Why the list is hand-written and cannot be derived: bio.tools' publication
    field mixes a tool's own papers with the method it implements, the community
    guidelines it follows and the platform hosting it. Summing it gave
    phantompeakqualtools the ENCODE ChIP-seq guidelines paper (+2,244) and every
    Galaxy wrapper the Galaxy platform's 1,965. `type: Primary` cannot separate
    them either: 75% of entries are untyped, including all eight of the MEME
    Suite's. Matching the tool name against the title fails in both directions -
    it admits Meta-MEME and ParaMEME by substring while rejecting MEME's own 1994
    paper, whose title is "Fitting a mixture model by expectation maximization".

    Returns a note describing what was left out, for the audit trail.
    """
    counts = {}
    for ident in dict.fromkeys(papers):        # dedupe: two records list one paper twice
        c = cites.get(cache_key(ident))
        if c is not None:
            counts[ident] = c
    if len(counts) < 2:
        # Not enough resolvable counts to total honestly; leave the row alone.
        return f"verified list has {len(counts)} resolvable count(s); no total shown"
    best = max(counts, key=counts.get)
    row["citations"] = counts[best]
    row["publication"] = best
    row["publication_is_preprint"] = is_preprint(best)
    row["citations_total"] = sum(counts.values())
    row["citations_papers"] = len(counts)
    missing = len(dict.fromkeys(papers)) - len(counts)
    return f"{missing} verified paper(s) had no citation count" if missing else ""


def from_seed(seed: dict, cites: dict[str, int] | None = None,
              shared: dict[str, int] | None = None) -> dict:
    """A hand-written entry, given the same citation treatment as a harvested one.

    Seeds used to be built with `citations: None` unconditionally, which meant a
    curated tool showed no count even when its DOI was sitting in the citation
    cache. FIMO was the visible case: one of the most-cited papers in the field,
    displayed blank, purely because it is carried as a seed rather than by
    bio.tools. The suite-paper suppression applies here too, so a seed sharing
    its primary publication with two or more other tools is still left blank.
    """
    ident = ""
    if seed.get("pmid"):
        ident = f"pmid:{seed['pmid']}"
    elif seed.get("doi"):
        ident = f"doi:{seed['doi']}"

    citations, note = None, ""
    n_sharing = (shared or {}).get(ident, 0)
    if ident in SUITE_PUBLICATIONS:
        note = "publication is a platform or suite paper"
    elif ident and n_sharing >= 3:
        note = f"primary publication shared by {n_sharing} tools"
    elif ident:
        # The cache is keyed by cache_key(), not by the raw identifier.
        citations = (cites or {}).get(cache_key(ident))
    return {
        "id": seed["name"],
        "name": seed["name"],
        "description": seed.get("description", ""),
        "categories": [c for c in CATEGORY_KEYS if c in set(seed.get("categories") or [])],
        "tier": "seed",
        "homepage": seed.get("url", ""),
        "repo_url": f"https://github.com/{seed['repo']}" if seed.get("repo") else "",
        "repo_origin": "curated" if seed.get("repo") else "",
        "repo_stars": None, "repo_pushed": "", "repo_archived": None,
        "repo_language": "", "repo_license": "",
        "tool_type": [], "topics": [], "languages": [],
        "license": "", "maturity": "", "cost": "",
        "citations": citations, "citation_note": note, "year": seed.get("year", ""),
        "citations_total": None, "citations_papers": None,
        "publication": ident,
        "publication_is_preprint": is_preprint(ident),
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
    repomap = load_repo_map()
    regmap = load_registry_map()
    installmap = load_install_map()
    yearmap = load_year_map()
    deadpages = load_homepage_status()
    # How many catalog tools claim each publication as their primary one.
    shared = Counter(p for p in (primary_identifier(t, pubmap) for t in enriched) if p)
    seeds = yaml.safe_load(SEEDS.read_text()) or {}
    overlay = yaml.safe_load(OVERLAY.read_text()) or {}

    featured = overlay.get("featured") or {}
    corrections = overlay.get("corrections") or {}
    excluded = overlay.get("exclude") or {}
    aliases = overlay.get("aliases") or {}
    pub_overrides = overlay.get("publications") or {}
    verified_pubs = {k: v["papers"] for k, v in
                     (overlay.get("verified_publications") or {}).items()}
    no_article = overlay.get("no_article") or {}
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
        rows.append(from_biotools(tool, cites, shared, pubmap, repomap))
        seen_names[norm_name(tool["name"])] = bid

    seeded = 0
    for seed in seeds.get("tools") or []:
        if norm_name(seed["name"]) in seen_names:
            continue          # bio.tools already has it; the harvested record wins
        rows.append(from_seed(seed, cites, shared))
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
        if key in corrections and "repo_url" in corrections[key]:
            row["repo_origin"] = "curated"
        if key in pub_overrides:
            row["publication"] = pub_overrides[key]
            row["publication_is_preprint"] = is_preprint(pub_overrides[key])
            # The count has to follow the link. Overriding only the link left the
            # citation describing the paper we just decided was the wrong one:
            # Signac pointed at its Nature Methods paper while still reporting
            # the bioRxiv preprint's 164 rather than 1,889.
            row["citations"] = cites.get(cache_key(pub_overrides[key]))
        if key in verified_pubs:
            note = apply_verified_publications(row, verified_pubs[key], cites)
            if note:
                row["citation_note"] = note
        if key in featured:
            row["featured"] = featured[key]
        else:
            row["featured"] = ""
        row["primary_category"] = row["categories"][0] if row["categories"] else "uncategorised"

    rows.sort(key=lambda r: (-int(r["citations"] or 0), r["name"].lower()))

    # Fill what is derivable rather than leaving a blank the reader has to
    # research. Both are marked, and neither overwrites a stated value.
    for r in rows:
        r["homepage_status"] = deadpages.get(canon_link(r.get("homepage")), "")
        # A deleted repository is a dead link too, and for six tools here the
        # repository *is* the homepage.
        r["repo_status"] = deadpages.get(canon_link(r.get("repo_url")), "")
        if not r.get("year") and r.get("publication"):
            r["year"] = yearmap.get(cache_key(r["publication"]), "")
        # An empty citation cell has three quite different causes, and a reader
        # cannot tell them apart. Sierra showed blank because its published DOI
        # was never fetched, which looked identical to a tool with no paper at
        # all; say which it is instead of leaving it to be re-investigated.
        if r["citations"] is None and not r["citation_note"]:
            # "no publication recorded" reads as missing data waiting to be
            # filled. For these it is settled: the software has no paper, or the
            # only candidate was examined and rejected. Say which.
            if r["id"] in no_article:
                r["citation_note"] = no_article[r["id"]]
            else:
                r["citation_note"] = ("no publication recorded" if not r.get("publication")
                                      else "publication not indexed by OpenAlex")
        # A repository's licence is weaker evidence than a declared one, so say
        # which it is rather than quietly merging the two.
        if r.get("license"):
            r["license_source"] = "declared"
        elif r.get("repo_license"):
            r["license"] = r["repo_license"]
            r["license_source"] = "repository"
        else:
            r["license_source"] = ""

    # Package availability: what bio.tools recorded, plus what the registry
    # sweep verified. Sorted so the TSV column is stable across rebuilds.
    for r in rows:
        merged = dict(r.get("_registries") or {})
        merged.update(regmap.get(r["id"], {}))
        # Applied last, so a route the project advertises itself wins over one
        # inferred from a name match.
        merged.update(installmap.get(r["id"], {}))
        r["_registries"] = merged
        r["registries"] = "|".join(sorted(merged))

    meta = {
        "generated": date.today().isoformat(),
        "count": len(rows),
        "from_biotools": len(rows) - seeded,
        "curated_seeds": seeded,
        "featured": sum(1 for r in rows if r["featured"]),
        "with_repo": sum(1 for r in rows if r["repo_url"]),
        "repo_recovered": sum(1 for r in rows if r["repo_url"] and r["id"] in repomap),
        "repo_by_origin": {k: sum(1 for r in rows if r["repo_url"] and r["repo_origin"] == k)
                           for k in ("recorded", "inferred", "curated")},
        "llm_assisted": sum(1 for r in rows if r.get("_llm_applied")),
        "llm_scope_dropped": len(llm_out_of_scope),
    }
    CATALOG_JSON.write_text(json.dumps({"meta": meta, "tools": rows}, indent=1))

    with CATALOG_TSV.open("w", newline="") as fh:
        w = csv.writer(fh, delimiter="\t")
        w.writerow(COLUMNS)
        for r in rows:
            w.writerow([
                "|".join(r.get(c) or []) if isinstance(r.get(c), list) else
                ("" if r.get(c) is None else r.get(c))
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
