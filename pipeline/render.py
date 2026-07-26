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

from config import CATEGORIES, CATEGORY_DESC, CATEGORY_LABEL, DATA, DOCS, ROOT

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
    featured_n = meta["featured"]

    out = []
    A = out.append

    A("# Awesome Regulatory Genomics")
    A("")
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
      "tool type, language, licence, activity and citations.")
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

    A("## How this list is built")
    A("")
    A("```")
    A("harvest.py        wide sweep of bio.tools (EDAM operation + free-text queries)")
    A("select_domain.py  tiered precision filter -> what is in scope")
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
      "fuzzy text match, not an ontology lookup. An unquoted query for `cis-regulatory` "
      "returns 3,000 records matching \"cis\" *or* \"regulatory\". So the sweep is "
      "deliberately over-broad and precision is restored afterwards by filtering on the "
      "annotations a record actually carries.")
    A("")
    A("**EDAM annotations are not trusted on their own.** They are frequently wrong: "
      "FIMO is filed under *Genotyping*, HOCOMOCO under *Data handling*, MACS under "
      "*Modelling and simulation*, and the operation *Peak detection* is used almost "
      "exclusively by mass-spectrometry tools. Operations are therefore tiered: "
      "specific terms admit a record on their own, ambiguous ones need a corroborating "
      "topic or text signal, and four terms are queried but never used to admit anything. "
      "A text-match escape hatch recovers in-domain tools with no usable annotation at "
      "all. Every accepted record stores the rule that admitted it "
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
      "[`docs/repo-review.md`](docs/repo-review.md) rather than applied.")
    A(f"- **{featured_n} tools are featured** in the curated sections above; the rest are "
      f"in the [full catalog]({SITE}).")
    A("")
    A("Honest limitations:")
    A("")
    A("- bio.tools skews toward tools with a publication and an ELIXIR-adjacent "
      "submitter. The sequence-to-function deep-learning literature is badly "
      "under-represented there; those entries come from `curation/seeds.yaml` and are "
      "necessarily incomplete.")
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
      "binding site prediction. That table and the scripts that produced it are preserved "
      "unchanged in [`dissertation/`](dissertation/) for citation; "
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
}
@media (prefers-color-scheme:dark){
  :root{ --bg:#14171a; --fg:#e6e9ec; --muted:#98a2ad; --line:#2a2f35; --accent:#6aa9f0;
         --chip:#21262c; --chip-on:#6aa9f0; --chip-on-fg:#101316; --card:#1a1e22; --warn:#e0a06a; }
}
:root[data-theme=light]{ --bg:#fff; --fg:#1a1d21; --muted:#5c6570; --line:#e3e6ea; --accent:#1b6ac9;
  --chip:#f1f4f8; --chip-on:#1b6ac9; --chip-on-fg:#fff; --card:#fff; --warn:#a4551a; }
:root[data-theme=dark]{ --bg:#14171a; --fg:#e6e9ec; --muted:#98a2ad; --line:#2a2f35; --accent:#6aa9f0;
  --chip:#21262c; --chip-on:#6aa9f0; --chip-on-fg:#101316; --card:#1a1e22; --warn:#e0a06a; }
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
  font:15px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;}
a{color:var(--accent);text-decoration:none} a:hover{text-decoration:underline}
header{border-bottom:1px solid var(--line);padding:18px 20px;position:sticky;top:0;background:var(--bg);z-index:10}
.wrap{max-width:1180px;margin:0 auto}
h1{font-size:19px;margin:0 0 3px} h1 a{color:inherit}
.sub{color:var(--muted);font-size:13px}
.controls{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px;align-items:center}
input[type=search],select{background:var(--card);color:var(--fg);border:1px solid var(--line);
  border-radius:7px;padding:8px 11px;font:inherit;font-size:14px}
input[type=search]{flex:1 1 300px;min-width:200px}
main{max-width:1180px;margin:0 auto;padding:18px 20px 60px}
.chips{display:flex;gap:6px;flex-wrap:wrap;margin:0 0 14px}
.chip{background:var(--chip);border:1px solid var(--line);border-radius:999px;
  padding:4px 11px;font-size:12.5px;cursor:pointer;user-select:none;white-space:nowrap}
.chip[aria-pressed=true]{background:var(--chip-on);color:var(--chip-on-fg);border-color:var(--chip-on)}
.chip .n{opacity:.65;margin-left:5px;font-variant-numeric:tabular-nums}
.count{color:var(--muted);font-size:13px;margin:0 0 10px}
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:10px}
table{border-collapse:collapse;width:100%;min-width:820px;font-size:14px}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}
th{position:sticky;top:0;background:var(--bg);cursor:pointer;white-space:nowrap;
   font-weight:600;font-size:12.5px;letter-spacing:.02em;text-transform:uppercase;color:var(--muted)}
th:hover{color:var(--fg)} th .ar{opacity:.5;font-size:10px}
tbody tr:hover{background:var(--chip)}
td.name{font-weight:600;min-width:150px}
td.desc{color:var(--muted);max-width:520px}
td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.cat{display:inline-block;background:var(--chip);border:1px solid var(--line);border-radius:5px;
  padding:1px 6px;font-size:11.5px;margin:1px 3px 1px 0;color:var(--muted);white-space:nowrap}
.links{white-space:nowrap;font-size:13px}
.arch{color:var(--warn);font-size:11.5px}
.seed{border-color:var(--accent);color:var(--accent)}
footer{color:var(--muted);font-size:12.5px;margin-top:22px;line-height:1.7}
.theme{background:none;border:1px solid var(--line);border-radius:7px;color:var(--fg);
  padding:8px 11px;cursor:pointer;font:inherit;font-size:14px}
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
      <button class="theme" id="theme" type="button">◐</button>
    </div>
  </div>
</header>
<main>
  <div class="chips" id="cats"></div>
  <div class="count" id="count"></div>
  <div class="tablewrap">
    <table>
      <thead><tr>
        <th data-k="name">Tool</th>
        <th data-k="categories">Categories</th>
        <th class="desc" data-k="description">Description</th>
        <th data-k="repo_stars" class="num">Stars</th>
        <th data-k="citations" class="num">Cites</th>
        <th data-k="year" class="num">Year</th>
        <th>Links</th>
      </tr></thead>
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
    <br>Corrections welcome: <a href="https://github.com/__REPO__/issues">open an issue</a>.
  </footer>
</main>
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
const state = { q:'', cats:new Set(), type:'', lang:'', activity:'', sort:'citations', dir:-1 };

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
CATS.forEach(([key,label]) => {
  if (!catCounts[key]) return;
  const b = document.createElement('button');
  b.className = 'chip'; b.type = 'button';
  b.setAttribute('aria-pressed', state.cats.has(key));
  b.innerHTML = label + '<span class="n">' + catCounts[key] + '</span>';
  b.onclick = () => {
    state.cats.has(key) ? state.cats.delete(key) : state.cats.add(key);
    b.setAttribute('aria-pressed', state.cats.has(key));
    render();
  };
  chipBox.append(b);
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

const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const catLabel = Object.fromEntries(CATS);

function render(){
  const rows = TOOLS.filter(matches).sort(cmp);
  $('count').textContent = rows.length + ' of ' + TOOLS.length + ' tools' +
    (state.cats.size ? ' · ' + [...state.cats].map(c=>catLabel[c]).join(', ') : '');
  $('rows').innerHTML = rows.map(t => {
    const href = t.homepage || t.repo_url || t.biotools_url;
    const links = [];
    if (t.repo_url) links.push('<a href="'+esc(t.repo_url)+'">code</a>');
    if (t.biotools_url) links.push('<a href="'+esc(t.biotools_url)+'">bio.tools</a>');
    if (t.publication) {
      const p = t.publication;
      if (p.startsWith('pmid:')) links.push('<a href="https://pubmed.ncbi.nlm.nih.gov/'+esc(p.slice(5))+'/">paper</a>');
      else if (p.startsWith('doi:')) links.push('<a href="https://doi.org/'+esc(p.slice(4))+'">'+(t.preprint?'preprint':'paper')+'</a>');
    }
    const cats = t.categories.map(c=>'<span class="cat">'+esc(catLabel[c]||c)+'</span>').join('') +
      (t.source === 'curated' ? '<span class="cat seed">curated</span>' : '');
    return '<tr><td class="name">' + (href ? '<a href="'+esc(href)+'">'+esc(t.name)+'</a>' : esc(t.name)) +
      (t.repo_archived ? '<br><span class="arch">archived</span>' : '') + '</td>' +
      '<td>' + cats + '</td>' +
      '<td class="desc">' + esc(t.description) + '</td>' +
      '<td class="num">' + (t.repo_stars ?? '') + '</td>' +
      '<td class="num">' + (t.citations ? t.citations.toLocaleString() : '') + '</td>' +
      '<td class="num">' + esc(t.year) + '</td>' +
      '<td class="links">' + links.join(' · ') + '</td></tr>';
  }).join('');
}

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
        "homepage": t["homepage"], "repo_url": t["repo_url"], "biotools_url": t["biotools_url"],
        "repo_stars": t["repo_stars"], "repo_pushed": t["repo_pushed"],
        "repo_archived": t["repo_archived"], "repo_language": t["repo_language"],
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
