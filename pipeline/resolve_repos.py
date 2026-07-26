#!/usr/bin/env python3
"""Stage 2c - find source repositories that bio.tools does not record.

bio.tools stores whatever links a submitter supplied, which for older entries is
often just an institutional homepage. WebLogo is the clearest case: its record
carries only a Berkeley URL, while the source lives at gecrooks/weblogo and is
published on PyPI.

Four sources are tried, cheapest and most reliable first:

  bioconda    recipes/<name>/meta.yaml, a curated field maintained by packagers
  bioconductor  the package DESCRIPTION's URL / BugReports fields
  pypi        project_urls and home_page for a package of the same name
  homepage    GitHub links on the tool's own page

**Every candidate is validated before it is accepted**, because guessing by name
is actively dangerous here. A bare PyPI lookup returns `katylava/memepy`, a meme
generator, for MEME; `shyal/vulcan`, a terminal flashcard app, for vulcan; and
an unrelated personal project for GREAT. Three false positives in a five-tool
probe. A wrong repository link is the same class of error as a wrong DOI: it
looks fine and quietly misinforms.

Acceptance needs either an exact name match or real textual agreement between
the repository and the tool. Anything weaker is written to docs/repo-review.md
as a proposal rather than applied.

    python pipeline/resolve_repos.py [--limit N] [--refresh]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date

import requests

from config import CACHE, DOCS, RAW
from jsonio import read_json
from mdutil import cell

ENRICHED = RAW / "enriched.json.gz"
REPOMAP = CACHE / "repo_map.json"
REPORT = DOCS / "repo-review.md"

GH = re.compile(r"github\.com/([A-Za-z0-9._-]+)/([A-Za-z0-9._-]+)")
BAD_OWNER = {"orgs", "topics", "search", "about", "features", "sponsors", "site",
             "apps", "marketplace", "readme", "explore", "login", "join"}
# Generic English and software words only. Domain words are deliberately NOT
# here: "sequence", "motif", "genome" and "binding" are exactly what
# distinguishes a sequence-logo generator from a meme generator. Adding them to
# this list was enough to reject gecrooks/weblogo, the correct answer.
STOP = {"the", "a", "an", "for", "and", "of", "to", "in", "with", "from", "on", "by",
        "is", "are", "it", "its", "this", "that", "can", "you", "your", "we", "our",
        "using", "used", "use", "based", "tool", "tools", "software", "package",
        "library", "framework", "application", "program", "implementation",
        "simple", "fast", "easy", "new", "open", "source", "code", "project",
        "python", "java", "version", "web", "online", "server", "designed", "make",
        "provides", "allows", "support", "supports"}


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def tokens(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]{3,}", (s or "").lower()) if w not in STOP}


def clean_slug(url: str) -> str | None:
    m = GH.search(url or "")
    if not m:
        return None
    owner, repo = m.group(1), re.sub(r"\.git$", "", m.group(2))
    if owner.lower() in BAD_OWNER or not repo:
        return None
    return f"{owner}/{repo}"


# ---------------------------------------------------------------------------
# candidate sources
# ---------------------------------------------------------------------------
def from_bioconda(http, name) -> tuple[str, str] | None:
    for variant in dict.fromkeys([name, name.lower(), norm(name)]):
        try:
            r = http.get("https://raw.githubusercontent.com/bioconda/bioconda-recipes"
                         f"/master/recipes/{variant}/meta.yaml", timeout=20)
        except requests.RequestException:
            continue
        if r.status_code == 200:
            for field in ("dev_url", "home"):
                m = re.search(rf"{field}:\s*\S*?({GH.pattern})", r.text)
                if m:
                    slug = clean_slug(m.group(1))
                    if slug:
                        return slug, "bioconda"
            slug = clean_slug(r.text)
            if slug:
                return slug, "bioconda"
    return None


def from_bioconductor(http, name) -> tuple[str, str] | None:
    try:
        r = http.get(f"https://bioconductor.org/packages/release/bioc/html/{name}.html",
                     timeout=20)
    except requests.RequestException:
        return None
    if r.status_code != 200:
        return None
    slug = clean_slug(r.text)
    return (slug, "bioconductor") if slug else None


def from_pypi(http, name) -> tuple[str, str, str] | None:
    try:
        r = http.get(f"https://pypi.org/pypi/{name}/json", timeout=20)
    except requests.RequestException:
        return None
    if r.status_code != 200:
        return None
    info = r.json().get("info") or {}
    urls = [info.get("home_page") or ""] + list((info.get("project_urls") or {}).values())
    for u in urls:
        slug = clean_slug(u or "")
        if slug:
            return slug, "pypi", (info.get("summary") or "")
    return None


def from_homepage(http, url) -> list[tuple[str, str]]:
    """Every distinct GitHub link on the page, not just the first.

    Taking the first match makes the result depend on page layout: a docs site
    with an Angular badge in its header yielded `angular/angular` for PomBase's
    motif search. Collecting all of them lets validation choose, and a page
    rarely carries more than a handful.
    """
    if not url or "github.com" in url:
        return []
    try:
        r = http.get(url, timeout=8, allow_redirects=True)
    except requests.RequestException:
        return []
    if r.status_code != 200 or "html" not in r.headers.get("Content-Type", ""):
        return []
    out, seen = [], set()
    for m in GH.finditer(r.text[:400_000]):
        slug = clean_slug(m.group(0))
        if slug and slug not in seen:
            seen.add(slug)
            out.append((slug, "homepage"))
        if len(out) >= 8:
            break
    return out


# ---------------------------------------------------------------------------
def validate(tool: dict, slug: str, gh_meta: dict | None, extra_text: str = "") -> tuple[bool, str]:
    """Decide whether `slug` really is this tool's repository.

    **A matching name is necessary but never sufficient.** An earlier version
    accepted exact name matches outright and was right less than half the time:
    tool names in this field are short and generic, so `Match` resolved to a
    text-matching library, `SEA` to an RPC framework, `CREME` to an online
    machine-learning package and `PINES` to somebody's utility scripts.

    Even a domain-scoped registry does not rescue it. bioconda carries a recipe
    named `medusa` for a genome scaffolder, while this catalog's MEDUSA learns
    motif models of TF binding sites. Two real bioinformatics tools, one name.

    So the repository has to say something recognisably about the same subject:
    at least two content words shared with the tool's description. A repository
    with no description at all cannot be verified and is held for review, not
    accepted on the strength of its name.
    """
    repo_name = slug.split("/")[-1]
    name_ok = norm(repo_name) == norm(tool["name"]) or norm(tool["name"]) in norm(repo_name)

    repo_text = " ".join(filter(None, [
        (gh_meta or {}).get("description") or "",
        " ".join((gh_meta or {}).get("topics") or []),
        (gh_meta or {}).get("readme") or "",
        extra_text,
    ])).strip()
    if not repo_text:
        return False, "repo has no description; cannot verify beyond the name"

    shared = tokens(tool.get("description") or "") & tokens(repo_text)
    evidence = f"{len(shared)} shared terms ({', '.join(sorted(shared)[:4])})"
    if name_ok and len(shared) >= 2:
        return True, f"name match + {evidence}"
    if len(shared) >= 4:
        return True, evidence
    if name_ok:
        return False, f"name matches but only {evidence}"
    return False, f"no name match and only {evidence}"


def github_meta(http, slug, token, cache) -> dict | None:
    if slug in cache:
        return cache[slug]
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        r = http.get(f"https://api.github.com/repos/{slug}", headers=headers, timeout=25)
    except requests.RequestException:
        return None
    if r.status_code != 200:
        cache[slug] = None
        return None
    d = r.json()
    meta = {"description": d.get("description"), "topics": d.get("topics") or [],
            "stars": d.get("stargazers_count"), "archived": d.get("archived"),
            "full_name": d.get("full_name"), "readme": ""}
    # Many research repos leave the description blank. The opening of the README
    # is usually enough to tell a motif finder from an RPC framework.
    if not meta["description"]:
        try:
            rr = http.get(f"https://api.github.com/repos/{slug}/readme",
                          headers={**headers, "Accept": "application/vnd.github.raw"},
                          timeout=20)
            if rr.status_code == 200:
                meta["readme"] = rr.text[:1200]
        except requests.RequestException:
            pass
    cache[slug] = meta
    return cache[slug]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()

    from enrich import github_token
    token = github_token()

    tools = [t for t in read_json(ENRICHED)["list"] if not t.get("_repo_slug")]
    tools = tools[: args.limit] if args.limit else tools
    print(f"{len(tools)} records without a repository; searching four sources")

    found = json.loads(REPOMAP.read_text()) if REPOMAP.exists() and not args.refresh else {}
    gh_cache: dict = {}
    lock = threading.Lock()
    done = [0]

    def resolve(tool):
        bid = tool["biotoolsID"]
        with lock:
            if bid in found:
                return None
        http = requests.Session()
        http.headers.update({"User-Agent": "awesome-regulatory-genomics/1.0"})
        name = tool["name"]
        # Try several spellings: bio.tools display names carry spaces, hyphens
        # and capitalisation that package registries do not.
        variants = list(dict.fromkeys([name, name.lower(), name.replace(" ", ""),
                                       name.replace(" ", "-").lower(), norm(name)]))
        candidates = []
        for fn in ([lambda v=v: from_bioconda(http, v) for v in variants[:3]]
                   + [lambda v=v: from_bioconductor(http, v) for v in variants[:2]]
                   + [lambda v=v: from_pypi(http, v) for v in variants[:3]]
                   + [lambda: from_homepage(http, tool.get("homepage"))]):
            try:
                got = fn()
            except Exception:                                # noqa: BLE001
                got = None
            if not got:
                continue
            candidates.extend(got if isinstance(got, list) else [got])
        result = None
        for cand in candidates:
            slug, source = cand[0], cand[1]
            extra = cand[2] if len(cand) > 2 else ""
            meta = github_meta(http, slug, token, gh_cache)
            if meta is None:
                continue
            ok, why = validate(tool, slug, meta, extra)
            entry = {"slug": slug, "source": source, "reason": why,
                     "accepted": ok, "stars": meta.get("stars"),
                     "repo_desc": (meta.get("description") or "")[:140],
                     "tool_desc": (tool.get("description") or "")[:140],
                     "name": name}
            if ok:
                result = entry
                break
            result = result or entry
        time.sleep(0.1)
        with lock:
            done[0] += 1
            if result:
                found[bid] = result
            if done[0] % 100 == 0:
                print(f"  {done[0]}/{len(tools)}  accepted so far: "
                      f"{sum(1 for v in found.values() if v['accepted'])}", flush=True)
                REPOMAP.parent.mkdir(parents=True, exist_ok=True)
                REPOMAP.write_text(json.dumps(found, indent=1, sort_keys=True))
        return result

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for fut in as_completed([pool.submit(resolve, t) for t in tools]):
            try:
                fut.result()
            except Exception as exc:                         # noqa: BLE001
                print(f"    ! {exc}", file=sys.stderr)

    REPOMAP.parent.mkdir(parents=True, exist_ok=True)
    REPOMAP.write_text(json.dumps(found, indent=1, sort_keys=True))

    accepted = {k: v for k, v in found.items() if v["accepted"]}
    rejected = {k: v for k, v in found.items() if not v["accepted"]}
    print(f"\naccepted {len(accepted)}, held for review {len(rejected)}")

    out = ["# Repository resolution review", "",
           f"Generated {date.today().isoformat()} by `make repos`.", "",
           "bio.tools records whatever links a submitter supplied, which for older "
           "entries is often only an institutional homepage. This stage looks for the "
           "source repository in bioconda recipes, Bioconductor DESCRIPTION fields, "
           "PyPI metadata and the tool's own homepage.", "",
           "**Every candidate is validated.** Guessing by name alone is dangerous: a "
           "bare PyPI lookup returns `katylava/memepy` for MEME and `shyal/vulcan`, a "
           "flashcard app, for vulcan. A wrong repository link is the same class of "
           "error as a wrong DOI, so a candidate is accepted only on an exact name "
           "match or real vocabulary overlap between repository and tool.", "",
           f"- **{len(accepted)} accepted** and applied to the catalog.",
           f"- **{len(rejected)} held for review** below; none of these are applied.", ""]
    if rejected:
        out += ["## Held for review", "",
                "| Tool | Candidate | Source | Why it was not accepted | Repo description |",
                "| --- | --- | --- | --- | --- |"]
        for v in sorted(rejected.values(), key=lambda x: x["name"].lower()):
            out.append(f"| {cell(v['name'])} | [{cell(v['slug'])}](https://github.com/{v['slug']}) "
                       f"| {cell(v['source'])} | {cell(v['reason'], 60)} | {cell(v['repo_desc'], 80)} |")
        out.append("")

    DOCS.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(out))
    print(f"-> {REPOMAP.name}, {REPORT}")


if __name__ == "__main__":
    main()
