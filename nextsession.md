# Next session

**Last updated:** 2026-07-28
**Start with:** `CLAUDE.md` (traps and generated-file rules), then `ROADMAP.md`.
Memory notes: `[[awesome-regulatory-genomics]]`, `[[biotools-edam-annotations-unreliable]]`,
`[[verify-inferred-data-not-just-resolvable]]`, `[[upstream-fields-can-be-populated-and-wrong]]`.

## Current state

- **Public** at https://github.com/thirtysix/awesome-regulatory-genomics
- **Site live** at https://thirtysix.github.io/awesome-regulatory-genomics/
- Local: `~/Dropbox/manuscripts/0.datasets_visualizations/002.AI_projects/awesome-regulatory-genomics`
- **Working tree clean, `main` level with `origin/main` at `d8c7266`.** Everything
  from this session is committed, pushed, and both CI workflows are green.
- Credentials: none in the repo. `DEEPINFRA_API_KEY` and `CONTACT_EMAIL` are
  optional, documented in `.env.example`, and `.env` is gitignored

## Headline results

**1,951 tools** across **20 categories**, up from 1,800 and 15 at the start of
the session. Benchmark recall **153/221 (69%)** against a benchmark grown from 89
entries; the original scored 100% and had stopped measuring anything.

Per-record evidence: 988 with a source repository, 1,269 with a site of their
own, 413 installable from a package registry, ~1,800 with a publication year,
1,861 with a publication, 130 links known dead and struck through.

## What changed this session

Six commits. Full detail in `ROADMAP.md`; the shape of it:

1. **Tests and CI.** 120 offline tests over the rule functions, run on every push
   plus a rebuild-and-check-for-drift gate.
2. **Discovery beyond bio.tools.** Bioconductor + Galaxy ToolShed (`make
   discover`) and Europe PMC via the "NAME: what it does" tool-paper title
   convention (`make discover-lit`). 93 tools promoted by hand.
3. **Scope widened** to DNA methylation, 3D genome, histone marks, reporter
   assays and molecular QTL, with a third benchmark tier written first.
4. **Evidence per record.** Homepage liveness (`make check-links`), install
   routes read off each repository README (`make installs`), publication year and
   licence backfill (`make fill-metadata`).
5. **The site.** Full bleed, a statistics panel that follows the current filter,
   category rack ordered by size, repository link in the header.

## Gotchas discovered this session

Full list in `CLAUDE.md`. The ones most likely to bite again:

- **The pipeline order is select -> enrich -> build.** Changing the selection
  rules and running `make build` alone silently reuses the previous
  `enriched.json.gz`, and the change looks like it did nothing.
- **`build.py` writes `catalog.json` before the TSV.** A row mutation placed
  between the two lands in the TSV and silently not on the site.
- **A monorepo is not a tool's repository.** `hgv_pass` inherited Galaxy's 1,818
  stars and outranked MACS. Dropping the URL is not enough; the stars, activity,
  licence and language all come from the same blob.
- **Four bugs this session were the same shape:** something matched on a name and
  was believed. `norm_name` merging SCENIC+ into SCENIC, `from_seed` never
  reading the citation cache, `probe_biotools` reporting name hits as fact, and
  the monorepo link.
- **Two of the README's own examples of bad EDAM metadata were themselves
  wrong** (FIMO, MACS). A plausible claim about bad metadata reads as
  self-evidently true. Query the live record.
- **Hi-C is a technology, not a field.** In the strong tier it admitted a genome
  announcement paper that used Hi-C to scaffold an assembly.
- **A partial link check sorted alphabetically is a biased sample** - every
  `http://` URL sorts first, which is exactly the rottenest hosts.

## Possible next steps

None committed; ask the user. In rough order of value:

1. **The deferred curation block.** 19 of 1,951 entries are featured. Expanding
   that, marking superseded tools, and adding task-oriented entry points is the
   main thing left between this and being genuinely *better* than bio.tools
   rather than merely more complete.
2. **68 benchmark misses** in `docs/coverage.md`, concentrated in the new areas:
   Juicer, cooler, HiC-Pro, MPRAnalyze, coloc, SuSiE. Absent from bio.tools, so
   this is `seeds.yaml` work.
3. **Review queues:** 134 held install routes, ~500 discovery candidates, 235
   repository near-misses, 147 scope disputes.
4. `make refresh` to pick up the 5 new `SEED_BIOTOOLS_IDS` (fetch-by-ID only
   happens during harvest), and `make repos` for the 93 new seeds.
5. CRISPR screens, the half of scope batch 2 deliberately skipped.
6. Watch the first automated refresh on 1 August 2026, 04:00 UTC.

## Outstanding, needs the user

- **Rotate the DeepInfra key** used in an earlier session. It never entered the
  repository but is in that conversation transcript. Still outstanding.
- The `jobscout` repo has three commits from a stop-hook sweep that were
  deliberately **not pushed**. Unrelated to this project.
