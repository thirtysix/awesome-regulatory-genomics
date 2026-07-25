# Awesome Regulatory Genomics

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re) [![Tools](https://img.shields.io/badge/tools-1741-blue)](https://thirtysix.github.io/awesome-regulatory-genomics/) [![License: CC BY 4.0](https://img.shields.io/badge/data-CC--BY--4.0-lightgrey)](LICENSE-DATA) [![Updated](https://img.shields.io/badge/updated-2026--07--25-brightgreen)](#)

A catalog of tools, databases and methods for **transcription-factor binding, sequence motifs, regulatory elements, chromatin and gene-regulatory networks**.

**[Browse and search all 1741 tools →](https://thirtysix.github.io/awesome-regulatory-genomics/)** — filter by category, tool type, language, licence, activity and citations.

This list is *generated and then curated*. A reproducible pipeline harvests [bio.tools](https://bio.tools), resolves source repositories, and pulls citation counts and repository activity; a hand-written overlay adds tools bio.tools does not index and promotes the entries below. Everything is rebuildable with `make all` — see [How this list is built](#how-this-list-is-built).

## Contents

- [Motif discovery](#motif-discovery) — 186 tools
- [Motif scanning & enrichment](#motif-scanning--enrichment) — 237 tools
- [Motif comparison & visualisation](#motif-comparison--visualisation) — 42 tools
- [Motif & TF databases](#motif--tf-databases) — 119 tools
- [TFBS prediction](#tfbs-prediction) — 750 tools
- [Promoter & enhancer prediction](#promoter--enhancer-prediction) — 472 tools
- [Footprinting](#footprinting) — 35 tools
- [Peak calling](#peak-calling) — 573 tools
- [Peak annotation & differential binding](#peak-annotation--differential-binding) — 23 tools
- [ChIP/ATAC data resources](#chipatac-data-resources) — 63 tools
- [Gene regulatory networks](#gene-regulatory-networks) — 395 tools
- [Regulatory variant effect](#regulatory-variant-effect) — 30 tools
- [Nucleosome & chromatin state](#nucleosome--chromatin-state) — 356 tools
- [Single-cell regulatory genomics](#single-cell-regulatory-genomics) — 99 tools
- [Comparative & evolutionary](#comparative--evolutionary) — 38 tools
- [How this list is built](#how-this-list-is-built)
- [Coverage and known gaps](#coverage-and-known-gaps)
- [Contributing](#contributing)

## Motif discovery

*De novo discovery of sequence motifs from sets of sequences or peaks.*

- **[JASPAR](http://jaspar.genereg.net/)** — The default open motif database; six taxonomic groups, versioned releases — [code](https://github.com/asntech/pyjaspar) · [bio.tools](https://bio.tools/jaspar) · [paper](https://pubmed.ncbi.nlm.nih.gov/34850907/) `★38 | 8,544 cites`
- **[RSAT suite](http://rsat.eu)** — Long-running suite covering matrix scanning, comparison and enrichment — [bio.tools](https://bio.tools/rsat) · [paper](https://pubmed.ncbi.nlm.nih.gov/10641039/) `1,770 cites`
- **[TFBSTools](http://bioconductor.org/packages/release/bioc/html/TFBSTools.html)** — R interface to motif matrices, scanning and JASPAR — [code](https://github.com/ge11232002/TFBSTools) · [bio.tools](https://bio.tools/tfbstools) · [paper](https://pubmed.ncbi.nlm.nih.gov/26794315/) `★37 | 349 cites`
- **[BPNet](https://github.com/kundajelab/bpnet)** — Base-resolution TF binding model that recovers motif syntax — [code](https://github.com/kundajelab/bpnet) · [paper](https://doi.org/10.1038/s41588-021-00782-6)
- **[homer](http://homer.ucsd.edu/homer/motif/)** — Motif discovery plus peak annotation; the pragmatic first stop for ChIP-seq — [bio.tools](https://bio.tools/homer)

<sub>[+ 181 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=motif-discovery)</sub>

## Motif scanning & enrichment

*Scanning sequences with known matrices; motif enrichment and over-representation.*

- **[TFBSTools](http://bioconductor.org/packages/release/bioc/html/TFBSTools.html)** — R interface to motif matrices, scanning and JASPAR — [code](https://github.com/ge11232002/TFBSTools) · [bio.tools](https://bio.tools/tfbstools) · [paper](https://pubmed.ncbi.nlm.nih.gov/26794315/) `★37 | 349 cites`
- **[FIMO](https://meme-suite.org/meme/tools/fimo)** — Standard scanner for known motifs with calibrated p-values — [code](https://github.com/cinquin/MEME) · [paper](https://doi.org/10.1093/bioinformatics/btr064)
- **[homer](http://homer.ucsd.edu/homer/motif/)** — Motif discovery plus peak annotation; the pragmatic first stop for ChIP-seq — [bio.tools](https://bio.tools/homer)
- **[motifmatchr](https://bioconductor.org/packages/motifmatchr/)** — Fast motif matching over large genomic range sets — [code](https://github.com/GreenleafLab/motifmatchr) · [paper](https://doi.org/10.18129/B9.bioc.motifmatchr)

<sub>[+ 233 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=motif-scanning)</sub>

## Motif comparison & visualisation

*Comparing, clustering, aligning and drawing motifs and logos.*

<sub>[42 tools in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=motif-comparison)</sub>

## Motif & TF databases

*Curated collections of binding profiles, TF families and TF-target relationships.*

- **[JASPAR](http://jaspar.genereg.net/)** — The default open motif database; six taxonomic groups, versioned releases — [code](https://github.com/asntech/pyjaspar) · [bio.tools](https://bio.tools/jaspar) · [paper](https://pubmed.ncbi.nlm.nih.gov/34850907/) `★38 | 8,544 cites`
- **[ReMap](https://remap.univ-amu.fr/)** — Large-scale atlas of regulatory regions from public DNA-binding experiments — [bio.tools](https://bio.tools/inserm-remap) · [paper](https://pubmed.ncbi.nlm.nih.gov/25477382/) `1,069 cites`
- **[GTRD](http://gtrd.biouml.org/)** — Uniformly reprocessed ChIP-seq with meta-clusters of TF binding sites — [bio.tools](https://bio.tools/gtrd) · [paper](https://pubmed.ncbi.nlm.nih.gov/33231677/) `306 cites`
- **[CIS-BP](http://cisbp.ccbr.utoronto.ca/)** — Motif inference across species by DNA-binding-domain similarity — [paper](https://doi.org/10.1016/j.cell.2014.08.009)
- **[HOCOMOCO](https://hocomoco.autosome.org)** — Human and mouse motifs derived from uniform ChIP-seq reprocessing — [bio.tools](https://bio.tools/hocomoco) · [paper](https://pubmed.ncbi.nlm.nih.gov/29140464/)

<sub>[+ 114 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=motif-databases)</sub>

## TFBS prediction

*Predicting transcription-factor binding sites, including sequence-based ML models.*

- **[JASPAR](http://jaspar.genereg.net/)** — The default open motif database; six taxonomic groups, versioned releases — [code](https://github.com/asntech/pyjaspar) · [bio.tools](https://bio.tools/jaspar) · [paper](https://pubmed.ncbi.nlm.nih.gov/34850907/) `★38 | 8,544 cites`
- **[SCENIC](http://scenic.aertslab.org)** — Single-cell regulatory network inference; regulons rather than raw correlations — [code](https://github.com/aertslab/SCENIC) · [bio.tools](https://bio.tools/scenic) · [paper](https://pubmed.ncbi.nlm.nih.gov/28991892/) `★491 | 4,807 cites`
- **[RSAT suite](http://rsat.eu)** — Long-running suite covering matrix scanning, comparison and enrichment — [bio.tools](https://bio.tools/rsat) · [paper](https://pubmed.ncbi.nlm.nih.gov/10641039/) `1,770 cites`
- **[ReMap](https://remap.univ-amu.fr/)** — Large-scale atlas of regulatory regions from public DNA-binding experiments — [bio.tools](https://bio.tools/inserm-remap) · [paper](https://pubmed.ncbi.nlm.nih.gov/25477382/) `1,069 cites`
- **[TFBSTools](http://bioconductor.org/packages/release/bioc/html/TFBSTools.html)** — R interface to motif matrices, scanning and JASPAR — [code](https://github.com/ge11232002/TFBSTools) · [bio.tools](https://bio.tools/tfbstools) · [paper](https://pubmed.ncbi.nlm.nih.gov/26794315/) `★37 | 349 cites`
- **[TOBIAS](https://github.com/loosolab/TOBIAS)** — Differential ATAC-seq footprinting between conditions — [code](https://github.com/loosolab/TOBIAS) · [bio.tools](https://bio.tools/TOBIAS) · [paper](https://doi.org/10.1101/869560) `★251 | 8 cites`
- **[UniBind](https://unibind.uio.no/)** — TFBS predictions restricted to ChIP-seq-supported, high-confidence sites — [code](https://bitbucket.org/CBGR/unibind_enrichment/) · [bio.tools](https://bio.tools/unibind) · [paper](https://doi.org/10.1101/2020.11.17.384578) `7 cites`
- **[BPNet](https://github.com/kundajelab/bpnet)** — Base-resolution TF binding model that recovers motif syntax — [code](https://github.com/kundajelab/bpnet) · [paper](https://doi.org/10.1038/s41588-021-00782-6)
- **[Enformer](https://github.com/google-deepmind/deepmind-research/tree/master/enformer)** — Long-range sequence-to-expression model; a common baseline for regulatory prediction — [code](https://github.com/google-deepmind/deepmind-research) · [paper](https://doi.org/10.1038/s41592-021-01252-x)
- **[TFBSFootprinter](https://github.com/thirtysix/TFBS_footprinting)** — Multi-evidence TFBS scoring combining conservation, CAGE, eQTL and chromatin data — [code](https://github.com/thirtysix/TFBS_footprinting) · [paper](https://doi.org/10.3389/fbinf.2022.910346)

<sub>[+ 740 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=tfbs-prediction)</sub>

## Promoter & enhancer prediction

*Prediction and annotation of promoters, enhancers and other cis-regulatory elements.*

- **[RSAT suite](http://rsat.eu)** — Long-running suite covering matrix scanning, comparison and enrichment — [bio.tools](https://bio.tools/rsat) · [paper](https://pubmed.ncbi.nlm.nih.gov/10641039/) `1,770 cites`
- **[TFBSTools](http://bioconductor.org/packages/release/bioc/html/TFBSTools.html)** — R interface to motif matrices, scanning and JASPAR — [code](https://github.com/ge11232002/TFBSTools) · [bio.tools](https://bio.tools/tfbstools) · [paper](https://pubmed.ncbi.nlm.nih.gov/26794315/) `★37 | 349 cites`
- **[UniBind](https://unibind.uio.no/)** — TFBS predictions restricted to ChIP-seq-supported, high-confidence sites — [code](https://bitbucket.org/CBGR/unibind_enrichment/) · [bio.tools](https://bio.tools/unibind) · [paper](https://doi.org/10.1101/2020.11.17.384578) `7 cites`
- **[Enformer](https://github.com/google-deepmind/deepmind-research/tree/master/enformer)** — Long-range sequence-to-expression model; a common baseline for regulatory prediction — [code](https://github.com/google-deepmind/deepmind-research) · [paper](https://doi.org/10.1038/s41592-021-01252-x)
- **[homer](http://homer.ucsd.edu/homer/motif/)** — Motif discovery plus peak annotation; the pragmatic first stop for ChIP-seq — [bio.tools](https://bio.tools/homer)

<sub>[+ 467 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=regulatory-elements)</sub>

## Footprinting

*DNase/ATAC digital footprinting and phylogenetic footprinting.*

- **[TOBIAS](https://github.com/loosolab/TOBIAS)** — Differential ATAC-seq footprinting between conditions — [code](https://github.com/loosolab/TOBIAS) · [bio.tools](https://bio.tools/TOBIAS) · [paper](https://doi.org/10.1101/869560) `★251 | 8 cites`
- **[TFBSFootprinter](https://github.com/thirtysix/TFBS_footprinting)** — Multi-evidence TFBS scoring combining conservation, CAGE, eQTL and chromatin data — [code](https://github.com/thirtysix/TFBS_footprinting) · [paper](https://doi.org/10.3389/fbinf.2022.910346)

<sub>[+ 33 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=footprinting)</sub>

## Peak calling

*Calling enriched regions from ChIP-seq, ATAC-seq, CUT&RUN and related assays.*

- **[ReMap](https://remap.univ-amu.fr/)** — Large-scale atlas of regulatory regions from public DNA-binding experiments — [bio.tools](https://bio.tools/inserm-remap) · [paper](https://pubmed.ncbi.nlm.nih.gov/25477382/) `1,069 cites`
- **[TOBIAS](https://github.com/loosolab/TOBIAS)** — Differential ATAC-seq footprinting between conditions — [code](https://github.com/loosolab/TOBIAS) · [bio.tools](https://bio.tools/TOBIAS) · [paper](https://doi.org/10.1101/869560) `★251 | 8 cites`
- **[UniBind](https://unibind.uio.no/)** — TFBS predictions restricted to ChIP-seq-supported, high-confidence sites — [code](https://bitbucket.org/CBGR/unibind_enrichment/) · [bio.tools](https://bio.tools/unibind) · [paper](https://doi.org/10.1101/2020.11.17.384578) `7 cites`
- **[ChIP-Atlas](https://chip-atlas.org)** — Reprocessed public ChIP-seq, ATAC-seq and Bisulfite-seq across six organisms — [code](https://github.com/inutano/chip-atlas) · [bio.tools](https://bio.tools/chip-atlas) · [paper](https://pubmed.ncbi.nlm.nih.gov/35325188/) `★84`
- **[Genrich](https://github.com/jsh58/Genrich)** — Peak caller with replicate handling and an ATAC mode — [code](https://github.com/jsh58/Genrich)

<sub>[+ 568 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=peak-calling)</sub>

## Peak annotation & differential binding

*Annotating peaks to genes/features and testing differential occupancy.*

<sub>[23 tools in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=peak-annotation)</sub>

## ChIP/ATAC data resources

*Portals and databases of processed binding and accessibility experiments.*

- **[ReMap](https://remap.univ-amu.fr/)** — Large-scale atlas of regulatory regions from public DNA-binding experiments — [bio.tools](https://bio.tools/inserm-remap) · [paper](https://pubmed.ncbi.nlm.nih.gov/25477382/) `1,069 cites`
- **[GTRD](http://gtrd.biouml.org/)** — Uniformly reprocessed ChIP-seq with meta-clusters of TF binding sites — [bio.tools](https://bio.tools/gtrd) · [paper](https://pubmed.ncbi.nlm.nih.gov/33231677/) `306 cites`
- **[ChIP-Atlas](https://chip-atlas.org)** — Reprocessed public ChIP-seq, ATAC-seq and Bisulfite-seq across six organisms — [code](https://github.com/inutano/chip-atlas) · [bio.tools](https://bio.tools/chip-atlas) · [paper](https://pubmed.ncbi.nlm.nih.gov/35325188/) `★84`

<sub>[+ 60 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=chip-resources)</sub>

## Gene regulatory networks

*Inferring and analysing TF-target networks and regulons.*

- **[SCENIC](http://scenic.aertslab.org)** — Single-cell regulatory network inference; regulons rather than raw correlations — [code](https://github.com/aertslab/SCENIC) · [bio.tools](https://bio.tools/scenic) · [paper](https://pubmed.ncbi.nlm.nih.gov/28991892/) `★491 | 4,807 cites`
- **[pySCENIC](https://github.com/aertslab/pySCENIC)** — Fast implementation of SCENIC — [code](https://github.com/aertslab/pySCENIC) · [paper](https://doi.org/10.1038/s41596-020-0336-2)

<sub>[+ 393 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=grn-inference)</sub>

## Regulatory variant effect

*Assessing the impact of sequence variants on binding and regulatory activity.*

<sub>[30 tools in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=regulatory-variants)</sub>

## Nucleosome & chromatin state

*Nucleosome positioning, chromatin accessibility and chromatin-state segmentation.*

- **[ReMap](https://remap.univ-amu.fr/)** — Large-scale atlas of regulatory regions from public DNA-binding experiments — [bio.tools](https://bio.tools/inserm-remap) · [paper](https://pubmed.ncbi.nlm.nih.gov/25477382/) `1,069 cites`
- **[UniBind](https://unibind.uio.no/)** — TFBS predictions restricted to ChIP-seq-supported, high-confidence sites — [code](https://bitbucket.org/CBGR/unibind_enrichment/) · [bio.tools](https://bio.tools/unibind) · [paper](https://doi.org/10.1101/2020.11.17.384578) `7 cites`

<sub>[+ 354 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=nucleosome-chromatin)</sub>

## Single-cell regulatory genomics

*Single-cell ATAC/multiome and single-cell regulatory network methods.*

- **[SCENIC](http://scenic.aertslab.org)** — Single-cell regulatory network inference; regulons rather than raw correlations — [code](https://github.com/aertslab/SCENIC) · [bio.tools](https://bio.tools/scenic) · [paper](https://pubmed.ncbi.nlm.nih.gov/28991892/) `★491 | 4,807 cites`
- **[pySCENIC](https://github.com/aertslab/pySCENIC)** — Fast implementation of SCENIC — [code](https://github.com/aertslab/pySCENIC) · [paper](https://doi.org/10.1038/s41596-020-0336-2)

<sub>[+ 97 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=single-cell)</sub>

## Comparative & evolutionary

*Cross-species conservation and evolution of regulatory sequence.*

- **[TFBSFootprinter](https://github.com/thirtysix/TFBS_footprinting)** — Multi-evidence TFBS scoring combining conservation, CAGE, eQTL and chromatin data — [code](https://github.com/thirtysix/TFBS_footprinting) · [paper](https://doi.org/10.3389/fbinf.2022.910346)

<sub>[+ 37 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=comparative)</sub>

## How this list is built

```
harvest.py        wide sweep of bio.tools (EDAM operation + free-text queries)
select_domain.py  tiered precision filter -> what is in scope
enrich.py         resolve source repos, GitHub activity, OpenAlex citations
build.py          merge with curated seeds, assign categories, apply overlay
render.py         write README.md and the searchable site
audit_coverage.py measure recall against a hand-written benchmark
```

**No step calls an LLM.** Selection, categorisation and enrichment are set membership on EDAM terms, compiled regex and API lookups, so `make refresh` is reproducible, runs in CI without any API key, and every rule is readable in [`pipeline/config.py`](pipeline/config.py). An *optional* stage ([`docs/llm-stage.md`](docs/llm-stage.md)) can propose better categories and descriptions, but it writes to a review file that is merged below the hand-written overlay — it never decides anything on its own.

Two design decisions are worth stating, because they are where most tool tables go wrong:

**Recall and precision are separated.** bio.tools' `operation=` parameter is a fuzzy text match, not an ontology lookup — an unquoted query for `cis-regulatory` returns 3,000 records matching "cis" *or* "regulatory". So the sweep is deliberately over-broad and precision is restored afterwards by filtering on the annotations a record actually carries.

**EDAM annotations are not trusted on their own.** They are frequently wrong: FIMO is filed under *Genotyping*, HOCOMOCO under *Data handling*, MACS under *Modelling and simulation*, and the operation *Peak detection* is used almost exclusively by mass-spectrometry tools. Operations are therefore tiered — specific terms admit a record on their own, ambiguous ones need a corroborating topic or text signal, and four terms are queried but never used to admit anything. A text-match escape hatch recovers in-domain tools with no usable annotation at all. Every accepted record stores the rule that admitted it (`_select_reason`), and every rejected one is written to [`data/raw/rejected.json`](data/raw/rejected.json) so the boundary can be argued with rather than taken on trust.

## Coverage and known gaps

- **1741 tools**: 1702 harvested from bio.tools, 39 added by hand because bio.tools does not index them.
- **836 (48%) have a resolvable source repository.** bio.tools rarely records one directly, so repository URLs are also recovered through Bioconductor, CRAN and PyPI metadata.
- **19 tools are featured** in the curated sections above; the rest are in the [full catalog](https://thirtysix.github.io/awesome-regulatory-genomics/).

Honest limitations:

- bio.tools skews toward tools with a publication and an ELIXIR-adjacent submitter. The sequence-to-function deep-learning literature is badly under-represented there; those entries come from `curation/seeds.yaml` and are necessarily incomplete.
- Citation counts are OpenAlex `cited_by_count` summed over *all* publications linked to a tool, so suites with many papers accumulate more than single-paper tools. Treat them as a rough popularity signal, not a quality measure.
- Categories are assigned by rule, then corrected by hand where wrong. Mis-categorisations are expected; please open an issue.
- A tool being listed is not an endorsement, and the absence of a repository link often means the tool is web-only, not that it is unmaintained.

Recall against a hand-written benchmark of standard resources is tracked in [`docs/coverage.md`](docs/coverage.md) and regenerated by `make audit`, so "did it find the obvious things?" is a number rather than an impression.

## Contributing

Additions, corrections and re-categorisations are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). Edit [`curation/seeds.yaml`](curation/seeds.yaml) or [`curation/overlay.yaml`](curation/overlay.yaml); never edit `README.md` or `data/catalog.*` directly, as both are regenerated.

## Provenance

This catalog began as a table in a doctoral dissertation on transcription-factor binding site prediction. That table and the scripts that produced it are preserved unchanged in [`dissertation/`](dissertation/) for citation; [`docs/provenance.md`](docs/provenance.md) documents how it was derived and what this catalog changes.

## Licence

Catalog data: [CC BY 4.0](LICENSE-DATA). Pipeline code: [MIT](LICENSE). Tool metadata originates from [bio.tools](https://bio.tools) (CC BY 4.0) and [OpenAlex](https://openalex.org) (CC0).
