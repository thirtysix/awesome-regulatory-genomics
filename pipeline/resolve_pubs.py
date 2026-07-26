#!/usr/bin/env python3
"""Stage 2b - point publication links at the peer-reviewed version, and check them.

bio.tools records the publication that existed when the entry was created, which
for a large slice of the catalog is a bioRxiv or medRxiv preprint that has since
appeared in a journal. TOBIAS is the clearest case: bio.tools carries
``10.1101/869560`` while the paper is in Nature Communications.

Crossref records the link explicitly, as ``relation.is-preprint-of`` on the
preprint's own record, so this is a lookup rather than a guess. Where the
relation is absent the preprint link is kept: a title search would occasionally
attach the wrong paper, and a preprint link is merely dated, whereas a wrong one
is a false citation.

The same pass validates every DOI, because a link that 404s is worse than no
link at all. Results are cached, so re-runs are free and offline.

    python pipeline/resolve_pubs.py [--refresh] [--check-all]
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from config import CACHE, CURATION, DOCS, RAW
from jsonio import read_json
from mdutil import cell

ENRICHED = RAW / "enriched.json.gz"
PUBMAP = CACHE / "publication_map.json"
REPORT = DOCS / "link-check.md"
CROSSREF = "https://api.crossref.org/works/"

PREPRINT_PREFIXES = ("10.1101/", "10.21203/", "10.31234/", "10.20944/", "10.48550/")


def session() -> requests.Session:
    s = requests.Session()
    # Crossref's polite pool: identify yourself and you get better service.
    s.headers.update({"User-Agent": "awesome-regulatory-genomics/1.0 "
                                    "(+https://github.com/thirtysix/awesome-regulatory-genomics; "
                                    "mailto:contact@example.org)"})
    return s


def crossref(http: requests.Session, doi: str, attempts: int = 5) -> dict | None:
    """Fetch one Crossref record, backing off on rate limits.

    Crossref returns 429 freely under concurrency, and treating that as "this
    DOI is broken" is badly wrong: an early version of this script reported 151
    dead links that were all rate-limited retries of perfectly good DOIs. Only a
    genuine 404 means the DOI does not exist.
    """
    delay = 1.0
    for attempt in range(attempts):
        try:
            r = http.get(CROSSREF + doi, timeout=30)
        except requests.RequestException:
            time.sleep(delay)
            delay *= 2
            continue
        if r.status_code == 200:
            try:
                return r.json()["message"]
            except (ValueError, KeyError):
                return None
        if r.status_code == 404:
            return {"_status": 404}
        # 429 and 5xx are transient; honour Retry-After when given.
        wait = float(r.headers.get("Retry-After") or delay)
        time.sleep(min(wait, 30))
        delay *= 2
    return None                       # exhausted retries: unknown, not broken


def verify_curated(http: requests.Session) -> list[tuple]:
    """Check that every hand-written publication points at the right paper.

    Resolving is not enough. A DOI can be perfectly valid and still be the wrong
    article: this catalog shipped ChromBPNet pointing at "The maize
    cis-regulatory landscape", footprintDB at a riboswitch paper and i-cisTarget
    at a therapeutic-peptide database, all of which resolve happily. Hand-written
    identifiers are the ones at risk, because they are the ones written from
    memory rather than harvested.

    The check is a heuristic - many correct papers do not carry the tool's name
    in the title (MAST is "Combining evidence using p-values") - so it reports
    for review rather than failing the build.
    """
    import re
    import yaml as _yaml
    seeds = (_yaml.safe_load((CURATION / "seeds.yaml").read_text()) or {}).get("tools") or []
    overlay = _yaml.safe_load((CURATION / "overlay.yaml").read_text()) or {}
    entries = [(s["name"], "doi", s["doi"]) for s in seeds if s.get("doi")]
    entries += [(s["name"], "pmid", str(s["pmid"])) for s in seeds if s.get("pmid")]
    for key, ident in (overlay.get("publications") or {}).items():
        kind, _, val = ident.partition(":")
        entries.append((key, kind, val))

    def norm(x):
        return re.sub(r"[^a-z0-9]", "", (x or "").lower())

    flagged = []
    for name, kind, val in entries:
        title = None
        if kind == "doi":
            msg = crossref(http, val)
            if msg and "_status" not in msg:
                title = (msg.get("title") or [""])[0]
            elif msg and msg.get("_status") == 404:
                flagged.append((name, val, "DOES NOT RESOLVE", ""))
                continue
        else:
            try:
                r = http.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                             params={"db": "pubmed", "id": val, "retmode": "json"}, timeout=25)
                title = list(r.json()["result"].values())[-1].get("title")
            except Exception:                                # noqa: BLE001
                title = None
        time.sleep(0.2)
        if not title:
            continue                       # DataCite DOIs (arXiv, Bioconductor) land here
        stem = re.split(r"[ /(]", name)[0]
        if norm(stem) not in norm(title):
            flagged.append((name, val, "name not in title", title[:80]))
    return flagged


def identifiers(tool: dict) -> list[str]:
    out = []
    for pub in tool.get("publication") or []:
        doi = (pub.get("doi") or "").strip().removeprefix("https://doi.org/")
        if doi:
            out.append(doi)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--refresh", action="store_true", help="ignore cached lookups")
    ap.add_argument("--check-all", action="store_true",
                    help="validate every DOI, not just preprints (slower)")
    ap.add_argument("--skip-curated-check", action="store_true",
                    help="skip verifying hand-written seed/overlay publications")
    ap.add_argument("--workers", type=int, default=3,
                    help="Crossref is shared infrastructure; keep this modest")
    args = ap.parse_args()

    tools = read_json(ENRICHED)["list"]
    all_dois = sorted({d for t in tools for d in identifiers(t)})
    preprints = [d for d in all_dois if d.lower().startswith(PREPRINT_PREFIXES)]
    todo = all_dois if args.check_all else preprints
    print(f"{len(all_dois)} distinct DOIs, {len(preprints)} of them preprints")

    cache = json.loads(PUBMAP.read_text()) if PUBMAP.exists() else {}
    if args.refresh:
        cache = {}
    todo = [d for d in todo if d not in cache]
    print(f"looking up {len(todo)} (rest cached)")

    http = session()
    lock = threading.Lock()
    done = [0]

    def lookup(doi: str):
        msg = crossref(http, doi)
        time.sleep(0.2)
        if msg is None:
            entry = {"state": "unknown"}          # retries exhausted; NOT a dead link
        elif "_status" in msg:
            entry = {"state": "broken", "http": msg["_status"]}
        else:
            published = [x["id"] for x in (msg.get("relation", {}).get("is-preprint-of") or [])]
            entry = {"state": "ok", "type": msg.get("type"),
                     "title": (msg.get("title") or [""])[0][:120],
                     "journal": (msg.get("container-title") or [""])[0][:80],
                     "published_doi": published[0] if published else None}
        with lock:
            cache[doi] = entry
            done[0] += 1
            if done[0] % 50 == 0:
                print(f"  {done[0]}/{len(todo)}", flush=True)
                PUBMAP.parent.mkdir(parents=True, exist_ok=True)
                PUBMAP.write_text(json.dumps(cache, indent=1, sort_keys=True))
        return entry

    if todo:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for fut in as_completed([pool.submit(lookup, d) for d in todo]):
                try:
                    fut.result()
                except Exception as exc:                     # noqa: BLE001
                    print(f"    ! {exc}", file=sys.stderr)

    PUBMAP.parent.mkdir(parents=True, exist_ok=True)
    PUBMAP.write_text(json.dumps(cache, indent=1, sort_keys=True))

    upgraded = {d: e["published_doi"] for d, e in cache.items()
                if e.get("published_doi")}
    broken = {d: e for d, e in cache.items() if e.get("state") == "broken"}
    unknown = [d for d, e in cache.items() if e.get("state") in ("unknown", "error")]
    stuck = [d for d in preprints
             if d in cache and cache[d].get("state") == "ok" and not cache[d].get("published_doi")]

    print(f"\npreprints with a published version on Crossref: {len(upgraded)}")
    print(f"preprints with none recorded (link kept as-is):  {len(stuck)}")
    print(f"DOIs that genuinely 404:                         {len(broken)}")
    print(f"DOIs Crossref would not answer for (unknown):     {len(unknown)}")

    out = ["# Publication link check", "",
           "Generated by `make links`. bio.tools records the publication that existed "
           "when an entry was created, so a large share of the catalog points at "
           "preprints that have since appeared in journals.", "",
           f"- **{len(all_dois)} distinct DOIs** in the catalog"
           f" ({len(preprints)} preprints).",
           f"- **{len(upgraded)} preprints upgraded** to the peer-reviewed version via "
           "Crossref's `is-preprint-of` relation.",
           f"- **{len(stuck)} preprints kept as-is**: Crossref records no published "
           "version. A title search could find some of them, but it would "
           "occasionally attach the wrong paper, and a dated link is better than a "
           "false citation.",
           f"- **{len(broken)} DOIs genuinely 404.** Crossref returns 429 freely under "
           "concurrency, and an early version of this check reported 151 dead links "
           "that were all rate-limited retries of valid DOIs. Only a 404 counts.", ""]
    if broken:
        out += ["## Broken DOIs", "",
                "These come from upstream records unless marked otherwise. A link that "
                "404s is worse than no link.", "",
                "| DOI | HTTP |", "| --- | --- |"]
        for d, e in sorted(broken.items()):
            out.append(f"| `{cell(d)}` | {cell(e.get('http', '?'))} |")
        out.append("")
    if upgraded:
        out += ["## Upgraded to the published version", "", "| Preprint | Published |",
                "| --- | --- |"]
        for d, pub in sorted(upgraded.items()):
            out.append(f"| `{cell(d)}` | [`{cell(pub)}`](https://doi.org/{pub}) |")
        out.append("")

    if not args.skip_curated_check:
        flagged = verify_curated(http)
        out += ["## Hand-written publications needing review", "",
                "A DOI can resolve and still be the wrong paper. This catalog shipped "
                "ChromBPNet pointing at \"The maize cis-regulatory landscape\" and "
                "i-cisTarget at a therapeutic-peptide database; both resolved fine. "
                "The check is a heuristic, so most rows below are benign: many correct "
                "papers do not carry the tool's name in their title (MAST's is "
                "\"Combining evidence using p-values\").", "",
                f"{len(flagged)} of the hand-written identifiers want a look.", "",
                "| Tool | Identifier | Flag | Title |", "| --- | --- | --- | --- |"]
        for name, val, why, title in flagged:
            out.append(f"| {cell(name)} | `{cell(val)}` | {cell(why)} | {cell(title, 90)} |")
        out.append("")
        print(f"hand-written publications flagged for review: {len(flagged)}")

    DOCS.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(out))
    print(f"-> {PUBMAP.name}, {REPORT}")


if __name__ == "__main__":
    main()
