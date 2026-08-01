# Working on this repository

Read this before editing. Most of the traps here are things that look fine and
are silently wrong, which is why several of them cost a rebuild to find.

## Generated files: never edit by hand

These are overwritten on every build. Edits are lost without warning.

| Generated | Edit instead |
| --- | --- |
| `README.md` | `pipeline/render.py` |
| `docs/index.html`, `docs/catalog.js` | `pipeline/render.py` |
| `data/catalog.json`, `data/catalog.tsv` | `curation/*.yaml`, then `make curate` |
| `data/excluded.json`, `data/excluded.tsv` | `curation/overlay.yaml: exclude` |
| `docs/scope-audit.md` | `pipeline/llm_assist.py --jobs audit-scope`; promote rows into `overlay.yaml: exclude` |
| `docs/coverage.md` | `curation/benchmark.yaml` |
| `docs/link-check.md`, `docs/repo-review.md`, `docs/addition-review.md` | their pipeline stage |
| `docs/registry-discovery.md` | `pipeline/discover_registries.py`; promote rows into `seeds.yaml` |
| `docs/literature-discovery.md` | `pipeline/discover_literature.py`; promote rows into `seeds.yaml` |
| `docs/homepage-check.md` | `pipeline/check_homepages.py` |
| `docs/install-review.md` | `pipeline/resolve_installs.py`; promote rows into `overlay.yaml` |
| `docs/publication-discovery.md` | `pipeline/discover_pubs.py`; promote rows into `overlay.yaml` or `seeds.yaml` |
| `docs/publication-recheck.md` | `pipeline/discover_pubs.py --recheck-flagged` |
| `docs/publication-search.md` | `pipeline/search_pubs.py`; weakest evidence in the pipeline, read before promoting |
| `docs/identifier-check.md` | `pipeline/enrich.py --check-identifiers` |
| `docs/zenodo-release.md`, `.zenodo.json`, `CITATION.cff` | hand-written; keep `version` in step with the git tag |
| `curation/llm_proposals.yaml` | it is model output; promote things into `overlay.yaml` |
| `data/cache/citation_cache.csv` | refreshed from OpenAlex; see the citation gotchas below |

`curation/overlay.yaml`, `curation/seeds.yaml`, `curation/benchmark.yaml` and
`curation/upstream-log.yaml` are the hand-written layer and are never overwritten.

## Commands

```bash
pip install -r requirements-dev.txt   # requirements.txt + pytest
make test          # unit-test the rule functions. Run this FIRST after any
                   # change to config.py, select_domain.py or resolve_repos.py
make curate        # rebuild catalog + README + site from committed data (offline)
make build-strict  # rebuild ignoring all LLM proposals
make all           # re-select, enrich, resolve repos and links, rebuild, audit
make refresh       # also re-sweep bio.tools (over an hour end to end)
make check         # sanity-check the built catalog
make serve PORT=8500   # preview the site; 8000 is often taken locally
```

Optional, needs `DEEPINFRA_API_KEY` (see `.env.example`, `docs/llm-stage.md`):
`make llm`, `make verify-additions`, `make bench`.

**Set `OPENALEX_API_KEY` in `.env` before any heavy citation work.** OpenAlex
meters free use as a daily credit budget at $0.0001 a request, resetting at
midnight UTC: **$0.10/day (~1,000 requests) anonymous, $1/day (~10,000) with a
free key** from openalex.org/settings/api. A full refresh touches ~3,700
identifiers, so the anonymous tier dies partway through and every later call
returns 429. `make enrich` prints the tier it is running on.

The `mailto` polite pool does not help here and is a different mechanism: a
request with and without one gets byte-identical rate headers. `CONTACT_EMAIL`
still matters for Crossref, which is why `polite_params()` (mailto, safe
anywhere) and `openalex_params()` (adds the key) are separate. Never put the key
in `polite_params()`: that function also feeds Crossref, and a credential
belongs only in requests to the service that issued it.

## Conventions

- **This repository is public. `nextsession.md` is the file that forgets that.**
  It is a working handoff, so it attracts whatever was on the desk at the time,
  and on 2026-08-01 it was publicly carrying the name of an unrelated private
  repository, a pointer to the machine's system-health log, an AppArmor bug, the
  phrase "the redis healthcheck credential", the local Dropbox path, and a note
  that a credential rotation was still outstanding. None of that has any value to
  a reader here. Keep the handoff to THIS project; machine-level and
  cross-project items belong in a private note. Editing the file later does not
  remove it from git history, so the discipline has to be at write time.
- **No em-dashes anywhere**, generated or hand-written. A sweep enforces this.
- Commits use `Harlan Barker <9118487+thirtysix@users.noreply.github.com>`.
  The personal address was scrubbed from history; do not reintroduce it.
- `CONTACT_EMAIL` is optional config, never hard-coded. Unset is supported: the
  `mailto` parameter is omitted rather than filled with a placeholder.

## Gotchas, each of which cost real time

**The build must converge.** `verify_additions.py` reads `data/raw/enriched.json.gz`,
NOT `data/catalog.json`. Reading the built catalog makes the pipeline oscillate:
`build.py` drops what the stage votes out, so the evidence for dropping
disappears, the next build restores it, and the catalog flips by ~57 tools
forever. After changing anything in that loop, run build/verify twice and check
the count is stable.

**`SEED_BIOTOOLS_IDS` is read from `config.py`, never from the sweep.** Reading
the sweep's stored `forced` list makes *additions* fail until a re-harvest;
unioning the two makes *removals* fail. Both happened. config is the single
source of truth in both directions.

**A matching name is necessary but never sufficient**, for repositories and for
publications alike. Tool names in this field are short and collide across all of
software: `Match` resolved to a text-matching library, `SEA` to an RPC
framework, `MEDUSA` to a genome scaffolder that shares the name. Substring
matching is worse: `cudameme` is a prefix of `cudamemeticalgorithm`. Always
require description agreement too.

**Do not put domain words in a stopword list.** `sequence`, `genome`, `motif`
and `binding` are exactly what separates a sequence-logo generator from a meme
generator. Adding them to `STOP` in `resolve_repos.py` was enough to reject the
correct answer for WebLogo.

**HTTP 429 is not a dead link.** An early link checker reported 152 broken DOIs;
151 were Crossref rate-limiting under concurrency. Only a genuine 404 counts.
Back off and honour `Retry-After`.

**GitHub search allows 30 requests/minute**, not the core API's 5,000/hour.
`resolve_repos.py` throttles to ~17/min through a single lock and caps each run
with `--search-budget`. Do not raise the concurrency.

**A resolving DOI can still be the wrong paper.** This catalog shipped ChromBPNet
pointing at "The maize cis-regulatory landscape" and i-cisTarget at a
therapeutic-peptide database, both of which resolve fine. `resolve_pubs.py`
verifies hand-written identifiers by comparing the title to the tool name.

**Citations come from the primary publication only.** Summing every linked
publication hands each member of a suite the suite's total: the EMBOSS paper is
linked to dozens of commands, the Bioconductor paper to 23 packages. Where a
primary publication is shared by three or more tools, no count is shown.

**A tool with several of its own papers gets a hand-checked list, never a rule.**
`curation/overlay.yaml: verified_publications` names the papers that genuinely
belong to one tool; `citations` shows the most-cited of them and
`citations_total` the sum, displayed as "across N papers" and never sorted on.
Every rule tried for deriving that list failed on real records. Summing the
linked list gave phantompeakqualtools the ENCODE ChIP-seq guidelines paper
(+2,244) and every Galaxy wrapper the platform's 1,965. `type: Primary` cannot
separate them because 75% of publication entries are untyped, including all
eight of the MEME Suite's. Name-in-title matching fails both ways at once: it
admits Meta-MEME and ParaMEME by substring while rejecting MEME's own 1994
paper, titled "Fitting a mixture model by expectation maximization". Two records
(ATACseqQC, COUGER) list one paper twice, and a dozen list a preprint and its
published version as separate entries, so anything that sums must dedupe.

**The suite-paper guard counts identifiers, not works.** The same paper is
reachable as both a PMID and a DOI, so its tally splits: Bioconductor is
`pmid:25633503` for 23 records and `doi:10.1038/nmeth.3252` for TransView, and
the DOI copy tallied 1, slid under the `>= 3` threshold, and made TransView the
12th most-cited entry on the Bioconductor paper's 4,023 citations. Galaxy splits
the same way. `SUITE_PUBLICATIONS` in `config.py` lists every identifier each
platform paper is reachable by; it is the publication analogue of `MONOREPOS`.

**Overriding a publication link must also move the citation count.** Setting
`publications:` in the overlay changed `row["publication"]` and left `citations`
describing the paper just rejected. Signac linked its Nature Methods paper while
reporting the bioRxiv preprint's 164 instead of 1,889; ArchR showed 74 for 1,486.

**A failed citation lookup is unknown, not zero.** The original sweep cached
lookup failures as `0`, which is indistinguishable from an uncited paper. 410 of
them were hiding real counts, including JASPAR 2018 at 0 against a true 1,615,
and they masked contamination: three out-of-scope records (`erange`, `edger`,
`express`) only became visible in the top 15 once the real numbers arrived. The
cache also held 1,126 fewer identifiers than the harvest actually uses.
`openalex_lookup()` now leaves an unresolved key absent, costing one retry.

**Citations must be fetched for what the catalog DISPLAYS, not for what the
harvest contains.** `enrich.py` iterates the bio.tools sweep, so two whole
classes of publication were never looked up and 148 tools showed a blank cell:
seed entries from `seeds.yaml`, which never appear in the sweep at all, and
preprints that `resolve_pubs.py` upgraded to their published version, where only
the preprint is in the harvest. bio.tools records Sierra as bioRxiv
`10.1101/867309`; the catalog correctly links its Genome Biology paper and showed
nothing, because that DOI was never fetched. TOBIAS, a featured tool with 251
stars, was blank for the seed reason. `enrich.displayed_identifiers()` collects
seeds, `publication_map.json` upgrades and the overlay's own lists;
`publication_map.json` is written by a later stage, so a brand-new upgrade is
picked up on the following run.

**An empty citation cell has several causes and the reader cannot tell them
apart.** `citation_note` now always says which, and the site renders the blank as
a dash carrying that reason as a tooltip. No blank is unexplained.

**`10.1101/` is not a preprint prefix.** It belongs to Cold Spring Harbor
Laboratory Press, which publishes bioRxiv *and* Genome Research, Genes &
Development, RNA and the Perspectives series. Treating the whole prefix as
bioRxiv labelled six peer-reviewed papers as preprints, RegulomeDB's Genome
Research paper among them at 2,878 citations, and also demoted them inside
`primary_identifier()`, which deliberately prefers a published version over a
preprint. `config.is_preprint()` identifies bioRxiv by the SHAPE of the suffix
(`10.1101/2024.12.25.630221`, or the legacy all-digit `10.1101/867309`) rather
than by excluding a list of journal abbreviations, because that list cannot be
known to be complete. The same audit found `10.48550/` (arXiv) missing from
build.py's list while present in resolve_pubs.py's; both now share one function.

**A recorded publication is not a verified one, and nothing was checking.** The
same cross-check that finds a missing paper also finds a wrong one, by deriving
the paper independently from the tool's own declared citation and comparing.
Applied to records that already HAD a publication it corrected eight, moving
counts in both directions: MoonlightR was carrying "Lateral lumbar interbody
fusion: a systematic review of complications", a spine-surgery review; vulcan
was carrying VIPER's paper and 1,079 citations that were not its own; RTNduals
and RTNsurvival were carrying RTN's; GOTHiC the Hi-C biology paper rather than
its method paper. Two were badly *under* counted, ChIPpeakAnno by 1,178 and
DiffBind by 2,359, because the record pointed at a protocol chapter or an
application paper instead of the tool's own.

When comparing a recorded identifier with a derived one, **compare works, not
strings.** A PMID and a DOI for the same paper look like a disagreement:
progeny's `pmid:29295995` and `doi:10.1038/s41467-017-02391-6` are one work, and
14 of 50 apparent conflicts were exactly this.

**Even a work id is not the last word: OpenAlex holds duplicates, and a PMID can
resolve to the wrong copy.** `pmid:22426492` lands on a record carrying an ACM
conference DOI and no journal source, with 290 citations, while the Nature
Methods record of the same Segway paper has 663 (a third copy has 474). The
identifier was correct and the count still understated by 373; linking the DOI
sidesteps it. **This is rare, not systematic**: a same-title sweep over the 300
most-cited entries, with Segway as a control that had to reproduce, found no
other confirmed case. Its one hit was a false positive worth knowing about, since
two genuinely different papers can share a title - CEAS published "CEAS:
cis-regulatory element annotation system" in NAR 2006 and again in Bioinformatics
2009, different PMIDs, 210 and 494 citations. Check the year and venue before
calling two records duplicates.

**A sweep whose control case fails measures nothing.** A first pass reported
"0 of 120 tools have a higher-cited duplicate", which was OpenAlex returning 429
to every request while the helper swallowed the error as an empty result. The
same shape as the link checker that once reported 152 broken DOIs, 151 of which
were rate limiting. Put a known-positive control in any sweep like this and
abort rather than report a rate when it does not reproduce. Note also that this
is where the "never cache a failure as 0" rule earns itself: six DOIs came back
empty under throttling and were left absent, so a later retry filled them in
rather than freezing six wrong zeros into the catalog.

**Searching by name is the LAST stop, never the first, and never unadjudicated.**
The rule below stands: ask the tool first. But when that runs out it leaves most
of a set unresolved - of 61 records flagged as carrying an unrelated paper, the
authoritative route resolved 8 and 53 declared nothing, mostly older tools whose
pages are gone. `search_pubs.py` (`make search-pubs`) then title-searches
OpenAlex and has a model judge each candidate against the tool's own description,
which is the check the `Match` failure lacked: a name match with nothing to
verify it against. It refuses correctly - asked about EP3 it answered "all
candidates describe the prostaglandin E receptor EP3, not a bioinformatics tool"
- and it recovered four records that were carrying the Bioconductor suite paper
rather than their own. Two guards matter. Controls: MACS must be found and a
fabricated tool given a plausible description must return NOTHING, or the run
aborts. And **a candidate can be worse than what is recorded**: the search offers
Signac its bioRxiv preprint at 164 citations over the Nature Methods paper at
1,889, which is the swap this catalog has already made once, so any candidate
that is a preprint against a published record, or carries far fewer citations, is
marked REGRESSION rather than proposed.

**To find a missing paper, ask the tool, never the literature.**
`discover_pubs.py` (`make discover-pubs`) reads each tool's own declared citation:
the Bioconductor citation page, `CITATION.cff`, `codemeta.json`, the README, then
the homepage. It never searches by name, because that is what put a text-matching
library in this catalog under `Match`. Of the 90 tools that had no publication, 24
were recovered, 32 have no article at all, and the rest are in
`docs/publication-discovery.md`. Four traps, each of which cost a rerun:

- **A DOI contains dots.** A lazy regex stopping at the first one turned every
  `10.18129/B9.bioc.<pkg>` into `10.18129/B9`, which then failed the
  self-citation test, so 31 packages with no paper were reported as recoveries.
- **`10.18129/B9.bioc.*`, Zenodo and figshare DOIs are deposits, not papers.**
  A Bioconductor page declaring only its own DOI means "cite the package", which
  is a permanent answer; Attune's README yields a figshare DOI for model weights.
  These live in `overlay.yaml: no_article` so nothing re-proposes them.
- **A citation may be stated in prose with no identifier anywhere.** HOMER is the
  case that matters: featured, 14,799 citations, and it showed blank. Its page
  says "cite the following paper: Heinz S, ..." with no DOI or PMID, its title
  carries no hint of the name, and the citation is on `homer.ucsd.edu/homer/`
  while the record points at `.../homer/motif/`. Resolving it needs a parent-path
  walk plus a Crossref reference-string query, gated on the returned title being
  mostly words from the reference asked about.
- **A period is not the end of a reference.** Matching `[^.]{0,500}` after "cite"
  truncated HOMER at "Bertolino E et al." - precisely before the title - leaving a
  query with authors and no title, which silently found nothing.

The declared citation can also be the wrong thing to record: `rmspc` declares the
MSPC paper it wraps, and `consensusSeekeR` a t-mixture statistics paper. Read the
title before promoting a row.

**A wrong publication identifier can be a typo, not a wrong choice of paper.**
bio.tools records NOBAI as `pmid:18449469`, which resolves cleanly to
"Ellipsoidal particles at fluid interfaces" in European Physical Journal E and
handed the tool that paper's 146 citations against a true 15. The correct PMID is
`18448469`: one transposed digit, and both resolve, so nothing that checks
"does this identifier resolve" can see it. It surfaced only because the scope
audit read the description and the paper together and said they disagree.
Searching for more of these: comparing the tool name against the paper title
finds nothing useful, because bioinformatics papers routinely have descriptive
titles that never name the tool (HOMER's is "Simple Combinations of
Lineage-Determining Transcription Factors...", DiffBind's is about oestrogen
receptor binding in breast cancer) - 100 records fail that test and were all
correct. Scanning publication VENUES for fields alien to genomics found 12, all
of them legitimate methods papers in chemistry-flavoured journals. So NOBAI looks
isolated rather than systematic, but note that both detectors are weak and this
is "nothing else surfaced", not "nothing else exists".

**One EDAM operation is not enough to admit a record.** 599 of the catalog's
entries were selected by a single `operation:` match with nothing corroborating
it, and EDAM is wrong often enough that this let in a cytochrome-P450 inhibition
predictor on `Promoter prediction`, a protein beta-strand predictor on the same
tag, a small-molecule docking tool on `Transcription factor binding site
prediction`, and a microtubule-associated-protein database on `Sequence motif
discovery`. Re-read by two models on 2026-07-31 against their descriptions and
papers, **250 were called out of scope by both**: T-cell receptor databases,
peptide toxicity predictors, cell-image segmentation, and one record whose linked
paper is colloid physics. 187 non-RNA ones were excluded; the RNA-level group
(63) was deliberately kept, since whether post-transcriptional regulation belongs
here is a scope decision rather than an error. This is the same lesson as "a
matching name is necessary but never sufficient", applied to selection: the
existing hand-written exclusions were already this exact class of finding
("General-purpose sequence analysis suite; tagged Sequence motif discovery
upstream"), just found one at a time. `make audit-scope` writes
`docs/scope-audit.md`; the sweep aborts unless four control records classify
correctly first, and only proposes a drop where two different models agree.

**An exclusion must archive the record, not just the id.** Dropping a tool is a
judgement that gets revisited, and revisiting it should not need a re-harvest.
`build.py` writes every overlay-excluded record to `data/excluded.json` and
`data/excluded.tsv` with the full row it had when dropped - description, links,
categories, citation count. Reinstating one is deleting its id from
`overlay.yaml: exclude` and rebuilding. Note `exclude` is keyed by **biotoolsID**,
not by catalog id; they differ often enough to matter.

**The describe stage must read the HARVEST, not the built catalog.** The
convergence trap again, in the stage the `verify_additions.py` note did not
cover. `llm_assist.py` read `data/catalog.json` for its input text, and
`build.py` had already merged the previous run's rewrite into that file, so the
second `make llm` rewrote a rewrite. For 1,407 of 1,563 records the `was:` field
in `llm_proposals.yaml` therefore held generation 1's output, not the bio.tools
original: MACS's true source is "Model-based Analysis of ChIP-seq data.", while
`was:` claimed "Calls peaks from ChIP-seq data using a model-based approach",
which is what run 1 produced. Nothing was lost, because the originals live in
`enriched.json.gz`, but the audit trail said otherwise and the handoff notes
repeated the claim. `source_descriptions()` now reads the harvest. Cost of the
extra generation, measured: 492 records changed, 75 gained a claim the source
does not make, and 45 of those were cases where run 1 had correctly returned the
source verbatim. ePIANNO went from the accurate "ePIgenomics ANNOtation tool." to
the invented "Analyses and classifies genetic variants from ChIP-seq and GWAS
data".

**Never let a model fill a thin description from EDAM terms.** The describe
prompt was handed each record's EDAM operations, which this repository documents
at length as unreliable. When the prose source was a fragment - 223 of them were
under 80 characters - the model padded the sentence out of those tags, and the
result reads as authoritative. h4HiChIP-Peaks was described as calling peaks
"using an essential dynamics algorithm", a protein molecular-dynamics technique
present only as a wrong EDAM operation. COMAN, a metatranscriptomics web server
whose entire bio.tools text is "Comprehensive metatranscriptomics analysis.", was
described as predicting transcriptional regulatory elements, that being its one
(wrong) EDAM operation. HOT and ePIANNO were invented the same way, and ReMap got
a full description built on a source reading "THIS PAGE IS DEPRECATED, GO TO ...".
365 descriptions (23%) carried at least one claim traceable only to an EDAM term.
The prompt now names EDAM as unreliable, forbids a capability resting on a tag
alone, and permits `{"description": null}` instead of a guess.

**To describe a tool whose registry text is too thin, ask its paper.** The same
move as `discover_pubs.py`: go to the source that knows. 98% of catalogued tools
have a publication and 90% now have its abstract stored, including 218 of the 223
whose bio.tools text was a fragment, which is almost exactly the failing set.
Feeding title and abstract to the describe stage fixed every confirmed error:
ARACNE moved from "using network deconvolution" - a phrase the source uses only
for the general problem class - to "using an information theoretic approach to
eliminate indirect interactions", which is the actual method; cLoops2 recovered
the word "loops" a tag-derived rewrite had dropped. Two traps while doing it.
**An abstract's findings are not the tool's features**: TOBIAS was described as
predicting "transcription factor binding kinetics" because its paper title says
footprinting unravels binding kinetics; the tool does footprinting. And
**`_identifiers` is not the tool's publication list** - it holds what the harvest
mentioned, so a paper recovered by `discover_pubs.py` or set in the overlay is
absent from it. HOMER, featured and second most-cited, carries its DOI in
`publication` with an empty `_identifiers` and drew on no paper at all until
`paper_context()` learned to try both.

**Store the whole OpenAlex response, not the fields you need today.**
`openalex_lookup()` was already fetching the complete work object and keeping
four fields, so abstracts arrived and were discarded on every run. Recovering
them meant a second pass over 2,231 identifiers against a metered daily budget,
for data already paid for. `save_openalex_work()` now writes the full response
gzipped to `data/cache/openalex/` (6.6x, 41 MB for the full set, gitignored), and
`abstract_text()` rebuilds prose from OpenAlex's inverted index. Keep
`enrich.py --backfill-works` an explicit flag rather than folding it into
`make enrich`: a citation count already in the cache short-circuits before the
network, so a silent re-fetch would be a surprise 2,000-request sweep spending
most of a day's allowance.

**A stated length rule is not the rule that binds.** The describe prompt said
"8-22 words" and the validator allowed 4-40. Actual output: median 11, maximum
19, and 96 descriptions below the stated floor. Nothing ever approached the
ceiling, so raising it alone changes nothing; what governs length is "one
sentence" plus the terseness instruction. Meanwhile 461 tools had a source of 40+
words (median 35 content words) compressed into 11, which is where detail was
lost. Check the distribution before tuning a limit.

**Writing to bio.tools: four behaviours that will bite automation.** Verified by
a staged pilot on 2026-08-01, one change at a time.

- **A write can return HTTP 500 and still succeed.** Three of four writes did:
  the POST that registered TFBSFootprinter, and the PUTs to deepcyps and
  enhanceratlas. The data landed correctly every time and only the response
  rendering failed. Never branch on the status code; GET the record back and
  read the field. Retrying on 500 would double-write, and a retry that varied
  the `biotoolsID` would have created a duplicate entry.
- **Read shape is not write shape.** A GET returns `null` for empty fields and
  the validator rejects nulls, so a record cannot be round-tripped without
  recursively stripping nulls and empty values first. Also strip the
  server-managed fields: `additionDate`, `lastUpdate`, `owner`, `validated`,
  `homepage_status`, `confidence_flag`.
- **`/api/tool/validate/` is create-only**, so on an existing record the only
  error it can return is a spurious "ID already exists". There is no dry run for
  an update. It also renders HTML unless you pass `?format=json`, which reads
  like a missing endpoint.
- **`/api/request/` is read-only.** It lists sent and received edit requests but
  `POST` returns 405, so edit rights can only be requested through the button on
  the tool card. `collectionID` must be omitted rather than sent empty, and
  `biotoolsID` must be supplied rather than derived from the name.

**Keep the whole original, not just the field you changed.** bio.tools has no
version history and no undo, so if an edit turns out wrong the only way back is a
copy kept beforehand. `curation/upstream-snapshots/` holds the complete record as
it stood immediately before each edit; the ledger's `before:` says what changed,
the snapshot holds everything that did not, which is what a restore needs.
`pipeline/biotools_edit.py` writes the snapshot before it will submit anything
and `--restore` puts it back. `make verify-upstream` marks any logged edit whose
snapshot is missing as NO SNAPSHOT, because an edit that cannot be undone is a
different risk from one that can.

**bio.tools records no contribution history.** An edit to a record you do not own
appears nowhere in your profile: the account lists only `resources` you own, and
the record itself stores `lastUpdate` with no editor and no diff. The correction
to deepcyps is invisible everywhere except `curation/upstream-log.yaml`, which is
why that file is hand-written and tracked. `make verify-upstream` reads it back
against the live registry and reports anything that has been reverted.

**`homepage_status` is bio.tools' own dead-link flag, and it is not writable.**
Setting it on a record you own returns 200 and changes nothing, so it is computed
by their monitor. It is also barely populated: 13 records across the harvest carry
a non-zero value, while a link check found 130 homepages returning 404 or 410. So
the useful contribution is to report dead links into that mechanism rather than to
edit records. Do not simply delete a dead URL either: it still carries the
institution and path that let a reader find where a resource moved. EnhancerAtlas
was repointed from a 404 page to its live root, which is the shape to prefer.

**bio.tools `operation=` and `q=` are fuzzy text search, not ontology lookup.**
Always quote the value. `q="cis-regulatory"` returns 107 records; unquoted it
returns about 3,500, matching "cis" OR "regulatory".

**Two of the README's own examples of bad EDAM annotation were themselves
wrong**, and both were caught only by querying the live API rather than
believing the doc. There is no bio.tools record for the MEME Suite's FIMO: the
ID `fimo` is FiMO, an unrelated genotyping tool, so "FIMO is filed under
Genotyping" was a name collision. MACS is annotated `Peak calling` and always
was, not "Modelling and simulation". Verified examples, safe to reuse: HOCOMOCO
under `Data handling`, SICER under `Sequence contamination filtering`,
ChIP-Atlas under `Genome assembly`, Cluster Buster under `Document clustering`.

**A monorepo is not a tool's repository.** bio.tools records hgv_pass with a
homepage of `github.com/galaxyproject/galaxy`, so it inherited the whole Galaxy
project's 1,818 stars and became the most-starred entry in the catalog, ahead of
MACS. `build.is_monorepo()` drops the link and everything derived from it;
`MONOREPOS` in `config.py` is the list. Dropping the URL alone is not enough:
the stars, activity, licence and language all come from `_github` and survive
the link that justified them.

**Syntax-check the site JavaScript before shipping.** It is generated as a Python
string, so an apostrophe in the prose terminates a JS string literal and ships a
blank page. Extract the inline `<script>` blocks and run them under `node` with a
stubbed DOM; this has caught a blank page once already.

**Three vocabulary traps found while widening the scope on 2026-07-28.**
`Hi-C` is a technology, not a field: genome assemblies are scaffolded with it,
so putting it in the strong tier admitted "A high-quality genome sequence of
alkaligrass". It lives in `KEEP_TEXT_PATTERNS`, needing a domain topic.
`Loop modelling`, `Gene expression QTL analysis` and `Bisulfite mapping` are
EDAM operations that look decisive and are not: bio.tools attaches them to RNA
secondary structure, expression atlases and general commercial suites. They
admit nothing, not even with topic corroboration. And `methylation` alone spans
three fields, so only DNA-specific wording (bisulfite, WGBS, methylome, DMR,
Bis-seq) admits.

**The pipeline order is select -> enrich -> build.** Changing `select_domain.py`
or the `config.py` rules and then running `make build` uses the PREVIOUS
`enriched.json.gz`, so the change appears not to have worked. Re-run
`make enrich` in between; it is cached, so only the new records cost anything.

**`pkill -f "http.server 8000"` matches your own shell** and kills it. Use the
bracket trick (`[h]ttp.server`) or kill by PID.

## Scope

In scope: transcription-factor binding and motifs, promoters and enhancers,
footprinting, ChIP/ATAC peak calling and annotation, chromatin accessibility and
nucleosomes, gene-regulatory networks, regulatory variant effect, and the
databases serving those. **Widened 2026-07-28** to DNA methylation, the 3D
genome (Hi-C, HiChIP, loops, TADs), histone modifications, reporter assays
(MPRA/STARR-seq) and molecular QTL (eQTL, caQTL).

Out: general alignment and assembly, RNA structure, protein structure and
docking, mass spectrometry, proteomics, metabolomics, phylogenetics, and generic
differential-expression tooling, even when they share vocabulary like "motif",
"peak" or "binding". Also out, and newly enforced: RNA modification
(m6A/m5C/pseudouridine), protein methylation, and genome-announcement papers. The rules live in `pipeline/config.py`; rejected records are
written to `data/raw/rejected.json` so the boundary can be argued with.
