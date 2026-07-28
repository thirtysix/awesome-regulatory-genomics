#!/usr/bin/env python3
"""Stage 4 - render the catalog into README.md and the browsable site.

The README carries the curated tier: enough to be useful at a glance, short
enough to read. The full catalog lives in docs/index.html, which is a single
self-contained page with client-side search and faceting - no build step, no
backend, works from a file:// URL as well as GitHub Pages.

    python pipeline/render.py
"""
from __future__ import annotations

import json
import re
from datetime import date
from urllib.parse import urlparse

from config import (CATEGORIES, CATEGORY_DESC, CATEGORY_LABEL, CODE_HOSTS, DATA,
                    DOCS, ROOT)

CATALOG = DATA / "catalog.json"
README = ROOT / "README.md"
INDEX = DOCS / "index.html"
DATA_JS = DOCS / "catalog.js"

REPO_SLUG = "thirtysix/awesome-regulatory-genomics"
SITE = "https://thirtysix.github.io/awesome-regulatory-genomics/"


def fmt_int(n) -> str:
    try:
        return f"{int(n):,}"
    except (TypeError, ValueError):
        return ""


def _norm_url(u: str) -> str:
    return (u or "").rstrip("/").lower().replace("://www.", "://")


def site_url(t: dict) -> str:
    """The tool's own website, when that is something other than its repository.

    bio.tools' ``homepage`` is populated for every record, but for a third of
    them it simply points at GitHub, so showing it verbatim would give a column
    of 1,800 links that mostly duplicate the Code column. A "site" is therefore
    a homepage that is neither the source repository nor any other code host:
    the project page, web server or database front end you would cite. That
    makes the column worth sorting and filtering on - "web-only resource" and
    "repo, no site" become answerable questions.
    """
    homepage = t.get("homepage") or ""
    if not homepage:
        return ""
    host = urlparse(homepage).netloc.lower().removeprefix("www.")
    if host in CODE_HOSTS:
        return ""
    if _norm_url(homepage) == _norm_url(t.get("repo_url")):
        return ""
    return homepage


def slug(label: str) -> str:
    """GitHub's heading-anchor rule: lowercase, drop punctuation, spaces to hyphens."""
    return re.sub(r"\s", "-", re.sub(r"[^\w\s-]", "", label.lower()))


def plural(n: int, word: str) -> str:
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def tool_line(t: dict) -> list[str]:
    """One README entry, as two lines.

    GitHub renders a README in a fixed-width column that a repository cannot
    widen, so the layout has to earn its space rather than ask for more.
    Putting the links on their own indented line keeps the description on a
    single unbroken line at typical widths, and gives the eye a predictable
    place to find "code / bio.tools / paper" for every entry.
    """
    label = t["name"]
    href = t["homepage"] or t["repo_url"] or t["biotools_url"]
    head = f"**[{label}]({href})**" if href else f"**{label}**"

    links = []
    if t["repo_url"]:
        links.append(f"[code]({t['repo_url']})")
    if t["biotools_url"]:
        links.append(f"[bio.tools]({t['biotools_url']})")
    if t["publication"]:
        ident = t["publication"]
        if ident.startswith("pmid:"):
            links.append(f"[paper](https://pubmed.ncbi.nlm.nih.gov/{ident[5:]}/)")
        elif ident.startswith("doi:"):
            label = "preprint" if t.get("publication_is_preprint") else "paper"
            links.append(f"[{label}](https://doi.org/{ident[4:]})")

    signals = []
    if t.get("repo_stars"):
        signals.append(f"{fmt_int(t['repo_stars'])} stars")
    if t.get("citations"):
        signals.append(f"{fmt_int(t['citations'])} cites")
    if t.get("repo_archived"):
        signals.append("archived")

    desc = (t.get("featured") or t.get("description") or "").rstrip(".")
    rows = [f"- {head}: {desc}"]
    meta = " · ".join(links)
    if signals:
        meta += (" · " if meta else "") + f"`{' | '.join(signals)}`"
    if meta:
        rows.append(f"  <sub>{meta}</sub>")
    return rows


def render_readme(catalog: dict) -> str:
    tools = catalog["tools"]
    meta = catalog["meta"]
    by_cat: dict[str, list] = {k: [] for k, _, _ in CATEGORIES}
    for t in tools:
        for c in t["categories"]:
            by_cat[c].append(t)

    total = len(tools)
    with_repo = meta["with_repo"]
    with_site = sum(1 for t in tools if site_url(t))
    with_pkg = sum(1 for t in tools if t.get("_registries"))
    dead_links = sum(1 for t in tools
                     if t.get("homepage_status") == "dead" or t.get("repo_status") == "dead")
    with_year = sum(1 for t in tools if t.get("year"))
    featured_n = meta["featured"]

    out = []
    A = out.append

    A("# Awesome Regulatory Genomics")
    A("")
    # The awesome.re badge is the one awesome.md asks for, unmodified and next
    # to the title. It marks the list as following those guidelines; it is not a
    # claim of inclusion in the sindresorhus/awesome index.
    A("[![Awesome](https://awesome.re/badge.svg)](https://awesome.re) "
      f"[![Tools](https://img.shields.io/badge/tools-{total}-blue)]({SITE}) "
      "[![License: CC BY 4.0](https://img.shields.io/badge/data-CC--BY--4.0-lightgrey)](LICENSE-DATA) "
      f"[![Updated](https://img.shields.io/badge/updated-"
      f"{meta['generated'].replace('-', '--')}-brightgreen)](#)")
    A("")
    A("A catalog of tools, databases and methods for **transcription-factor binding, "
      "sequence motifs, regulatory elements, chromatin and gene-regulatory networks**.")
    A("")
    A(f"**[Browse and search all {total} tools →]({SITE})**. Filter by category, "
      "tool type, language, repository activity, and per column by name, "
      "description, links, package availability, stars, citations and year. "
      "The panel above the table charts publication year, repository activity, "
      "citations and stars **for whatever is currently filtered**, so \"when "
      "were the peak callers written, and are they still maintained\" is one "
      "click rather than a download.")
    A("")
    A("This list is *generated and then curated*. A reproducible pipeline harvests "
      "[bio.tools](https://bio.tools), resolves source repositories, and pulls citation "
      "counts and repository activity; a hand-written overlay adds tools bio.tools does "
      "not index and promotes the entries below. Everything is rebuildable with "
      "`make all`; see [How this list is built](#how-this-list-is-built).")
    A("")

    A("## Contents")
    A("")
    for key, label, _ in CATEGORIES:
        n = len(by_cat[key])
        if n:
            A(f"- [{label}](#{slug(label)}), {plural(n, 'tool')}")
    A("- [How this list is built](#how-this-list-is-built)")
    A("- [Coverage and known gaps](#coverage-and-known-gaps)")
    A("- [Contributing](#contributing)")
    A("")

    for key, label, _ in CATEGORIES:
        entries = by_cat[key]
        if not entries:
            continue
        picks = [t for t in entries if t.get("featured")]
        picks.sort(key=lambda t: -int(t["citations"] or 0))
        A(f"## {label}")
        A("")
        A(f"*{CATEGORY_DESC[key]}*")
        A("")
        if picks:
            for t in picks:
                out.extend(tool_line(t))
            A("")
        rest = len(entries) - len(picks)
        if rest > 0:
            more = "more in this category" if picks else "in this category"
            A(f"<sub>[+ {rest} {more} →]({SITE}?category={key})</sub>"
              if picks else f"<sub>[{rest} tools in this category →]({SITE}?category={key})</sub>")
            A("")

    A("## Running the pipeline")
    A("")
    A("```bash")
    A("pip install -r requirements.txt")
    A("cp .env.example .env        # optional; see below")
    A("make test                   # unit-test the scope and linking rules")
    A("make curate                 # rebuild README and site from committed data")
    A("make all                    # re-select, enrich, resolve links, rebuild")
    A("make serve PORT=8000        # preview the site locally")
    A("```")
    A("")
    A("`make test` needs `pip install -r requirements-dev.txt` and runs offline. "
      "It covers the three functions that decide the catalog's boundary, its "
      "repository links and its citation counts, using the real records that "
      "motivated each rule. Run it before changing "
      "[`pipeline/config.py`](pipeline/config.py): every regression this "
      "project has shipped came from loosening one of those rules, and the "
      "tests encode why each is written the way it is.")
    A("")
    A("`.env` holds two optional settings, both blank by default:")
    A("")
    A("- `CONTACT_EMAIL` identifies the client to the OpenAlex and Crossref "
      "*polite pools*, which give faster and more reliable service to callers "
      "that say who they are. Leave it unset and the pipeline omits the "
      "parameter rather than sending a placeholder, since a fake address there "
      "is worse than none.")
    A("- `DEEPINFRA_API_KEY` is needed only by the optional model stages "
      "(`make llm`, `make bench`, `make verify-additions`). Their results are "
      "cached and committed, so a normal build never asks for it.")
    A("")
    A("## How this list is built")
    A("")
    A("```")
    A("harvest.py        wide sweep of bio.tools (EDAM operation + free-text queries)")
    A("select_domain.py  tiered precision filter -> what is in scope")
    A("discover_registries.py  the same filter over Bioconductor and Galaxy,")
    A("                  for tools bio.tools does not index at all")
    A("enrich.py         resolve source repos, GitHub activity, OpenAlex citations")
    A("resolve_repos.py  find repos bio.tools omits (bioconda/PyPI/homepage), validated")
    A("resolve_pubs.py   upgrade preprint links to the published version, check DOIs")
    A("build.py          merge with curated seeds, assign categories, apply overlay")
    A("render.py         write README.md and the searchable site")
    A("audit_coverage.py measure recall against a hand-written benchmark")
    A("```")
    A("")
    A("**Harvesting and selection never call an LLM.** They are set membership on "
      "EDAM terms, compiled regex and API lookups, so the scope of the catalog is "
      "reproducible and every rule is readable in "
      "[`pipeline/config.py`](pipeline/config.py). Categories and descriptions are "
      "then refined by an *optional* model pass "
      "([`docs/llm-stage.md`](docs/llm-stage.md)) that writes to a review file "
      "merged below the hand-written overlay; `make build-strict` ignores it "
      "entirely and rebuilds on rules alone. Removing a record needs two different "
      "models to agree independently, and never overrides a hand-vetted entry. "
      "Additions get the mirror check from a third model "
      "([`docs/addition-review.md`](docs/addition-review.md)), which is how a "
      "name collision between the MEME Suite's MAST and the unrelated "
      "single-cell package of the same name was caught.")
    A("")
    A("Two design decisions are worth stating, because they are where most tool "
      "tables go wrong:")
    A("")
    A("**Recall and precision are separated.** bio.tools' `operation=` parameter is a "
      "fuzzy text match, not an ontology lookup. Quoting matters more than it should: "
      "`q=\"cis-regulatory\"` returns 107 records, while the same query unquoted returns "
      "about 3,500, matching \"cis\" *or* \"regulatory\". So the sweep is "
      "deliberately over-broad and precision is restored afterwards by filtering on the "
      "annotations a record actually carries.")
    A("")
    A("**EDAM annotations are not trusted on their own.** They are frequently wrong, and "
      "wrong in ways no query can anticipate: HOCOMOCO, a motif database, is filed under "
      "*Data handling*; SICER, a ChIP-seq peak caller, under *Sequence contamination "
      "filtering*; ChIP-Atlas, a data portal, under *Genome assembly*. Whole operations "
      "belong to another field: of the 204 records carrying *Peak detection*, roughly "
      "three in four are proteomics, metabolomics or NMR tools. Operations are therefore "
      "tiered. Seventeen specific terms admit a record on their own; five ambiguous ones "
      "that bio.tools also applies to protein motifs, RNA structure and orthology need a "
      "corroborating topic or text signal; and five that belong to a different field "
      "outright are documented in `REJECTED_OPERATIONS`, never queried and never able to "
      "admit anything. A text-match escape hatch recovers in-domain tools with no usable "
      "annotation at all. Every accepted record stores the rule that admitted it "
      "(`_select_reason`), and every rejected one is written to "
      "[`data/raw/rejected.json`](data/raw/rejected.json) so the boundary can be argued "
      "with rather than taken on trust.")
    A("")

    A("## Coverage and known gaps")
    A("")
    A(f"- **{total} tools**: {meta['from_biotools']} harvested from bio.tools, "
      f"{meta['curated_seeds']} added by hand because bio.tools does not index them.")
    A(f"- **{with_repo} ({with_repo/max(total,1):.0%}) have a resolvable source repository.** "
      "bio.tools rarely records one directly, so repositories are also recovered "
      "from Bioconductor, CRAN and PyPI metadata, from bioconda recipes and from "
      "links on the tool's own homepage. Every candidate is validated against the "
      "tool's description before it is used: matching on name alone resolves MEME "
      "to a meme generator and MEDUSA to a genome scaffolder that merely shares "
      "the name. Near-misses are listed in "
      "[`docs/repo-review.md`](docs/repo-review.md) rather than applied. "
      "Publication links get the same treatment in "
      "[`docs/link-check.md`](docs/link-check.md), which records every preprint "
      "upgraded to its published version and every DOI that does not resolve.")
    A("")
    origins = meta.get("repo_by_origin") or {}
    A("**If you maintain a tool listed here and its link is wrong, please say so.** "
      f"Of the {with_repo} links shown, {origins.get('recorded', 0)} are recorded "
      f"upstream, {origins.get('curated', 0)} are hand-verified and "
      f"{origins.get('inferred', 0)} are *inferred* from a homepage or a GitHub "
      "search. Inferred links are marked with a dotted underline on the "
      f"[catalog site]({SITE}) and carry a one-click report button; there are "
      "[issue templates](.github/ISSUE_TEMPLATE) for a wrong repository and for a "
      "wrong category, description or scope decision. Correcting the entry at "
      "[bio.tools](https://bio.tools) instead fixes it here on the next refresh, "
      "and for every other consumer of that registry.")
    A(f"- **{with_site} ({with_site/max(total,1):.0%}) have a website of their own**, "
      "meaning a project page, web server or database front end that is not just "
      "their source repository. The rest live on a code host alone. The catalog "
      f"site shows this as a sortable *Site* column, so \"web-only resource\" and "
      "\"code, no documentation site\" are both answerable questions.")
    A(f"- **{with_pkg} can be installed from a package registry** (Bioconductor, "
      "CRAN, PyPI, conda or Docker), shown as a sortable *Install* column. "
      "\"Can I install this today?\" is a more useful maintenance signal than a "
      "star count, and it is not a question bio.tools answers. A package is only "
      "linked when its description agrees with the tool's, never on a matching "
      "name: bioconda's `medusa` is a genome scaffolder, and this catalog's "
      "MEDUSA is a motif model.")
    A(f"- **{dead_links} links are known to be dead** and are struck through on the "
      "catalog site rather than quietly left to disappoint. Every homepage is "
      "checked (`make check-links`), which matters because nearly half this "
      "catalog has no repository, only a homepage, and academic URLs rot. "
      "Only a 404 or 410 counts: a timeout is as often a slow institutional "
      "host as a departed one, and 429 means the server is up and busy. The "
      "full grading is in [`docs/homepage-check.md`](docs/homepage-check.md).")
    A(f"- **{with_year} have a publication year**, recovered from OpenAlex where "
      "the registry did not record one.")
    A(f"- **{featured_n} tools are featured** in the curated sections above; the rest are "
      f"in the [full catalog]({SITE}).")
    A("")
    A("Honest limitations:")
    A("")
    A("- bio.tools skews toward tools with a publication and an ELIXIR-adjacent "
      "submitter. The sequence-to-function deep-learning literature is badly "
      "under-represented there; those entries come from `curation/seeds.yaml` and are "
      "necessarily incomplete. `make discover` widens this by running the same "
      "selection rules over registries that carry their own domain taxonomy "
      "(Bioconductor's `biocViews`, the Galaxy ToolShed), which is how tools like "
      "AlphaGenome, Cicero and Chromap reached this list; candidates land in "
      "[`docs/registry-discovery.md`](docs/registry-discovery.md) for review "
      "rather than being added automatically.")
    A("- Citation counts are the OpenAlex `cited_by_count` of a tool's **primary** "
      "publication only. Summing every linked publication, which is what the "
      "original dissertation script did, is badly wrong here: bio.tools attaches a suite's "
      "paper to each of its members, so the EMBOSS paper is linked to dozens of "
      "EMBOSS commands and the Bioconductor paper to 23 packages in this sweep, "
      "handing each member the whole suite's count. Where a primary publication is "
      "itself shared by three or more tools, no count is shown at all, because the "
      "member's own impact is genuinely unknown. Treat what remains as a rough "
      "popularity signal, not a quality measure.")
    A("- Categories are assigned by rule, then corrected by hand where wrong. The "
      "rules catch the systematic errors (bio.tools files orthology tools under "
      "*Phylogenetic footprinting* and mass-spectrometry tools under *Peak "
      "detection*), but a tail of individual mis-categorisations remains. Please "
      "open an issue, or see [`docs/llm-stage.md`](docs/llm-stage.md) for the "
      "optional classifier that targets exactly this tail.")
    A("- A tool being listed is not an endorsement, and the absence of a repository "
      "link often means the tool is web-only, not that it is unmaintained.")
    A("")
    A("Recall against a hand-written benchmark of standard resources is tracked in "
      "[`docs/coverage.md`](docs/coverage.md) and regenerated by `make audit`, so "
      "\"did it find the obvious things?\" is a number rather than an impression.")
    A("")

    A("## Contributing")
    A("")
    A("Additions, corrections and re-categorisations are welcome; see "
      "[CONTRIBUTING.md](CONTRIBUTING.md). Edit "
      "[`curation/seeds.yaml`](curation/seeds.yaml) or "
      "[`curation/overlay.yaml`](curation/overlay.yaml); never edit `README.md` or "
      "`data/catalog.*` directly, as both are regenerated.")
    A("")
    A("## Provenance")
    A("")
    A("This catalog began as a table in a doctoral dissertation on transcription-factor "
      "binding site prediction. That table and the scripts that produced it are kept "
      "in [`dissertation/`](dissertation/) for citation, edited only to redact five "
      "absolute working-directory paths; "
      "[`docs/provenance.md`](docs/provenance.md) documents how it was derived and what "
      "this catalog changes.")
    A("")
    A("## Licence")
    A("")
    A("Catalog data: [CC BY 4.0](LICENSE-DATA). Pipeline code: [MIT](LICENSE). "
      "Tool metadata originates from [bio.tools](https://bio.tools) (CC BY 4.0) and "
      "[OpenAlex](https://openalex.org) (CC0).")
    A("")
    return "\n".join(out)


# ---------------------------------------------------------------------------
HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Awesome Regulatory Genomics: catalog</title>
<meta name="description" content="Searchable catalog of __COUNT__ tools for transcription-factor binding, sequence motifs, regulatory elements, chromatin and gene-regulatory networks.">
<style>
:root{
  --bg:#ffffff; --fg:#1a1d21; --muted:#5c6570; --line:#e3e6ea; --accent:#1b6ac9;
  --chip:#f1f4f8; --chip-on:#1b6ac9; --chip-on-fg:#fff; --card:#fff; --warn:#a4551a;
  /* Data marks. One hue: bar length carries magnitude, so colour is not a
     second encoding of the same thing. Validated against this surface. */
  --series-1:#2a78d6; --grid:#e8ebee;
  --gh:url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27s1.36.09 2 .27c1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8z"/></svg>');
}
@media (prefers-color-scheme:dark){
  :root{ --bg:#14171a; --fg:#e6e9ec; --muted:#98a2ad; --line:#2a2f35; --accent:#6aa9f0;
         --chip:#21262c; --chip-on:#6aa9f0; --chip-on-fg:#101316; --card:#1a1e22; --warn:#e0a06a;
         --series-1:#3987e5; --grid:#262b31; }
}
:root[data-theme=light]{ --bg:#fff; --fg:#1a1d21; --muted:#5c6570; --line:#e3e6ea; --accent:#1b6ac9;
  --chip:#f1f4f8; --chip-on:#1b6ac9; --chip-on-fg:#fff; --card:#fff; --warn:#a4551a;
  --series-1:#2a78d6; --grid:#e8ebee; }
:root[data-theme=dark]{ --bg:#14171a; --fg:#e6e9ec; --muted:#98a2ad; --line:#2a2f35; --accent:#6aa9f0;
  --chip:#21262c; --chip-on:#6aa9f0; --chip-on-fg:#101316; --card:#1a1e22; --warn:#e0a06a;
  --series-1:#3987e5; --grid:#262b31; }
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
  font:15px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;}
a{color:var(--accent);text-decoration:none} a:hover{text-decoration:underline}
header{border-bottom:1px solid var(--line);padding:18px 20px;position:sticky;top:0;background:var(--bg);z-index:10}
.wrap{max-width:none;margin:0}
h1{font-size:19px;margin:0 0 3px} h1 a{color:inherit}
.sub{color:var(--muted);font-size:13px}
.controls{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px;align-items:center}
input[type=search],select{background:var(--card);color:var(--fg);border:1px solid var(--line);
  border-radius:7px;padding:8px 11px;font:inherit;font-size:14px}
input[type=search]{flex:1 1 300px;min-width:200px}
main{max-width:none;margin:0;padding:18px 24px 60px}
footer{max-width:110ch}   /* prose stays readable even when the table does not */
/* One grid cell per category, so the block is a tidy rack rather than a ragged
   wrap. Cells are wide enough for the longest label ("Peak annotation &
   differential binding") to sit on one line at desktop widths; narrower than
   that it wraps to two lines rather than truncating, since a clipped category
   name is worse than an uneven row. */
.chips{display:grid;grid-template-columns:repeat(auto-fit,minmax(238px,1fr));
  gap:6px;margin:0 0 14px}
.chip{background:var(--chip);border:1px solid var(--line);border-radius:8px;
  padding:5px 11px;font-size:12.5px;cursor:pointer;user-select:none;text-align:left;
  display:flex;align-items:center;gap:8px;min-height:30px;color:inherit;font-family:inherit}
.chip .lab{flex:1 1 auto;line-height:1.25}
.chip[aria-pressed=true]{background:var(--chip-on);color:var(--chip-on-fg);border-color:var(--chip-on)}
.chip .n{opacity:.65;font-variant-numeric:tabular-nums;flex:0 0 auto}
.count{color:var(--muted);font-size:13px;margin:0 0 10px}
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px}
table{border-collapse:collapse;width:100%;min-width:1120px;font-size:14px}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}
th{position:sticky;top:0;background:var(--bg);cursor:pointer;white-space:nowrap;
   font-weight:600;font-size:12.5px;letter-spacing:.02em;text-transform:uppercase;color:var(--muted)}
th:hover{color:var(--fg)} th .ar{opacity:.5;font-size:10px}
tbody tr:hover{background:var(--chip)}
td.name{font-weight:600;min-width:150px}
td.desc{color:var(--muted);max-width:520px}
td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
th.lnk,td.lnk{text-align:center;white-space:nowrap}
tr.filters th{position:sticky;top:34px;background:var(--bg);padding:4px 6px;cursor:default;
  text-transform:none;letter-spacing:0;font-weight:400}
tr.filters input,tr.filters select{width:100%;min-width:58px;box-sizing:border-box;
  background:var(--card);color:var(--fg);border:1px solid var(--line);border-radius:5px;
  padding:3px 6px;font:inherit;font-size:12px}
tr.filters input[type=number]{min-width:52px}
td.lnk a{font-size:12.5px}
.no{color:var(--muted);opacity:.45}
.cat{display:inline-block;background:var(--chip);border:1px solid var(--line);border-radius:5px;
  padding:1px 6px;font-size:11.5px;margin:1px 3px 1px 0;color:var(--muted);white-space:nowrap}
.links{white-space:nowrap;font-size:13px}
.arch{color:var(--warn);font-size:11.5px}
.seed{border-color:var(--accent);color:var(--accent)}
a.inf{border-bottom:1px dotted currentColor}
a.gone{color:var(--warn);text-decoration:line-through}
a.rep{color:var(--muted);text-decoration:none;font-size:11px;padding:0 2px}
a.rep:hover{color:var(--accent);text-decoration:none}
footer{color:var(--muted);font-size:12.5px;margin-top:22px;line-height:1.7}
.theme{background:none;border:1px solid var(--line);border-radius:7px;color:var(--fg);
  padding:8px 11px;cursor:pointer;font:inherit;font-size:14px}
a.theme{text-decoration:none;display:inline-flex;align-items:center;gap:6px;line-height:1.5}
a.theme:hover{border-color:var(--accent);color:var(--accent);text-decoration:none}
.repo::before{content:"";width:15px;height:15px;flex:0 0 15px;background:currentColor;
  -webkit-mask:var(--gh) center/contain no-repeat;mask:var(--gh) center/contain no-repeat}
.stats{margin:0 0 16px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin-bottom:12px}
.kpi{border:1px solid var(--line);border-radius:10px;padding:10px 13px;background:var(--card)}
.kpi .k{font-size:12px;color:var(--muted)}
.kpi .v{font-size:25px;font-weight:600;font-variant-numeric:tabular-nums;line-height:1.25}
.kpi .s{font-size:11.5px;color:var(--muted)}
.charts{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:10px}
.chart{border:1px solid var(--line);border-radius:10px;padding:10px 12px 6px;background:var(--card)}
.chart h3{margin:0;font-size:12.5px;font-weight:600}
.chart p{margin:1px 0 4px;font-size:11.5px;color:var(--muted)}
.chart svg{display:block;width:100%;height:auto}
.chart .band:hover{fill:var(--fg);fill-opacity:.05}
#tip{position:fixed;pointer-events:none;background:var(--card);color:var(--fg);border:1px solid var(--line);
  border-radius:7px;padding:5px 9px;font-size:12px;box-shadow:0 2px 10px rgba(0,0,0,.16);opacity:0;
  transition:opacity .1s;z-index:50;white-space:nowrap}
@media (max-width:640px){ td.desc{display:none} th.desc{display:none} }
</style>
</head>
<body>
<header>
  <div class="wrap">
    <h1><a href="https://github.com/__REPO__">Awesome Regulatory Genomics</a></h1>
    <div class="sub">__COUNT__ tools for transcription-factor binding, motifs, regulatory
      elements, chromatin and gene-regulatory networks · updated __DATE__</div>
    <div class="controls">
      <input type="search" id="q" placeholder="Search name, description, category, language…" autocomplete="off">
      <select id="type"><option value="">Any tool type</option></select>
      <select id="lang"><option value="">Any language</option></select>
      <select id="activity">
        <option value="">Any activity</option>
        <option value="repo">Has a source repository</option>
        <option value="active">Repo pushed in last 2 years</option>
        <option value="stale">Repo idle 5+ years</option>
        <option value="archived">Archived</option>
      </select>
      <button class="theme" id="stats-toggle" type="button" aria-expanded="true">Hide stats</button>
      <a class="theme repo" href="https://github.com/__REPO__">Repository</a>
      <button class="theme" id="theme" type="button">◐</button>
    </div>
  </div>
</header>
<main>
  <div class="chips" id="cats"></div>
  <section class="stats" id="stats">
    <div class="kpis" id="kpis"></div>
    <div class="charts" id="charts"></div>
  </section>
  <div class="count" id="count"></div>
  <div class="tablewrap">
    <table>
      <thead>
      <tr>
        <th data-k="name">Tool</th>
        <th data-k="categories">Categories</th>
        <th class="desc" data-k="description">Description</th>
        <th data-k="has_site" class="lnk">Site</th>
        <th data-k="has_code" class="lnk">Code</th>
        <th data-k="has_biotools" class="lnk">bio.tools</th>
        <th data-k="has_paper" class="lnk">Paper</th>
        <th data-k="n_registries" class="lnk">Install</th>
        <th data-k="repo_stars" class="num">Stars</th>
        <th data-k="citations" class="num">Cites</th>
        <th data-k="year" class="num">Year</th>
      </tr>
      <tr class="filters">
        <th><input data-f="name" type="search" placeholder="filter…"></th>
        <th><input data-f="categories" type="search" placeholder="filter…"></th>
        <th class="desc"><input data-f="description" type="search" placeholder="filter…"></th>
        <th><select data-f="has_site"><option value="">any</option><option value="1">has</option><option value="0">none</option></select></th>
        <th><select data-f="has_code"><option value="">any</option><option value="1">has</option><option value="0">none</option></select></th>
        <th><select data-f="has_biotools"><option value="">any</option><option value="1">has</option><option value="0">none</option></select></th>
        <th><select data-f="has_paper"><option value="">any</option><option value="1">paper</option><option value="2">preprint</option><option value="0">none</option></select></th>
        <th><select data-f="has_install"><option value="">any</option><option value="1">packaged</option><option value="0">none</option></select></th>
        <th><input data-f="repo_stars" type="number" min="0" placeholder="min"></th>
        <th><input data-f="citations" type="number" min="0" placeholder="min"></th>
        <th><input data-f="year" type="number" min="1980" placeholder="min"></th>
      </tr>
      </thead>
      <tbody id="rows"></tbody>
    </table>
  </div>
  <footer>
    Data from <a href="https://bio.tools">bio.tools</a> (CC BY 4.0),
    <a href="https://openalex.org">OpenAlex</a> (CC0) and the GitHub API, plus hand-curated
    entries. Citation counts come from each tool's primary publication only: a rough
    popularity signal, not a quality measure. Where that publication is shared by three
    or more tools it is a suite paper, and no count is shown. Links marked
    <b>preprint</b> are the version bio.tools records and no published equivalent was
    found; see <a href="https://github.com/__REPO__/blob/main/docs/link-check.md">the
    link check</a>.
    Entries marked <span class="cat seed">curated</span>
    are absent from bio.tools and were added by hand.
    A <span class="gone">struck-through</span> link returned 404 when last checked;
    links that merely timed out are not marked, because a slow institutional host
    looks identical to a departed one.
    <b>Site</b> is the tool's own page where that is something other than its source
    repository: a project page, web server or database front end. Tools hosted only on
    GitHub or another code host show a dash there rather than repeating the code link.
    <br><b>Maintainers:</b> a <span class="inf">dotted</span> code link was <i>inferred</i> from a
    homepage or a GitHub search rather than recorded upstream, so it is our guess and may be
    wrong. The <b>?</b> beside it opens a pre-filled issue. Corrections of any kind are welcome:
    <a href="https://github.com/__REPO__/issues/new/choose">open an issue</a>. Fixing the entry
    at <a href="https://bio.tools">bio.tools</a> instead fixes it here on the next refresh, and
    everywhere else that registry is used.
  </footer>
</main>
<div id="tip" role="status"></div>
<script src="catalog.js"></script>
<script>
const CATS = __CATS__;
const root = document.documentElement;
const themeBtn = document.getElementById('theme');
themeBtn.onclick = () => {
  const cur = root.getAttribute('data-theme') ||
    (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  root.setAttribute('data-theme', cur === 'dark' ? 'light' : 'dark');
};

const $ = id => document.getElementById(id);
const state = { q:'', cats:new Set(), type:'', lang:'', activity:'', col:{}, sort:'citations', dir:-1 };

const params = new URLSearchParams(location.search);
if (params.get('category')) state.cats.add(params.get('category'));

// facet dropdowns
const fill = (el, values) => {
  [...new Set(values)].filter(Boolean).sort().forEach(v => {
    const o = document.createElement('option'); o.value = o.textContent = v; el.append(o);
  });
};
fill($('type'), TOOLS.flatMap(t => t.tool_type));
fill($('lang'), TOOLS.flatMap(t => t.languages.concat(t.repo_language ? [t.repo_language] : [])));

// category chips
const catCounts = {};
TOOLS.forEach(t => t.categories.forEach(c => catCounts[c] = (catCounts[c]||0)+1));
const chipBox = $('cats');
// Ordered by size, so the shape of the field is legible from the rack itself.
// The ORDER of CATS still drives the README and the primary-category choice;
// this is presentation only.
[...CATS].filter(([k]) => catCounts[k])
         .sort((a, b) => catCounts[b[0]] - catCounts[a[0]])
         .forEach(([key,label]) => {
  const b = document.createElement('button');
  b.className = 'chip'; b.type = 'button'; b.title = label;
  b.setAttribute('aria-pressed', state.cats.has(key));
  b.innerHTML = '<span class="lab">' + label + '</span>' +
                '<span class="n">' + catCounts[key] + '</span>';
  b.onclick = () => {
    state.cats.has(key) ? state.cats.delete(key) : state.cats.add(key);
    b.setAttribute('aria-pressed', state.cats.has(key));
    render();
  };
  chipBox.append(b);
});

// Presence flags, computed once. Sorting a column of links is only meaningful
// as "which rows have one", so each link column sorts on 0/1 (paper uses 2 for
// a peer-reviewed link and 1 for a preprint, so sorting separates them).
TOOLS.forEach(t => {
  t.has_site = t.site ? 1 : 0;
  t.has_code = t.repo_url ? 1 : 0;
  t.has_biotools = t.biotools_url ? 1 : 0;
  t.has_paper = !t.publication ? 0 : (t.preprint ? 1 : 2);
  t.reg_names = Object.keys(t.registries || {}).sort();
  t.n_registries = t.reg_names.length;
  t.has_install = t.n_registries ? 1 : 0;
});

const YEAR_MS = 365.25*24*3600*1000;
const matches = t => {
  if (state.cats.size && !t.categories.some(c => state.cats.has(c))) return false;
  if (state.type && !t.tool_type.includes(state.type)) return false;
  if (state.lang && !t.languages.includes(state.lang) && t.repo_language !== state.lang) return false;
  if (state.activity) {
    const age = t.repo_pushed ? (Date.now() - Date.parse(t.repo_pushed)) / YEAR_MS : null;
    if (state.activity === 'repo' && !t.repo_url) return false;
    if (state.activity === 'active' && !(age !== null && age <= 2 && !t.repo_archived)) return false;
    if (state.activity === 'stale' && !(age !== null && age >= 5)) return false;
    if (state.activity === 'archived' && !t.repo_archived) return false;
  }
  for (const [k,v] of Object.entries(state.col)) {
    if (v === '' || v === undefined) continue;
    if (k === 'name' || k === 'description') {
      if (!String(t[k]||'').toLowerCase().includes(v)) return false;
    } else if (k === 'categories') {
      const txt = t.categories.map(c => (catLabel[c]||c)).join(' ').toLowerCase();
      if (!txt.includes(v)) return false;
    } else if (k === 'has_site' || k === 'has_code' || k === 'has_biotools'
               || k === 'has_install') {
      if (t[k] !== Number(v)) return false;
    } else if (k === 'has_paper') {
      if (t.has_paper !== Number(v)) return false;
    } else {                       // numeric minimums
      const n = k === 'year' ? Number(t.year) : Number(t[k]);
      if (!Number.isFinite(n) || n < Number(v)) return false;
    }
  }
  if (state.q) {
    const hay = (t.name + ' ' + t.description + ' ' + t.categories.join(' ') + ' ' +
      t.languages.join(' ') + ' ' + t.tool_type.join(' ') + ' ' + t.repo_language + ' ' +
      (t.tags||[]).join(' ')).toLowerCase();
    if (!state.q.split(/\\s+/).every(w => hay.includes(w))) return false;
  }
  return true;
};

const cmp = (a,b) => {
  const k = state.sort;
  let x = a[k], y = b[k];
  if (k === 'categories') { x = x.join(); y = y.join(); }
  if (x === null || x === undefined || x === '') return 1;
  if (y === null || y === undefined || y === '') return -1;
  if (typeof x === 'number' && typeof y === 'number') return (x-y) * state.dir;
  return String(x).localeCompare(String(y)) * state.dir;
};

const REPORT = 'https://github.com/__REPO__/issues/new';
const reportUrl = t => REPORT + '?template=wrong-repository.yml&title='
  + encodeURIComponent('repo: ' + t.name);

const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const catLabel = Object.fromEntries(CATS);

// ---------------------------------------------------------------------------
// Statistics panel.
//
// Every chart here is ONE series, so bar length carries the magnitude and the
// colour carries nothing: shading each bar darker-where-bigger would encode the
// same fact twice and burn the only free channel. The hue is the validated
// series-1 blue for the surface it sits on, read from CSS so the theme toggle
// moves it.
//
// The panel reflects the CURRENT FILTER, not the whole catalog, which is what
// makes it worth having: "when were the peak callers published" is a question
// you answer by clicking the category chip and reading the year chart.
// ---------------------------------------------------------------------------
let statsOpen = true;
const tip = document.getElementById('tip');
const showTip = (evt, html) => {
  tip.innerHTML = html;
  tip.style.opacity = '1';
  const pad = 14, w = tip.offsetWidth, h = tip.offsetHeight;
  let x = evt.clientX + pad, y = evt.clientY + pad;
  if (x + w > innerWidth - 8) x = evt.clientX - w - pad;
  if (y + h > innerHeight - 8) y = evt.clientY - h - pad;
  tip.style.left = x + 'px'; tip.style.top = y + 'px';
};
const hideTip = () => { tip.style.opacity = '0'; };

const compact = n => n >= 1000 ? (n / 1000).toFixed(n >= 10000 ? 0 : 1) + 'k'
                               : String(n);

// A column chart. bins: [{label, value, tip}]
function columns(bins, width, height) {
  const padL = 30, padR = 6, padT = 12, padB = 17;
  const plotW = Math.max(40, width - padL - padR), plotH = height - padT - padB;
  const max = Math.max(1, ...bins.map(b => b.value));
  const band = plotW / bins.length;
  // Cap the mark and leave the band's remainder as air; 2px of that is the
  // surface gap that separates neighbours without drawing a stroke.
  const barW = Math.max(2, Math.min(24, band - 2));
  const y = v => padT + plotH - (v / max) * plotH;
  const parts = [];

  // Recessive hairline grid: only zero and the top of the scale.
  for (const v of [0, max]) {
    parts.push('<line x1="' + padL + '" x2="' + (padL + plotW) + '" y1="' + y(v) +
               '" y2="' + y(v) + '" stroke="var(--grid)" stroke-width="1"/>');
    parts.push('<text x="' + (padL - 5) + '" y="' + (y(v) + 3.5) +
               '" text-anchor="end" font-size="9.5" fill="var(--muted)">' +
               compact(v) + '</text>');
  }

  const peak = bins.reduce((a, b) => b.value > a.value ? b : a, bins[0]);
  bins.forEach((b, i) => {
    const x = padL + i * band + (band - barW) / 2;
    const top = y(b.value), h = padT + plotH - top;
    if (h > 0) {
      // 4px rounded data-end, square at the baseline.
      const r = Math.min(4, barW / 2, h);
      parts.push('<path d="M' + x + ',' + (padT + plotH) +
                 ' L' + x + ',' + (top + r) +
                 ' Q' + x + ',' + top + ' ' + (x + r) + ',' + top +
                 ' L' + (x + barW - r) + ',' + top +
                 ' Q' + (x + barW) + ',' + top + ' ' + (x + barW) + ',' + (top + r) +
                 ' L' + (x + barW) + ',' + (padT + plotH) + ' Z" fill="var(--series-1)"/>');
    }
    // One direct label, on the tallest cap only. A number on every column is
    // noise; the axis and the tooltip carry the rest.
    if (b === peak && b.value > 0 && barW >= 14) {
      parts.push('<text x="' + (x + barW / 2) + '" y="' + (top - 3) +
                 '" text-anchor="middle" font-size="9.5" font-weight="600"' +
                 ' fill="var(--fg)">' + compact(b.value) + '</text>');
    }
    if (b.tick) {
      parts.push('<text x="' + (x + barW / 2) + '" y="' + (height - 4) +
                 '" text-anchor="middle" font-size="9.5" fill="var(--muted)">' +
                 b.tick + '</text>');
    }
    // Hit target spans the whole band, not just the mark.
    parts.push('<rect class="band" x="' + (padL + i * band) + '" y="' + padT +
               '" width="' + band + '" height="' + plotH + '" fill="transparent"' +
               ' data-tip="' + esc(b.tip) + '"/>');
  });
  return '<svg viewBox="0 0 ' + width + ' ' + height + '" width="' + width +
         '" height="' + height + '" role="img">' + parts.join('') + '</svg>';
}

function card(title, sub, bins, width) {
  return '<div class="chart"><h3>' + esc(title) + '</h3><p>' + esc(sub) + '</p>' +
         columns(bins, width, 132) + '</div>';
}

const yearBins = (rows, key) => {
  const years = rows.map(t => parseInt(t[key], 10)).filter(y => y >= 1990 && y <= 2100);
  if (!years.length) return null;
  const lo = Math.max(1993, Math.min(...years)), hi = Math.max(...years);
  const counts = new Map();
  years.forEach(y => { const c = Math.max(y, lo); counts.set(c, (counts.get(c) || 0) + 1); });
  const bins = [];
  for (let y = lo; y <= hi; y++) {
    const n = counts.get(y) || 0;
    bins.push({ value: n, tick: (y % 5 === 0) ? String(y) : '',
                tip: '<b>' + y + '</b> ' + n.toLocaleString() + ' tools' });
  }
  return { bins, n: years.length };
};

const LOG_BUCKETS = [[0, 0, 'none'], [1, 9, '1-9'], [10, 99, '10-99'],
                     [100, 999, '100-999'], [1000, 9999, '1k-10k'],
                     [10000, Infinity, '10k+']];
const logBins = (rows, key, noun) => {
  const vals = rows.map(t => t[key]).filter(v => v !== null && v !== undefined && v !== '');
  if (!vals.length) return null;
  const bins = LOG_BUCKETS.map(([lo, hi, tick]) => {
    const n = vals.filter(v => v >= lo && v <= hi).length;
    const range = hi === Infinity ? lo.toLocaleString() + '+'
                : lo === hi ? String(lo) : lo.toLocaleString() + ' to ' + hi.toLocaleString();
    return { value: n, tick,
             tip: '<b>' + range + ' ' + noun + '</b> ' + n.toLocaleString() + ' tools' };
  });
  return { bins, n: vals.length };
};

function renderStats(rows) {
  const total = rows.length;
  const pct = n => total ? Math.round(100 * n / total) + '%' : '0%';
  const withRepo = rows.filter(t => t.repo_url).length;
  const install = rows.filter(t => t.n_registries).length;
  // "Actively maintained" says more about whether to reach for a tool than a
  // dead-link count does, and the dead links are still marked in the table and
  // listed in docs/homepage-check.md. Same rule as the Activity filter.
  const YR = 365.25 * 24 * 3600 * 1000;
  const tracked = rows.filter(t => t.repo_pushed).length;
  const active = rows.filter(t => t.repo_pushed && !t.repo_archived &&
                                  (Date.now() - Date.parse(t.repo_pushed)) / YR <= 2).length;
  document.getElementById('kpis').innerHTML = [
    ['Tools shown', total.toLocaleString(),
     total === TOOLS.length ? 'the whole catalog' : 'of ' + TOOLS.length.toLocaleString() + ' total'],
    ['Source repository', withRepo.toLocaleString(), pct(withRepo) + ' of these'],
    ['Installable package', install.toLocaleString(), pct(install) + ' of these'],
    ['Actively maintained', active.toLocaleString(),
     // Against repositories we actually have activity data for. Dividing by
     // every repository would count Bitbucket and SourceForge entries as
     // inactive when the truth is that nothing was measured for them.
     tracked ? Math.round(100 * active / tracked) + '% of ' + tracked.toLocaleString() +
               ' with activity data'
             : 'no activity data here'],
  ].map(([k, v, sfx]) => '<div class="kpi"><div class="k">' + k + '</div><div class="v">' +
      v + '</div><div class="s">' + sfx + '</div></div>').join('');

  const box = document.getElementById('charts');
  // Measure, then draw at that size, so the text is never scaled by a viewBox.
  const cols = Math.max(1, Math.floor((box.clientWidth + 10) / 290));
  const w = Math.max(240, Math.floor((box.clientWidth - 10 * (cols - 1)) / cols) - 26);

  const pub = yearBins(rows, 'year');
  const push = yearBins(rows.map(t => ({ y: (t.repo_pushed || '').slice(0, 4) })), 'y');
  const cites = logBins(rows, 'citations', 'citations');
  const stars = logBins(rows, 'repo_stars', 'stars');
  const out = [];
  if (pub) out.push(card('Tools by publication year',
      pub.n.toLocaleString() + ' with a known year', pub.bins, w));
  if (push) out.push(card('Repository last updated',
      push.n.toLocaleString() + ' with a live repository', push.bins, w));
  if (cites) out.push(card('Citations of the primary paper',
      cites.n.toLocaleString() + ' with a count', cites.bins, w));
  if (stars) out.push(card('GitHub stars',
      stars.n.toLocaleString() + ' with a repository', stars.bins, w));
  box.innerHTML = out.join('');
  box.querySelectorAll('[data-tip]').forEach(el => {
    el.addEventListener('mousemove', e => showTip(e, el.dataset.tip));
    el.addEventListener('mouseleave', hideTip);
  });
}

function render(){
  const rows = TOOLS.filter(matches).sort(cmp);
  if (statsOpen) renderStats(rows);
  $('count').textContent = rows.length + ' of ' + TOOLS.length + ' tools' +
    (state.cats.size ? ' · ' + [...state.cats].map(c=>catLabel[c]).join(', ') : '');
  $('rows').innerHTML = rows.map(t => {
    const href = t.homepage || t.repo_url || t.biotools_url;
    const dash = '<span class="no">-</span>';
    // The tool's own page, only where that is not just its repository. The
    // hostname goes in the tooltip: it is the fastest way to see whether a
    // link is a maintained project page or a lab URL from 2009.
    // A 404 is worth saying out loud; a timeout is not, because it is as
    // often a slow institutional host as a departed one.
    const siteDead = t.homepage_status === 'dead';
    const siteCell = t.site
      ? '<a href="'+esc(t.site)+'" class="'+(siteDead?'gone':'')+'" title="'
          + (siteDead ? 'This page returned 404 when last checked. ' : '')
          + esc(t.site.replace(/^https?:\\/\\/(www\\.)?/, '').replace(/\\/.*$/, ''))+'">site</a>'
      : dash;
    // An inferred link is our guess, not the tool's own statement. Say so, and
    // make reporting it one click rather than a hunt for the issue tracker.
    let codeCell = dash;
    if (t.repo_url) {
      const inferred = t.repo_origin === 'inferred';
      const repoDead = t.repo_status === 'dead';
      const cls = [inferred?'inf':'', repoDead?'gone':''].filter(Boolean).join(' ');
      const tip = (repoDead ? 'This repository returned 404 when last checked. ' : '')
        + (inferred ? 'Inferred from its homepage or a GitHub search, not recorded upstream. Please report if wrong.' : '');
      codeCell = '<a href="'+esc(t.repo_url)+'"'+(cls?' class="'+cls+'"':'')+(tip?' title="'+esc(tip)+'"':'')+'>code</a>';
      if (inferred) codeCell += ' <a class="rep" title="Report a wrong repository link" href="'+reportUrl(t)+'">?</a>';
    }
    const btCell = t.biotools_url ? '<a href="'+esc(t.biotools_url)+'">bio.tools</a>' : dash;
    let paperCell = dash;
    if (t.publication) {
      const p = t.publication;
      if (p.startsWith('pmid:'))
        paperCell = '<a href="https://pubmed.ncbi.nlm.nih.gov/'+esc(p.slice(5))+'/">paper</a>';
      else if (p.startsWith('doi:'))
        paperCell = '<a href="https://doi.org/'+esc(p.slice(4))+'">'+(t.preprint?'preprint':'paper')+'</a>';
    }
    // Where the tool can actually be installed from. Two letters keeps the
    // column narrow; the tooltip and the link carry the detail.
    const REG = {bioconductor:'Bc', cran:'CR', pypi:'Py', conda:'Cn', docker:'Dk'};
    const installCell = t.n_registries
      ? t.reg_names.map(r => '<a href="'+esc(t.registries[r])+'" title="'+esc(r)+'">'
          + esc(REG[r] || r.slice(0,2)) + '</a>').join(' ')
      : dash;
    const cats = t.categories.map(c=>'<span class="cat">'+esc(catLabel[c]||c)+'</span>').join('') +
      (t.source === 'curated' ? '<span class="cat seed">curated</span>' : '');
    return '<tr><td class="name">' + (href ? '<a href="'+esc(href)+'">'+esc(t.name)+'</a>' : esc(t.name)) +
      (t.repo_archived ? '<br><span class="arch">archived</span>' : '') + '</td>' +
      '<td>' + cats + '</td>' +
      '<td class="desc">' + esc(t.description) + '</td>' +
      '<td class="lnk">' + siteCell + '</td>' +
      '<td class="lnk">' + codeCell + '</td>' +
      '<td class="lnk">' + btCell + '</td>' +
      '<td class="lnk">' + paperCell + '</td>' +
      '<td class="lnk">' + installCell + '</td>' +
      '<td class="num">' + (t.repo_stars ?? '') + '</td>' +
      '<td class="num">' + (t.citations ? t.citations.toLocaleString() : '') + '</td>' +
      '<td class="num">' + esc(t.year) + '</td></tr>';
  }).join('');
}

document.querySelectorAll('[data-f]').forEach(el => {
  const apply = () => {
    const v = el.value.trim();
    if (v === '') delete state.col[el.dataset.f];
    else state.col[el.dataset.f] = el.type === 'search' ? v.toLowerCase() : v;
    render();
  };
  // The debounce timer is PER ELEMENT. A single shared timer meant editing one
  // filter then another quickly cancelled the first one's pending update, so
  // clearing a box left its filter silently applied.
  let timer;
  el.addEventListener(el.tagName === 'SELECT' ? 'change' : 'input',
    () => { clearTimeout(timer); timer = setTimeout(apply, 120); });
  // The filter row sits inside <thead>; without this, typing in a box would
  // also trigger the column's sort handler.
  el.addEventListener('click', e => e.stopPropagation());
});

document.querySelectorAll('th[data-k]').forEach(th => {
  th.onclick = () => {
    const k = th.dataset.k;
    state.dir = state.sort === k ? -state.dir : (['name','description','categories'].includes(k) ? 1 : -1);
    state.sort = k;
    document.querySelectorAll('th .ar').forEach(a => a.remove());
    const ar = document.createElement('span');
    ar.className = 'ar'; ar.textContent = state.dir > 0 ? ' ▲' : ' ▼';
    th.append(ar);
    render();
  };
});
let timer;
$('q').oninput = e => { clearTimeout(timer); timer = setTimeout(() => { state.q = e.target.value.trim().toLowerCase(); render(); }, 120); };

// The panel is useful but the table is the point, so it can be folded away.
const statsBtn = $('stats-toggle');
statsBtn.onclick = () => {
  statsOpen = !statsOpen;
  $('stats').style.display = statsOpen ? '' : 'none';
  statsBtn.textContent = statsOpen ? 'Hide stats' : 'Show stats';
  statsBtn.setAttribute('aria-expanded', String(statsOpen));
  if (statsOpen) render();
};
// Charts are drawn at a measured pixel width rather than scaled by a viewBox,
// so a resize has to redraw them or the text ends up the wrong size.
let rzTimer;
addEventListener('resize', () => {
  clearTimeout(rzTimer);
  rzTimer = setTimeout(() => { if (statsOpen) renderStats(TOOLS.filter(matches)); }, 150);
});
['type','lang','activity'].forEach(id => $(id).onchange = e => { state[id] = e.target.value; render(); });
render();
</script>
</body>
</html>
"""


def render_site(catalog: dict) -> None:
    tools = catalog["tools"]
    slim = [{
        "name": t["name"], "description": t["description"], "categories": t["categories"],
        "homepage": t["homepage"], "site": site_url(t),
        "homepage_status": t.get("homepage_status", ""),
        "repo_status": t.get("repo_status", ""),
        "repo_url": t["repo_url"], "biotools_url": t["biotools_url"],
        "repo_stars": t["repo_stars"], "repo_pushed": t["repo_pushed"],
        "repo_archived": t["repo_archived"], "repo_language": t["repo_language"],
        "repo_origin": t.get("repo_origin", ""),
        "registries": t.get("_registries") or {},
        "tool_type": t["tool_type"], "languages": t["languages"],
        "citations": t["citations"], "year": t["year"], "publication": t["publication"],
        "preprint": bool(t.get("publication_is_preprint")),
        "source": t["source"], "tags": t["tags"],
    } for t in tools]

    DOCS.mkdir(parents=True, exist_ok=True)
    DATA_JS.write_text("const TOOLS = " + json.dumps(slim, separators=(",", ":")) + ";\n")

    cats = [[k, CATEGORY_LABEL[k]] for k, _, _ in CATEGORIES]
    html = (HTML
            .replace("__COUNT__", str(len(tools)))
            .replace("__DATE__", catalog["meta"]["generated"])
            .replace("__REPO__", REPO_SLUG)
            .replace("__CATS__", json.dumps(cats)))
    INDEX.write_text(html)


def main() -> None:
    catalog = json.loads(CATALOG.read_text())
    README.write_text(render_readme(catalog))
    render_site(catalog)
    print(f"README.md          {README.stat().st_size/1024:.1f} KB")
    print(f"docs/index.html    {INDEX.stat().st_size/1024:.1f} KB")
    print(f"docs/catalog.js    {DATA_JS.stat().st_size/1024:.1f} KB "
          f"({catalog['meta']['count']} tools)")


if __name__ == "__main__":
    main()
