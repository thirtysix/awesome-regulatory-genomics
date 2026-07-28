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
| `curation/llm_proposals.yaml` | it is model output; promote things into `overlay.yaml` |

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

**Syntax-check the site JavaScript before shipping.** It is generated as a Python
string, so an apostrophe in the prose terminates a JS string literal and ships a
blank page. Extract the inline `<script>` blocks and run them under `node` with a
stubbed DOM; this has caught a blank page once already.

**`pkill -f "http.server 8000"` matches your own shell** and kills it. Use the
bracket trick (`[h]ttp.server`) or kill by PID.

## Scope

In scope: transcription-factor binding and motifs, promoters and enhancers,
footprinting, ChIP/ATAC peak calling and annotation, chromatin accessibility and
nucleosomes, gene-regulatory networks, regulatory variant effect, and the
databases serving those.

Out: general alignment and assembly, RNA structure, protein structure and
docking, mass spectrometry, proteomics, metabolomics, phylogenetics, and generic
differential-expression tooling, even when they share vocabulary like "motif",
"peak" or "binding". The rules live in `pipeline/config.py`; rejected records are
written to `data/raw/rejected.json` so the boundary can be argued with.
