#!/usr/bin/env python3
"""Stage 2f - read install routes off the tool's own repository page.

`discover_registries.py` finds a package by looking for one *named like* the
tool, which is weak evidence and deliberately gated behind a description match.
A README is better evidence entirely: a PyPI or bioconda badge on a project's
own repository is the project saying where it ships. MACS advertises PyPI and
Anaconda, pySCENIC advertises PyPI, RSAT advertises Anaconda, and none of that
reached the catalog because bio.tools does not record it.

**The trap is that a README also mentions other people's packages.** Galaxy tool
repositories say `pip install planemo`, which is the Galaxy development harness,
not the tool. Dependencies, CI helpers and "see also" links all look identical
to the project's own badge. So a route is only accepted when the package name
matches the tool name or its repository name; anything else is written to
docs/install-review.md for a human instead of being applied.

    python pipeline/resolve_installs.py [--limit N] [--refresh]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from config import CACHE, DATA, DOCS, GITHUB_API, user_agent
from mdutil import cell
from resolve_repos import norm

INSTALL_MAP = CACHE / "install_map.json"
REPORT = DOCS / "install-review.md"

# Each pattern yields the package name in group 1. Badge URLs and install
# commands are both covered, because projects use one or the other or both.
PATTERNS = {
    "pypi": [
        r"pypi\.(?:org|python\.org)/(?:project|pypi)/([A-Za-z0-9._-]+)",
        r"img\.shields\.io/pypi/[a-z]+/([A-Za-z0-9._-]+)",
        r"badge\.fury\.io/py/([A-Za-z0-9._-]+)",
        r"pip3?\s+install\s+(?:-{1,2}[A-Za-z][\w-]*\s+)*([A-Za-z0-9._][A-Za-z0-9._-]*)",
    ],
    "conda": [
        r"anaconda\.org/(?:bioconda|conda-forge)/([A-Za-z0-9._-]+)",
        r"img\.shields\.io/conda/[a-z]+/(?:bioconda|conda-forge)/([A-Za-z0-9._-]+)",
        r"(?:conda|mamba)\s+install\s+(?:-{1,2}[A-Za-z][\w-]*(?:\s+[^-\s]\S*)?\s+)*"
        r"([A-Za-z0-9._][A-Za-z0-9._-]*)",
    ],
    "cran": [
        r"cran\.r-project\.org/(?:web/)?packages?[/=]([A-Za-z0-9._]+)",
        r"install\.packages\(['\"]([A-Za-z0-9._]+)['\"]\)",
    ],
    "bioconductor": [
        r"bioconductor\.org/packages/(?:release/bioc/html/)?([A-Za-z0-9._]+)",
        r"BiocManager::install\(['\"]([A-Za-z0-9._]+)['\"]\)",
    ],
    "docker": [
        r"hub\.docker\.com/r/([A-Za-z0-9._-]+/[A-Za-z0-9._-]+)",
        r"docker\s+pull\s+([A-Za-z0-9._\-/]+)",
    ],
}
COMPILED = {reg: [re.compile(p, re.I) for p in pats] for reg, pats in PATTERNS.items()}

URL_FOR = {
    "pypi": "https://pypi.org/project/{}/",
    "conda": "https://anaconda.org/bioconda/{}",
    "cran": "https://cran.r-project.org/package={}",
    "bioconductor": "https://bioconductor.org/packages/{}/",
    "docker": "https://hub.docker.com/r/{}",
}

# Package names that are never the tool: build tooling, dependencies and the
# Galaxy development harness that every Galaxy tool repository mentions.
NOT_THE_TOOL = {
    "planemo", "pip", "setuptools", "wheel", "numpy", "scipy", "pandas",
    "matplotlib", "cython", "pytest", "tox", "conda", "mamba", "python",
    "r-base", "bioconductor", "biocmanager", "devtools", "remotes",
    "requirements", "txt", "git", "docker", "jupyter", "notebook", "torch",
    "tensorflow", "scikit-learn", "sklearn", "anaconda", "miniconda",
}


def github_token() -> str:
    """Prefer an explicit token, fall back to whatever `gh auth login` stored."""
    for var in ("GITHUB_TOKEN", "GH_TOKEN"):
        if os.environ.get(var):
            return os.environ[var]
    try:
        out = subprocess.run(["gh", "auth", "token"], capture_output=True,
                             text=True, timeout=10)
        if out.returncode == 0:
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return ""


def slug_of(repo_url: str) -> str:
    m = re.match(r"https?://(?:www\.)?github\.com/([^/]+/[^/#?]+)", repo_url or "")
    return m.group(1).rstrip("/").removesuffix(".git") if m else ""


def fetch_readme(session: requests.Session, slug: str) -> str:
    try:
        r = session.get(f"{GITHUB_API}/repos/{slug}/readme", timeout=25,
                        headers={"Accept": "application/vnd.github.raw+json"})
    except requests.RequestException:
        return ""
    if r.status_code == 403 and "rate limit" in r.text.lower():
        time.sleep(5)
        return ""
    return r.text if r.status_code == 200 else ""


def routes_in(readme: str) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for registry, patterns in COMPILED.items():
        names = []
        for rx in patterns:
            for m in rx.finditer(readme):
                pkg = m.group(1).strip().strip(".,;:'\"")
                # `pip install -r requirements.txt` and `pip install --editable .`
                # both put a flag in group 1. So does a bare version pin.
                if pkg.startswith("-") or pkg[:1].isdigit():
                    continue
                # `pip install -r requirements.txt` names a file, not a package.
                if pkg.lower().endswith((".txt", ".yml", ".yaml", ".cfg",
                                         ".toml", ".lock", ".in")):
                    continue
                # A registry-qualified image (ghcr.io/..., quay.io/...) is not
                # on Docker Hub, and pretending otherwise fabricates a URL that
                # 404s. Bismark's README is the case: it ships via ghcr.io.
                if registry == "docker" and "." in pkg.split("/")[0]:
                    continue
                if pkg and pkg.lower() not in NOT_THE_TOOL and len(pkg) > 1:
                    names.append(pkg)
        if names:
            found[registry] = list(dict.fromkeys(names))
    return found


def belongs_to(pkg: str, tool_name: str, slug: str) -> bool:
    """Is this package plausibly the tool itself, rather than a dependency?

    Accepts a match against the tool's name or its repository name, with the
    same small-suffix tolerance `resolve_repos.validate()` uses ("weblogo" vs
    "weblogo3"). A Docker image is matched on its final path segment.
    """
    candidate = norm(pkg.split("/")[-1])
    if not candidate:
        return False
    for reference in (norm(tool_name), norm(slug.split("/")[-1])):
        if not reference:
            continue
        if candidate == reference:
            return True
        if reference in candidate and len(candidate) <= len(reference) + 3:
            return True
        if candidate in reference and len(reference) <= len(candidate) + 3:
            return True
    return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int)
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    catalog = json.loads((DATA / "catalog.json").read_text())
    cache = {}
    if INSTALL_MAP.exists() and not args.refresh:
        try:
            cache = json.loads(INSTALL_MAP.read_text())
        except ValueError:
            cache = {}

    targets = []
    for tool in catalog["tools"]:
        slug = slug_of(tool.get("repo_url", ""))
        if slug and tool["id"] not in cache:
            targets.append((tool["id"], tool["name"], slug))
    if args.limit:
        targets = targets[:args.limit]

    token = github_token()
    print(f"{len(targets)} repositories to read"
          f" ({'authenticated' if token else 'UNAUTHENTICATED, 60/hour'})")
    if not targets:
        write_report(cache, catalog)
        return

    session = requests.Session()
    session.headers.update({"User-Agent": user_agent()})
    if token:
        session.headers["Authorization"] = f"Bearer {token}"

    def work(item):
        tool_id, name, slug = item
        readme = fetch_readme(session, slug)
        accepted, held = {}, {}
        for registry, packages in routes_in(readme).items():
            for pkg in packages:
                if belongs_to(pkg, name, slug):
                    accepted[registry] = URL_FOR[registry].format(pkg)
                    break
            else:
                held[registry] = packages[:3]
        return tool_id, {"name": name, "slug": slug, "accepted": accepted,
                         "held": held, "readme": bool(readme)}

    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for fut in as_completed([pool.submit(work, t) for t in targets]):
            tool_id, result = fut.result()
            cache[tool_id] = result
            done += 1
            if done % 100 == 0:
                print(f"  {done}/{len(targets)}")
                INSTALL_MAP.write_text(json.dumps(cache, indent=1, sort_keys=True))
    INSTALL_MAP.parent.mkdir(parents=True, exist_ok=True)
    INSTALL_MAP.write_text(json.dumps(cache, indent=1, sort_keys=True))

    got = sum(1 for v in cache.values() if v["accepted"])
    held = sum(1 for v in cache.values() if v["held"] and not v["accepted"])
    print(f"install routes accepted for {got} tools; {held} more found only "
          "package names that do not match the tool")
    write_report(cache, catalog)
    print(f"-> {REPORT.relative_to(DOCS.parent)}")


def write_report(cache: dict, catalog: dict) -> None:
    by_registry = Counter(r for v in cache.values() for r in v["accepted"])
    held = {k: v for k, v in cache.items() if v["held"] and not v["accepted"]}
    out = [
        "# Install routes read from repository READMEs",
        "",
        f"Generated by `make installs`. {len(cache)} repositories read.",
        "",
        "A PyPI or bioconda badge on a project's own repository is the project "
        "stating where it ships, which is better evidence than finding a "
        "package that merely shares its name. This stage reads that, and it is "
        "how MACS, pySCENIC and RSAT gained install links bio.tools does not "
        "record.",
        "",
        "| Registry | Tools |",
        "| --- | ---: |",
    ]
    for registry, n in by_registry.most_common():
        out.append(f"| {registry} | {n} |")
    out += [
        "",
        f"## Held for review ({len(held)})",
        "",
        "A README names a package here, but the package name does not match the "
        "tool or its repository, so it is more likely a dependency than the "
        "tool itself. Galaxy tool repositories are the clearest case: they all "
        "say `pip install planemo`, which is the Galaxy development harness. "
        "Promote a row by adding the link to `curation/overlay.yaml`.",
        "",
        "| Tool | Repository | Package names found |",
        "| --- | --- | --- |",
    ]
    for tool_id, v in sorted(held.items())[:200]:
        names = "; ".join(f"{r}: {', '.join(p)}" for r, p in v["held"].items())
        out.append(f"| {cell(v['name'])} | {cell(v['slug'])} | {cell(names)} |")
    out.append("")
    REPORT.write_text("\n".join(out))


if __name__ == "__main__":
    main()
