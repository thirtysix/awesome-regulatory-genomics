# Next session

**Last updated:** 2026-07-28
**Start with:** `CLAUDE.md` (traps and generated-file rules), then `ROADMAP.md`.
Memory notes: `[[awesome-regulatory-genomics]]`, `[[biotools-edam-annotations-unreliable]]`,
`[[verify-inferred-data-not-just-resolvable]]`.

## Current state

- **Public** at https://github.com/thirtysix/awesome-regulatory-genomics
- **Site live** at https://thirtysix.github.io/awesome-regulatory-genomics/
- Local path: `~/Dropbox/manuscripts/0.datasets_visualizations/002.AI_projects/awesome-regulatory-genomics`
- **Nothing from the 2026-07-28 session is committed yet.** Working tree has
  ~21 modified and ~10 new files. Review before pushing.
- Credentials: none in the repo. `DEEPINFRA_API_KEY` and `CONTACT_EMAIL` are
  optional, documented in `.env.example`, and `.env` is gitignored

## Headline results

**1,893 tools** (1,764 from bio.tools, 129 curated seeds), up from 1,800.
Benchmark recall **137/168 (82%)** against a deliberately harder benchmark;
the old 89-entry one scored 100% and had stopped measuring.

Per-record coverage: 950 with a repository, 1,235 with a site of their own,
1,311 with citations, 1,800 with a year (95%), 857 with a licence, 278 with a
package install route, 131 links known dead and struck through.

## What changed this session

Seven items, all in `ROADMAP.md` with full detail:

1. **Unit tests** (`make test`, CI on every push): 70 tests over the rule
   functions, offline, sub-second.
2. **Registry discovery** (`make discover`): Bioconductor + Galaxy ToolShed
   through the same filter. 46 tools promoted.
3. **Literature discovery** (`make discover-lit`): the "NAME: what it does"
   title convention over Europe PMC. 47 tools promoted.
4. **Harder benchmark**: 89 to 168 entries, recall 100% to 82%.
5. **Install column**: package availability surfaced, 219 to 278 tools.
6. **Homepage liveness** (`make check-links`): all 1,837 homepages graded.
7. **Field filling** (`make fill-metadata`): year and licence.

**Three real bugs fell out of this work**, all the same shape: something
matched on a name and was believed.

- `norm_name()` stripped `+`, merging the SCENIC+ seed into the unrelated SCENIC.
- `from_seed()` hard-coded `citations: None`, so FIMO showed blank instead of 4,992.
- `probe_biotools()` reported name matches as fact; three of eight were
  different tools (`Thor`, `inps`, `maestro`).

## Gotchas discovered this session

Full list in `CLAUDE.md`. New ones worth not re-deriving:

- **`build.py` writes `catalog.json` before the TSV.** A row mutation placed
  between the two lands in the TSV and silently not on the site.
- **The Galaxy ToolShed publishes one repository per wrapper, not per tool.**
  AlphaGenome arrived five times. Merge by shared homepage, never by name.
- **bioconda is unusable for discovery**: its public index has names without
  summaries, and the API that carried them now returns 401.
- **A partial link check sorted alphabetically is a biased sample** - every
  `http://` URL sorts first, which is exactly the rottenest hosts.

## Possible next steps

1. **Commit and push** this session's work. Nothing has been pushed.
2. `make repos` for the 93 new seeds; only the GitHub-hosted ones have a code link.
3. `make refresh` to pick up the 5 new `SEED_BIOTOOLS_IDS` (fetch-by-ID only
   happens during harvest).
4. Work the 31 benchmark misses down (`docs/coverage.md`), and the 115 + 390
   remaining discovery candidates.
5. Decide the Hi-C/TAD and DNA-methylation scope question before promoting more
   registry candidates; it is what most of the untaken ones are.
6. Then the deferred curation block: featured entries beyond the current 19,
   superseded markers, task-oriented entry points.

## Outstanding, needs the user

- **Rotate the DeepInfra key** used in the previous session. It never entered
  the repository but is in that conversation transcript.
- The `jobscout` repo has three commits from a stop-hook sweep that were
  deliberately **not pushed**. Unrelated to this project.
