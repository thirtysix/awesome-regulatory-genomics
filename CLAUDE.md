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
| `docs/coverage.md` | `curation/benchmark.yaml` |
| `docs/link-check.md`, `docs/repo-review.md`, `docs/addition-review.md` | their pipeline stage |
| `docs/registry-discovery.md` | `pipeline/discover_registries.py`; promote rows into `seeds.yaml` |
| `docs/literature-discovery.md` | `pipeline/discover_literature.py`; promote rows into `seeds.yaml` |
| `docs/homepage-check.md` | `pipeline/check_homepages.py` |
| `docs/install-review.md` | `pipeline/resolve_installs.py`; promote rows into `overlay.yaml` |
| `curation/llm_proposals.yaml` | it is model output; promote things into `overlay.yaml` |
| `data/cache/citation_cache.csv` | refreshed from OpenAlex; see the citation gotchas below |

`curation/overlay.yaml`, `curation/seeds.yaml` and `curation/benchmark.yaml` are
the hand-written layer and are never overwritten.

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

## Conventions

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

**An empty citation cell has three causes and the reader cannot tell them
apart.** No paper recorded upstream (90 tools), a paper OpenAlex does not index
(7, mostly Zenodo and Bioconductor package DOIs), and a suppressed platform
paper. `citation_note` now always says which, and the site renders the blank as a
dash carrying that reason as a tooltip. Note the 90 include tools that plainly do
have papers, HOMER among them: that is a curation gap in `seeds.yaml` and
bio.tools, not a pipeline fault.

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
