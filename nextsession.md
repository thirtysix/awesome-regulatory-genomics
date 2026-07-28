# Next session

**Last updated:** 2026-07-28
**Start with:** `CLAUDE.md` (traps and generated-file rules), then `ROADMAP.md`.
Memory notes: `[[awesome-regulatory-genomics]]`, `[[biotools-edam-annotations-unreliable]]`,
`[[verify-inferred-data-not-just-resolvable]]`.

## Current state

- **Public** at https://github.com/thirtysix/awesome-regulatory-genomics
- **Site live** at https://thirtysix.github.io/awesome-regulatory-genomics/
  (Pages enabled with GitHub Actions as source; first deploy succeeded)
- Local path: `~/Dropbox/manuscripts/0.datasets_visualizations/002.AI_projects/awesome-regulatory-genomics`
  (moved here from `000.dissertation/analyses/biotools_tables/` on 2026-07-28;
  nothing was path-dependent, a full rebuild produced no diff)
- Working tree clean, `main` level with `origin/main`
- Credentials: none in the repo. `DEEPINFRA_API_KEY` and `CONTACT_EMAIL` are
  optional, documented in `.env.example`, and `.env` is gitignored

## Headline results

1,800 tools, benchmark recall 89/89. 950 have a source repository (873 recorded
upstream, 27 hand-verified, 50 inferred and marked as such). Publication links:
1,615 peer-reviewed, 144 labelled preprint, 41 none.

The dissertation table this grew from was verified field by field and matched
exactly. Its approach missed roughly nine in ten relevant tools, for three
documented reasons: planned queries never run, unreliable EDAM annotations, and
bio.tools simply not indexing a third of the field.

## Gotchas discovered this session

Full list with detail in `CLAUDE.md`. The ones most likely to bite again:

- **The build oscillated by 57 tools forever** because `verify_additions.py`
  judged the catalog that `build.py` had already pruned, so dropping a record
  removed the evidence for dropping it. It now reads the pre-drop selected set.
  After touching that loop, run build/verify twice and confirm the count is stable.

- **A resolving DOI can be the wrong paper.** Five hand-written citations were
  wrong, four of which resolved perfectly. One was invented outright. Verifying
  that a DOI *resolves* is not verification; compare the title to the tool.

- **A matching name is never sufficient**, for repositories or publications.
  Substring matching is worse than useless: `cudameme` prefixes
  `cudamemeticalgorithm`.

- **Domain words must not go in a stopword list.** Adding `sequence` and `genome`
  to `STOP` rejected the correct WebLogo repository, the case that prompted the
  work.

- **HTTP 429 is not a dead link.** 151 of 152 "broken" DOIs were Crossref
  rate-limiting.

- **Generated JS needs a syntax check.** An apostrophe in prose terminated a
  JavaScript string and would have shipped a blank dashboard.

- **GitHub search is 30 req/min**, not 5,000/hour. Throttled to ~17/min behind a
  single lock, budget-capped per run.

## Possible next steps

None committed; ask the user. In rough order of value:

1. Unit tests for `classify()`, `validate()`, `primary_identifier()` — every bug
   this project has had lived in those three functions and none are tested.
2. Further `make repos` runs for the ~940 records never reached by search.
3. Human review of `docs/repo-review.md` (235) and `docs/addition-review.md` (147).
4. Watch the first automated refresh on 1 August 2026, 04:00 UTC.

## Outstanding, needs the user

- **Rotate the DeepInfra key** used this session. It never entered the repository
  but is in the conversation transcript.
- The `jobscout` repo has three commits from a stop-hook sweep that were
  deliberately **not pushed**. Unrelated to this project.
