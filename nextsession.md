# Next session

**Last updated:** 2026-07-31
**Start with:** `CLAUDE.md` (traps and generated-file rules), then `ROADMAP.md`.
Memory notes: `[[awesome-regulatory-genomics]]`, `[[biotools-edam-annotations-unreliable]]`,
`[[verify-inferred-data-not-just-resolvable]]`, `[[upstream-fields-can-be-populated-and-wrong]]`,
`[[dashboard-figures-live-outside-the-repo]]`.

## Current state

- **Public** at https://github.com/thirtysix/awesome-regulatory-genomics
- **Site live** at https://thirtysix.github.io/awesome-regulatory-genomics/
- **Working tree clean, `main` level with `origin/main` at `62f7e08`.** Nine commits this
  session, all pushed. 131 tests pass; three consecutive builds byte-identical.
- Credentials: none in the repo. **`OPENALEX_API_KEY` is now read** alongside the optional
  `DEEPINFRA_API_KEY` and `CONTACT_EMAIL`, all documented in `.env.example`; `.env` is
  gitignored.

## Headline results

**1,948 tools** (three out-of-scope records removed) across 20 categories. This session was
about the *citation* column being wrong rather than about growing the catalog.

- **Total citations 184,650 -> 275,704.** 880 tools have a different count.
- **Unexplained blank citation cells: 47 -> 0.** Every blank now states its cause.
- **38 tools carry a hand-verified multi-paper total** (`citations_total`, displayed as
  "across N papers", never sorted on).
- **HOMER went from blank to 14,799**, now the second most-cited entry.
- **Download button** on the site: the visible, filtered, sorted table as TSV, 34 columns.

## What changed this session

Nine commits. `ROADMAP.md` has the detail; the shape of it:

1. **A tool can have more than one paper of its own.** `verified_publications` in
   `overlay.yaml` - 37 hand-checked lists over 106 papers. No rule works; see CLAUDE.md.
2. **Fetch citations for what the catalog SHOWS, not what the sweep holds.** Seeds and
   preprint-upgraded DOIs were never looked up: 148 blanks, TOBIAS and Sierra among them.
3. **Ask the tool for its paper, not the literature.** New `discover_pubs.py` /
   `make discover-pubs`, reading each tool's own declared citation.
4. **`10.1101` is Cold Spring Harbor, not bioRxiv.** `config.is_preprint()`.
5. **A recorded publication is not a verified one.** 15 wrong papers corrected, in both
   directions (MoonlightR was citing a spine-surgery review; ChIPpeakAnno was undercounted
   by 1,178).
6. **OpenAlex API key support**, and a clean stop when the daily budget is spent.
7. **New columns:** publication title, venue, URL, pmid, doi.
8. **Paper-title tooltip** on the site; `citations_last_full_year`, `citations_per_year`,
   `categories_n` in the download.

## Gotchas discovered this session

All written up in `CLAUDE.md` with the evidence. Short forms:

- **Never cache a failed lookup as `0`.** 410 zeros were hiding real counts (JASPAR 2018 at 0
  against a true 1,615), and worse, they *suppressed* the ranking signal that would have
  exposed three out-of-scope tools sitting in the top 15. This earned itself twice: when
  OpenAlex throttled us mid-session, six DOIs came back empty and a later retry filled them in
  rather than freezing six wrong zeros into the catalog.
- **A sweep whose control case fails measures nothing.** A duplicate-work sweep reported
  "0 of 120" that was really OpenAlex answering 429 to every request while the helper
  swallowed the error. Put a known-positive control in any sweep like this and abort rather
  than report a rate.
- **Compare works, not identifier strings.** A PMID and a DOI for the same paper look like a
  disagreement; 14 of 50 apparent conflicts were exactly that.
- **OpenAlex holds duplicate records**, and a PMID can resolve to the wrong copy:
  `pmid:22426492` lands on a record carrying an ACM DOI with 290 citations while the Nature
  Methods record of the same Segway paper has 663. Rare rather than systematic - a controlled
  sweep over the 300 most-cited found no other confirmed case.
- **Two records can share a title and be different papers.** CEAS published under the same
  title in NAR 2006 and Bioinformatics 2009. Check year and venue before calling them dupes.
- **The suite-paper guard counted identifiers, not works.** Bioconductor is `pmid:25633503`
  for 23 records and `doi:10.1038/nmeth.3252` for TransView, so the DOI copy tallied 1 and
  slid under the `>= 3` threshold. `SUITE_PUBLICATIONS` in `config.py` now lists every
  identifier each platform paper is reachable by.
- **OpenAlex meters a daily credit budget, not a rate:** $0.10/day anonymous against $1/day
  with a free key. The `mailto` polite pool buys nothing there any more (byte-identical rate
  headers with and without) - that is a Crossref mechanism now.

## Possible next steps

None committed; ask the user.

- **30 tools still have no publication** (was 90). `docs/publication-discovery.md` holds the
  candidates. Genrich and SnapATAC2 are the two worth a hand lookup; most of the rest are web
  services and MATLAB File Exchange entries that genuinely have no paper.
- **Descriptions were audited and regenerated on 2026-07-31.** See the session notes above;
  the claim previously recorded here, that "every original is recoverable from `was:`", was
  **wrong** - `was:` held the previous LLM rewrite for 1,407 of 1,563 rows. Originals live in
  `data/raw/enriched.json.gz`, which is now what the stage reads. A revert to bio.tools
  originals remains a mechanical join if ever wanted.
- Older follow-ups still open below in `ROADMAP.md`: 2b (registry candidates), 4b (benchmark
  misses), 7b (preprints and licences), the deferred curation block, and the ~940 unsearched
  repo-less records.

## Outstanding, needs the user

- Credential rotation for the optional model stages is tracked outside this repository.
- Machine-level and cross-project items are tracked outside this repository.

<!-- This file is a working handoff, not documentation. Keep it to THIS project.
     Anything about the machine, other repositories, or credentials belongs in a
     private note: the repository is public, and git history is not scrubbed by
     editing a file later. -->
