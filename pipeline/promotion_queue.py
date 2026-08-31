"""The promotion queue: the candidates a human is asked to rule on.

One definition, in one place. The queue is the join of two conditions the scope
auditor reports separately - in scope, and actually software - and both are
needed: a paper announcing a wet-lab assay is in scope and is not a tool, and a
tool for a neighbouring field is software and is not in scope. Everything that
renders or consumes the queue imports `build`, because the last time a rule
about scope was written out by hand in more than one place the copies drifted
and roughly a third of the exclusions were wrong.
"""
from __future__ import annotations

import re
from pathlib import Path

from jsonio import read_json

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"
DECLINED = Path(__file__).resolve().parent.parent / "curation" / "literature-declined.yaml"


def absolute(url: str) -> str:
    """A repo field holds either owner/name or a full url. Normalise to a url.

    The stages disagree on purpose - layer 1 resolves to a slug, the abstract
    scraper keeps whatever the paper printed - so callers must not concatenate
    blindly. Doing that produced github.com/https://github.com/... on the
    review page for the 169 candidates that already had an absolute url.
    """
    if not url:
        return ""
    url = str(url).strip()
    return url if url.startswith("http") else "https://github.com/" + url.lstrip("/")


def _rows(name: str) -> list[dict]:
    path = RAW / f"{name}.json"
    return read_json(path)["list"] if path.exists() else []


def build() -> list[dict]:
    """Every candidate the auditor calls both in scope and software, ranked."""
    scope = {r["name"]: r for r in _rows("literature_scope")}
    cats = {r["name"]: r for r in _rows("literature_categories")}
    cand = {r["name"]: r for r in _rows("literature_candidates")}
    layer1 = {r["name"]: r for r in _rows("literature_promote")}
    resolved = {r["name"]: r for r in _rows("literature_resolved_repos")}
    fulltext = {r["name"]: r for r in _rows("literature_fulltext_urls")}

    out = []
    for name, s in scope.items():
        if not (s.get("in_scope") and s.get("is_software")):
            continue
        c = cats.get(name, {})
        k = cand.get(name, {})
        a = layer1.get(name) or resolved.get(name) or {}
        f = fulltext.get(name) or {}
        # A validated row links to the repository root, not to whatever deep url
        # the paper printed: layer 1 already resolved it to owner/name.
        if a.get("layer1") == "pass":
            repo = absolute(a.get("slug") or k.get("repo") or "")
        else:
            repo = absolute(k.get("repo") or a.get("slug") or "")
        code = repo or absolute(f.get("url") if f.get("code") else "")
        out.append({
            "name": name,
            "description": (k.get("description") or s.get("description") or "")[:300],
            "year": k.get("year") or s.get("year"),
            "journal": k.get("journal", ""),
            "doi": k.get("doi", ""),
            "pmid": k.get("pmid", ""),
            "citations": k.get("citations") or s.get("citations") or 0,
            "categories": c.get("categories") or [],
            "cat_confidence": c.get("cat_confidence", ""),
            "repo": repo,
            "code": code,
            "software_url": code or absolute(f.get("url") or ""),
            "layer1": a.get("layer1", ""),
            "layer1_why": (a.get("why") or "")[:160],
            "scope_confidence": s.get("confidence", ""),
            "scope_reason": (s.get("reason") or "")[:200],
        })
    out.sort(key=lambda r: (-(r["citations"] or 0), r["name"].lower()))
    return out


def slug_of(url: str) -> str:
    """owner/name for a GitHub url, empty for anything else."""
    m = re.search(r"github\.com/([^/#?]+/[^/#?]+)", absolute(url))
    return re.sub(r"\.git$", "", m.group(1)) if m else ""


if __name__ == "__main__":
    rows = build()
    n = lambda p: sum(1 for r in rows if p(r))
    print(f"promotion queue: {len(rows)}")
    print(f"  validated repo    : {n(lambda r: r['layer1'] == 'pass')}")
    print(f"  unverified url    : {n(lambda r: r['layer1'] != 'pass' and r['code'])}")
    print(f"  homepage only     : {n(lambda r: not r['code'] and r['software_url'])}")
    print(f"  nothing found     : {n(lambda r: not r['software_url'])}")
