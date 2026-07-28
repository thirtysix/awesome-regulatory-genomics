#!/usr/bin/env python3
"""Stage 1c - find in-domain tools that bio.tools does not index.

bio.tools is one registry with one submission culture, and `docs/provenance.md`
measures the consequence: 32 of 85 canonical tools in this field are absent from
it outright. Those tools are not hiding. They are packaged, documented and
installable in registries that bio.tools simply does not mirror.

So this stage sweeps registries that carry their own domain taxonomy, and puts
every candidate through the SAME filter the bio.tools records face
(`select_domain.classify`). The taxonomy is what makes it work: a Bioconductor
package tagged `ChIPSeq` has been classified by its author against a controlled
vocabulary, which is exactly the corroborating signal `classify()` wants and
exactly what a bare package name cannot supply.

Sources, and why these:

  bioconductor  VIEWS is one file carrying Package, Title, Description and
                biocViews for every release package. The richest source
                available, and its taxonomy maps cleanly onto EDAM topics.
  galaxy        The ToolShed API lists every published repository with a
                description and a homepage. It has no domain taxonomy, so
                candidates from it must clear a STRONG text pattern on their
                own - the same bar a bio.tools record with useless annotation
                has to clear.

Deliberately NOT a source: **bioconda**. Its public package index gives names
and versions without summaries, and the anaconda.org API that carried summaries
now returns 401. Admitting on a name alone is the precise failure this project
rejects everywhere else: `medusa` is a genome scaffolder here and a motif model
there. bioconda remains useful for *resolving a repository for a tool already
known* (`resolve_repos.py`), where the tool's own description supplies the
evidence. It is not usable for discovery.

Nothing here is added to the catalog automatically. Candidates are written to
docs/registry-discovery.md for promotion into curation/seeds.yaml by hand, the
same treatment repository near-misses and model proposals get.

    python pipeline/discover_registries.py [--refresh]
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import date

import requests

from build import norm_name
from config import CACHE, DATA, DOCS, RAW, user_agent
from mdutil import cell
from select_domain import classify

CANDIDATES = RAW / "registry_candidates.json"
REPORT = DOCS / "registry-discovery.md"
REGISTRY_CACHE = CACHE / "registries"

BIOCONDUCTOR_VIEWS = "https://bioconductor.org/packages/release/bioc/VIEWS"
TOOLSHED_REPOS = "https://toolshed.g2.bx.psu.edu/api/repositories"

# biocViews term -> the EDAM topic it stands in for.
#
# Only terms specific enough to corroborate on their own are mapped, mirroring
# STRONG vs WEAK operations. `SystemsBiology` and `NetworkInference` are left
# out because they cover metabolic and signalling networks as readily as
# regulatory ones, and `PeakDetection` is left out for the reason it is left out
# of the EDAM query plan: in practice it is mass spectrometry's term.
BIOCVIEW_TOPIC = {
    "ChIPSeq": "ChIP-seq",
    "ChIPchip": "ChIP-on-chip",
    "ATACSeq": "Epigenomics",
    "DNaseSeq": "Epigenomics",
    "Epigenetics": "Epigenetics",
    "MotifAnnotation": "Sequence sites, features and motifs",
    "MotifDiscovery": "Sequence sites, features and motifs",
    "GeneRegulation": "Gene regulation",
    "GeneTarget": "Transcription factors and regulatory sites",
    "Transcription": "Gene transcription",
}


def http() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": user_agent()})
    return s


def fetch(session, url: str, name: str, refresh: bool) -> str:
    """Fetch with an on-disk cache, so re-runs and CI need no network."""
    REGISTRY_CACHE.mkdir(parents=True, exist_ok=True)
    path = REGISTRY_CACHE / f"{name}.txt"
    if path.exists() and not refresh:
        return path.read_text(encoding="utf-8")
    r = session.get(url, timeout=180)
    r.raise_for_status()
    path.write_text(r.text, encoding="utf-8")
    return r.text


# ---------------------------------------------------------------------------
# sources
# ---------------------------------------------------------------------------
def parse_dcf(text: str) -> list[dict]:
    """Debian Control Format: `Field: value`, indented continuations, blank-line separated."""
    records, current, key = [], {}, None
    for line in text.split("\n"):
        if not line.strip():
            if current:
                records.append(current)
            current, key = {}, None
            continue
        if line[0] in " \t" and key:
            current[key] += " " + line.strip()
            continue
        m = re.match(r"([A-Za-z0-9/_.-]+):\s?(.*)$", line)
        if m:
            key = m.group(1)
            current[key] = m.group(2)
    if current:
        records.append(current)
    return records


def from_bioconductor(session, refresh: bool) -> list[dict]:
    text = fetch(session, BIOCONDUCTOR_VIEWS, "bioconductor-views", refresh)
    out = []
    for pkg in parse_dcf(text):
        name = pkg.get("Package")
        if not name:
            continue
        views = [v.strip() for v in (pkg.get("biocViews") or "").split(",") if v.strip()]
        topics = sorted({BIOCVIEW_TOPIC[v] for v in views if v in BIOCVIEW_TOPIC})
        # Title is the one-line summary; Description is the paragraph. Both are
        # used for matching, but only Title is shown, because Bioconductor
        # descriptions run to several hundred words.
        out.append({
            "name": name,
            "title": pkg.get("Title", "").strip(),
            "description": " ".join(filter(None, [pkg.get("Title", ""),
                                                  pkg.get("Description", "")])).strip(),
            "homepage": f"https://bioconductor.org/packages/{name}/",
            "source": "bioconductor",
            "taxonomy": views,
            "topics": topics,
        })
    return out


def from_galaxy(session, refresh: bool) -> list[dict]:
    text = fetch(session, TOOLSHED_REPOS, "galaxy-toolshed", refresh)
    out = []
    for repo in json.loads(text):
        if repo.get("deprecated"):
            continue
        name = (repo.get("name") or "").strip()
        desc = " ".join(filter(None, [repo.get("description") or "",
                                      repo.get("long_description") or ""])).strip()
        if not name:
            continue
        out.append({
            "name": name,
            "title": (repo.get("description") or "").strip(),
            "description": desc,
            "homepage": repo.get("homepage_url") or repo.get("remote_repository_url") or "",
            "source": "galaxy",
            "taxonomy": [],
            # The ToolShed has no domain taxonomy, so nothing corroborates a
            # weak signal here. A candidate must clear a STRONG text pattern.
            "topics": [],
        })
    return out


SOURCES = {"bioconductor": from_bioconductor, "galaxy": from_galaxy}


# ---------------------------------------------------------------------------
def as_biotools_record(cand: dict) -> dict:
    """Shape a registry entry like a bio.tools record, so classify() applies.

    Reusing the audited filter rather than writing a second one is the point:
    the hard exclusions, the strong/weak text tiers and the topic corroboration
    all behave identically, and the unit tests cover both paths at once.
    """
    return {
        "name": cand["name"],
        "description": cand["description"],
        "function": [],                     # registries carry no EDAM operations
        "topic": [{"term": t} for t in cand["topics"]],
    }


def known_names(catalog: dict) -> set[str]:
    names = set()
    for tool in catalog["tools"]:
        names.add(norm_name(tool["name"]))
        if tool.get("biotools_id"):
            names.add(norm_name(tool["biotools_id"]))
    return names


def canon_url(url: str) -> str:
    """Compare links by identity, not by string.

    A GitHub link is reduced to owner/repo so that `.../tree/master/x`,
    a trailing slash and a `www.` prefix all resolve to the same thing.
    """
    u = re.sub(r"^https?://(www\.)?", "", (url or "").strip().lower()).rstrip("/")
    m = re.match(r"(github\.com/[^/]+/[^/]+)", u)
    return m.group(1) if m else u


def known_urls(catalog: dict) -> set[str]:
    urls = {canon_url(t.get("repo_url")) for t in catalog["tools"]}
    urls |= {canon_url(t.get("homepage")) for t in catalog["tools"]}
    urls.discard("")
    return urls


def collapse_wrappers(candidates: list[dict]) -> list[dict]:
    """One tool, one candidate.

    The Galaxy ToolShed publishes a repository per *wrapper*, so a single tool
    arrives several times: AlphaGenome appears five times, once per exposed
    operation, all pointing at the same homepage. Grouping by link rather than
    by name is safe, because a shared link is evidence rather than a guess.
    The shortest name is kept, since the wrappers are named by suffixing it.
    """
    groups: dict[str, list[dict]] = {}
    loose = []
    for cand in candidates:
        key = canon_url(cand.get("homepage"))
        if key:
            groups.setdefault(f"{cand['source']}|{key}", []).append(cand)
        else:
            loose.append(cand)
    out = list(loose)
    for members in groups.values():
        members.sort(key=lambda c: (len(c["name"]), c["name"]))
        best = dict(members[0])
        if len(members) > 1:
            best["merged"] = [m["name"] for m in members[1:]]
        out.append(best)
    return out


def wrapper_of(cand: dict, catalog_names: dict[str, str]) -> str:
    """Name an existing catalog tool this candidate is probably packaging.

    Flagged for the reviewer, never used to drop anything: name containment is
    the exact heuristic this project refuses to admit records on, and it is no
    more trustworthy for rejecting them. `chipseq_workflows` matches `chipseq`
    without being a wrapper of it.
    """
    for token in re.split(r"[^a-z0-9]+", cand["name"].lower()):
        if len(token) >= 4 and token in catalog_names:
            return catalog_names[token]
    return ""


REGISTRY_MAP = CACHE / "registry_map.json"


def link_known_tools(entries: list[dict], catalog: dict) -> dict[str, dict[str, str]]:
    """Answer "can I install this today?" for tools the catalog already has.

    A package whose *name* matches a tool is a candidate and nothing more, for
    the usual reason: bioconda's `medusa` is a genome scaffolder while this
    catalog's MEDUSA is a motif model. So a link is only recorded when the
    package description shares at least two content words with the tool's, the
    same bar `resolve_repos.validate()` applies to a repository.
    """
    from resolve_repos import tokens

    by_name: dict[str, dict] = {}
    for entry in entries:
        by_name.setdefault(norm_name(entry["name"]), entry)

    found: dict[str, dict[str, str]] = {}
    for tool in catalog["tools"]:
        entry = by_name.get(norm_name(tool["name"]))
        if not entry or entry["source"] != "bioconductor":
            continue
        shared = tokens(tool.get("description") or "") & tokens(entry["description"])
        if len(shared) >= 2:
            found[tool["id"]] = {"bioconductor": entry["homepage"]}
    return found


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true",
                    help="re-fetch the registries instead of using the cache")
    ap.add_argument("--source", choices=sorted(SOURCES), action="append",
                    help="limit to one source (repeatable)")
    args = ap.parse_args()

    catalog = json.loads((DATA / "catalog.json").read_text())
    seen = known_names(catalog)
    seen_urls = known_urls(catalog)
    # Only names long enough to be distinctive; short ones collide with words.
    catalog_names = {norm_name(t["name"]): t["name"]
                     for t in catalog["tools"] if len(t["name"]) >= 4}
    session = http()

    chosen = args.source or sorted(SOURCES)
    candidates, stats, all_entries = [], {}, []
    for source in chosen:
        entries = SOURCES[source](session, args.refresh)
        all_entries.extend(entries)
        kept = []
        for cand in entries:
            tier, reason = classify(as_biotools_record(cand))
            if not tier:
                continue
            cand = dict(cand, tier=tier, reason=reason)
            # Known by name, or by pointing at a link the catalog already has.
            # The second catches wrappers whose name shares nothing with the
            # tool they package.
            cand["known"] = (norm_name(cand["name"]) in seen
                             or canon_url(cand.get("homepage")) in seen_urls)
            kept.append(cand)
        kept = collapse_wrappers(kept)
        for cand in kept:
            cand["wraps"] = wrapper_of(cand, catalog_names)
        stats[source] = {
            "scanned": len(entries),
            "in_domain": len(kept),
            "new": sum(1 for c in kept if not c["known"]),
        }
        candidates.extend(kept)
        print(f"{source:14s} scanned {stats[source]['scanned']:5d}  "
              f"in domain {stats[source]['in_domain']:4d}  "
              f"not in catalog {stats[source]['new']:4d}")

    candidates.sort(key=lambda c: (c["known"], c["source"], c["name"].lower()))
    CANDIDATES.parent.mkdir(parents=True, exist_ok=True)
    CANDIDATES.write_text(json.dumps(
        {"generated": date.today().isoformat(), "stats": stats,
         "list": candidates}, indent=1))

    # Second product of the same sweep: availability links for tools already
    # in the catalog. Same data, different question.
    links = link_known_tools(all_entries, catalog)
    REGISTRY_MAP.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_MAP.write_text(json.dumps(links, indent=1, sort_keys=True))
    print(f"{'availability':14s} matched {len(links)} catalog tools to a package")

    write_report(candidates, stats)
    new = sum(s["new"] for s in stats.values())
    print(f"-> {REPORT.relative_to(DOCS.parent)} ({new} candidates not in the catalog)")


def write_report(candidates: list[dict], stats: dict) -> None:
    fresh = [c for c in candidates if not c["known"]]
    confirmed = [c for c in candidates if c["known"]]

    out = [
        "# Registry discovery",
        "",
        f"Generated {date.today().isoformat()} by `make discover`.",
        "",
        "Tools found in registries that bio.tools does not index, filtered by the "
        "same rules the bio.tools records face (`select_domain.classify`). "
        "**Nothing here is in the catalog.** Promote an entry by adding it to "
        "[`curation/seeds.yaml`](../curation/seeds.yaml); this file is regenerated "
        "and is not itself an input.",
        "",
        "| Source | Scanned | In domain | Not yet in the catalog |",
        "| --- | ---: | ---: | ---: |",
    ]
    for source, s in sorted(stats.items()):
        out.append(f"| {source} | {s['scanned']} | {s['in_domain']} | {s['new']} |")
    out += [
        "",
        f"{len(confirmed)} further in-domain entries are already in the catalog "
        "under the same name. That overlap is the useful control: it is evidence "
        "the filter behaves the same way on registry text as on bio.tools text, "
        "rather than admitting a different population.",
        "",
        "## Candidates",
        "",
        "`tier` is `core` where a strong domain phrase settled it on its own, and "
        "`extended` where a registry category corroborated a weaker signal.",
        "",
        "| Tool | Source | Tier | Why it matched | Summary |",
        "| --- | --- | --- | --- | --- |",
    ]
    for c in fresh:
        link = f"[{cell(c['name'])}]({c['homepage']})" if c["homepage"] else cell(c["name"])
        why = c["reason"]
        if c["taxonomy"]:
            why += " · " + ", ".join(c["taxonomy"][:3])
        if c.get("merged"):
            why += f" · {len(c['merged']) + 1} wrappers merged"
        if c.get("wraps"):
            why += f" · may package {c['wraps']}"
        summary = (c["title"] or c["description"])[:160]
        out.append(f"| {link} | {c['source']} | {c['tier']} | {cell(why)} | {cell(summary)} |")
    out += [
        "",
        "### Reading this list",
        "",
        "Precision is deliberately not 100%. This is a review queue, not a "
        "catalog: the cost of a wrong row here is one glance, while the cost of "
        "a missing tool is a gap nobody sees. Two caveats are worth knowing "
        "before working through it.",
        "",
        "**Galaxy publishes one repository per wrapper, not per tool.** Entries "
        "sharing a homepage are merged automatically, which is what collapses "
        "AlphaGenome's five wrappers into one row. Where a candidate's name "
        "contains an existing catalog tool it is flagged *may package X* and "
        "left in, because name containment is exactly the evidence this project "
        "refuses to act on: `chipseq_workflows` contains `chipseq` without being "
        "a wrapper of it.",
        "",
        "**Bioconductor's taxonomy is broader than this catalog's scope.** "
        "`Transcription` and `GeneRegulation` are applied to differential-"
        "expression and imputation packages too, so a row like an RNA-seq "
        "dropout imputer is the taxonomy being loose rather than the filter "
        "being broken.",
    ]
    REPORT.write_text("\n".join(out))


if __name__ == "__main__":
    main()
