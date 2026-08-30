#!/usr/bin/env python3
"""Stage 1e - turn literature candidates into seeds.yaml entries.

The literature route finds tools the registries do not index, but promoting one
has been entirely manual: read docs/literature-discovery.md, decide, retype the
entry. This stage does the checkable parts and leaves the judgement.

Three layers, cheapest first, each independently useful:

  1. VALIDATE THE REPOSITORY (deterministic, no key, no model). The paper's own
     abstract names a code url, so unlike the registry route there is nothing to
     guess - but a stated url still has to be the tool's own. Reuses
     resolve_repos.validate(), whose rule is that a matching name is necessary
     and never sufficient: the repo must share content words with the paper.
  2. CATEGORISE (model). `categories` is required by build.py and is the one
     field a human currently has to supply.
  3. MIRROR CHECK (a second opinion). Whether the tool is in scope at all. A
     rule cannot do this: CellCall is "ligand-receptor and transcription factor
     activity for cell-cell communication", which classify() admits on the
     phrase "transcription factor" while a reader sees a cell-communication
     tool. Reviewed by hand, it was the one rejection in the first 14.

Layers 2 and 3 decide nothing on their own: disagreement goes to a human, in
keeping with verify_additions.py - the bar for adding stays lower than the bar
for removing, because a wrongly included tool is visible and reportable while a
wrongly excluded one is invisible.

    python pipeline/promote_literature.py --layer1 [--only NAME] [--limit N]
"""
from __future__ import annotations

import argparse
import json

import requests

from config import CACHE, DATA, DOCS, RAW, user_agent
from jsonio import read_json, write_json
from resolve_repos import clean_slug, github_meta, norm, validate
from enrich import github_token

CANDIDATES = RAW / "literature_candidates.json"
VERDICTS = RAW / "literature_promote.json"
REPOMAP = CACHE / "repo_map.json"


def load_candidates(only: str | None, limit: int) -> list[dict]:
    blob = read_json(CANDIDATES)
    rows = blob["list"] if isinstance(blob, dict) and "list" in blob else blob
    rows = [r for r in rows if not r.get("known") and r.get("repo")]
    if only:
        rows = [r for r in rows if r["name"].lower() == only.lower()]
    rows.sort(key=lambda r: -(r.get("citations") or 0))
    return rows[:limit] if limit else rows


def layer1(rows: list[dict]) -> list[dict]:
    """Validate each stated repository against the paper's own description."""
    http = requests.Session()
    http.headers.update({"User-Agent": user_agent()})
    token = github_token()
    cache = json.loads(REPOMAP.read_text()) if REPOMAP.exists() else {}
    gh_cache = cache.setdefault("_gh_meta", {})

    out = []
    for r in rows:
        slug = clean_slug(r["repo"])
        rec = {"name": r["name"], "repo": r["repo"], "slug": slug,
               "citations": r.get("citations"), "year": r.get("year"),
               "doi": r.get("doi"), "pmid": r.get("pmid"),
               "description": r.get("description")}
        if not slug:
            # Bioconductor and CRAN urls are landing pages, not repositories.
            # Bioconductor and CRAN urls identify a package, not a repository,
            # so there is nothing here to validate against. Printed rather than
            # dropped silently: an invisible skip reads as a candidate that was
            # never seen.
            rec |= {"layer1": "skip", "why": "package landing page, not a repository"}
            out.append(rec)
            print(f"  skip  {r['name'][:22]:24s} {rec['why']}", flush=True)
            continue
        meta = github_meta(http, slug, token, gh_cache)
        if meta is None:
            rec |= {"layer1": "fail", "why": "repository not reachable (404 or private)"}
        else:
            ok, why = validate(r, slug, meta, source="abstract")
            # validate() is tuned for a repo we GUESSED, from a name search or a
            # registry, where the link is a hypothesis. Here the paper's own
            # abstract states the url, which is the author asserting it. With a
            # name match that is two independent confirmations, and demanding
            # shared vocabulary on top of it rejects correct repos whose
            # description is merely terse: epiGBS reads "Code for working with
            # epiGBS data", STARE "TF analysis from epigenetic and Hi-C data".
            # No name match is a different matter and still held: QuASAR-MPRA
            # points into github.com/piquelab/QuASAR/tree/master/mpra, a
            # subdirectory of a larger repo, which a human should see.
            if not ok and meta.get("description"):
                tn, rn = norm(r["name"]), norm(slug.split("/")[-1])
                if tn == rn or (tn in rn and len(rn) <= len(tn) + 3):
                    ok, why = True, f"author-stated url + name match ({why})"
            rec |= {"layer1": "pass" if ok else "hold", "why": why,
                    "stars": meta.get("stars"), "archived": meta.get("archived"),
                    "repo_description": meta.get("description")}
            if "/tree/" in r["repo"] or "/blob/" in r["repo"]:
                rec["note"] = "url points inside a larger repository, not at its root"
        out.append(rec)
        print(f"  {rec['layer1']:5s} {r['name'][:22]:24s} {rec.get('why','')[:64]}", flush=True)
    REPOMAP.write_text(json.dumps(cache, indent=1))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--layer1", action="store_true", help="validate repositories only")
    ap.add_argument("--only", help="a single candidate, by name")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    rows = load_candidates(args.only, args.limit)
    print(f"{len(rows)} candidates with a stated code url")
    if not args.layer1:
        print("nothing to do: pass --layer1 (layers 2 and 3 are not wired yet)")
        return
    verdicts = layer1(rows)
    write_json(VERDICTS, {"count": len(verdicts), "list": verdicts})
    tally = {}
    for v in verdicts:
        tally[v["layer1"]] = tally.get(v["layer1"], 0) + 1
    print("\n" + "  ".join(f"{k}={v}" for k, v in sorted(tally.items())))
    print(f"-> {VERDICTS}")


if __name__ == "__main__":
    main()
