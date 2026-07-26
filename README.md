# Awesome Regulatory Genomics

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re) [![Tools](https://img.shields.io/badge/tools-1817-blue)](https://thirtysix.github.io/awesome-regulatory-genomics/) [![License: CC BY 4.0](https://img.shields.io/badge/data-CC--BY--4.0-lightgrey)](LICENSE-DATA) [![Updated](https://img.shields.io/badge/updated-2026--07--26-brightgreen)](#)

A catalog of tools, databases and methods for **transcription-factor binding, sequence motifs, regulatory elements, chromatin and gene-regulatory networks**.

**[Browse and search all 1817 tools →](https://thirtysix.github.io/awesome-regulatory-genomics/)**. Filter by category, tool type, language, licence, activity and citations.

This list is *generated and then curated*. A reproducible pipeline harvests [bio.tools](https://bio.tools), resolves source repositories, and pulls citation counts and repository activity; a hand-written overlay adds tools bio.tools does not index and promotes the entries below. Everything is rebuildable with `make all`; see [How this list is built](#how-this-list-is-built).

## Contents

- [Motif discovery](#motif-discovery), 190 tools
- [Motif scanning & enrichment](#motif-scanning--enrichment), 208 tools
- [Motif comparison & visualisation](#motif-comparison--visualisation), 33 tools
- [Motif & TF databases](#motif--tf-databases), 105 tools
- [TFBS prediction](#tfbs-prediction), 609 tools
- [Promoter & enhancer prediction](#promoter--enhancer-prediction), 481 tools
- [Footprinting](#footprinting), 35 tools
- [Peak calling](#peak-calling), 499 tools
- [Peak annotation & differential binding](#peak-annotation--differential-binding), 82 tools
- [ChIP/ATAC data resources](#chipatac-data-resources), 104 tools
- [Gene regulatory networks](#gene-regulatory-networks), 433 tools
- [Regulatory variant effect](#regulatory-variant-effect), 102 tools
- [Nucleosome & chromatin state](#nucleosome--chromatin-state), 291 tools
- [Single-cell regulatory genomics](#single-cell-regulatory-genomics), 122 tools
- [Comparative & evolutionary](#comparative--evolutionary), 33 tools
- [How this list is built](#how-this-list-is-built)
- [Coverage and known gaps](#coverage-and-known-gaps)
- [Contributing](#contributing)

## Motif discovery

*De novo discovery of sequence motifs from sets of sequences or peaks.*

- **[JASPAR](http://jaspar.genereg.net/)**: The default open motif database; six taxonomic groups, versioned releases
  <sub>[code](https://github.com/asntech/pyjaspar) · [bio.tools](https://bio.tools/jaspar) · [paper](https://pubmed.ncbi.nlm.nih.gov/34850907/) · `38 stars | 1,576 cites`</sub>
- **[TFBSTools](http://bioconductor.org/packages/release/bioc/html/TFBSTools.html)**: R interface to motif matrices, scanning and JASPAR
  <sub>[code](https://github.com/ge11232002/TFBSTools) · [bio.tools](https://bio.tools/tfbstools) · [paper](https://pubmed.ncbi.nlm.nih.gov/26794315/) · `37 stars | 349 cites`</sub>
- **[RSAT suite](http://rsat.eu)**: Long-running suite covering matrix scanning, comparison and enrichment
  <sub>[bio.tools](https://bio.tools/rsat) · [paper](https://pubmed.ncbi.nlm.nih.gov/10641039/) · `184 cites`</sub>
- **[BPNet](https://github.com/kundajelab/bpnet)**: Base-resolution TF binding model that recovers motif syntax
  <sub>[code](https://github.com/kundajelab/bpnet) · [paper](https://doi.org/10.1038/s41588-021-00782-6)</sub>
- **[homer](http://homer.ucsd.edu/homer/motif/)**: Motif discovery plus peak annotation; the pragmatic first stop for ChIP-seq
  <sub>[bio.tools](https://bio.tools/homer)</sub>

<sub>[+ 185 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=motif-discovery)</sub>

## Motif scanning & enrichment

*Scanning sequences with known matrices; motif enrichment and over-representation.*

- **[TFBSTools](http://bioconductor.org/packages/release/bioc/html/TFBSTools.html)**: R interface to motif matrices, scanning and JASPAR
  <sub>[code](https://github.com/ge11232002/TFBSTools) · [bio.tools](https://bio.tools/tfbstools) · [paper](https://pubmed.ncbi.nlm.nih.gov/26794315/) · `37 stars | 349 cites`</sub>
- **[RSAT suite](http://rsat.eu)**: Long-running suite covering matrix scanning, comparison and enrichment
  <sub>[bio.tools](https://bio.tools/rsat) · [paper](https://pubmed.ncbi.nlm.nih.gov/10641039/) · `184 cites`</sub>
- **[FIMO](https://meme-suite.org/meme/tools/fimo)**: Standard scanner for known motifs with calibrated p-values
  <sub>[code](https://github.com/cinquin/MEME) · [paper](https://doi.org/10.1093/bioinformatics/btr064)</sub>
- **[homer](http://homer.ucsd.edu/homer/motif/)**: Motif discovery plus peak annotation; the pragmatic first stop for ChIP-seq
  <sub>[bio.tools](https://bio.tools/homer)</sub>
- **[motifmatchr](https://bioconductor.org/packages/motifmatchr/)**: Fast motif matching over large genomic range sets
  <sub>[code](https://github.com/GreenleafLab/motifmatchr) · [paper](https://doi.org/10.18129/B9.bioc.motifmatchr)</sub>

<sub>[+ 203 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=motif-scanning)</sub>

## Motif comparison & visualisation

*Comparing, clustering, aligning and drawing motifs and logos.*

- **[RSAT suite](http://rsat.eu)**: Long-running suite covering matrix scanning, comparison and enrichment
  <sub>[bio.tools](https://bio.tools/rsat) · [paper](https://pubmed.ncbi.nlm.nih.gov/10641039/) · `184 cites`</sub>

<sub>[+ 32 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=motif-comparison)</sub>

## Motif & TF databases

*Curated collections of binding profiles, TF families and TF-target relationships.*

- **[JASPAR](http://jaspar.genereg.net/)**: The default open motif database; six taxonomic groups, versioned releases
  <sub>[code](https://github.com/asntech/pyjaspar) · [bio.tools](https://bio.tools/jaspar) · [paper](https://pubmed.ncbi.nlm.nih.gov/34850907/) · `38 stars | 1,576 cites`</sub>
- **[GTRD](http://gtrd.biouml.org/)**: Uniformly reprocessed ChIP-seq with meta-clusters of TF binding sites
  <sub>[bio.tools](https://bio.tools/gtrd) · [paper](https://pubmed.ncbi.nlm.nih.gov/33231677/) · `306 cites`</sub>
- **[ReMap](https://remap.univ-amu.fr/)**: Large-scale atlas of regulatory regions from public DNA-binding experiments
  <sub>[bio.tools](https://bio.tools/inserm-remap) · [paper](https://pubmed.ncbi.nlm.nih.gov/25477382/) · `138 cites`</sub>
- **[UniBind](https://unibind.uio.no/)**: TFBS predictions restricted to ChIP-seq-supported, high-confidence sites
  <sub>[code](https://bitbucket.org/CBGR/unibind_enrichment/) · [bio.tools](https://bio.tools/unibind) · [preprint](https://doi.org/10.1101/2020.11.17.384578) · `7 cites`</sub>
- **[CIS-BP](http://cisbp.ccbr.utoronto.ca/)**: Motif inference across species by DNA-binding-domain similarity
  <sub>[paper](https://doi.org/10.1016/j.cell.2014.08.009)</sub>
- **[HOCOMOCO](https://hocomoco.autosome.org)**: Human and mouse motifs derived from uniform ChIP-seq reprocessing
  <sub>[bio.tools](https://bio.tools/hocomoco) · [paper](https://pubmed.ncbi.nlm.nih.gov/29140464/)</sub>

<sub>[+ 99 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=motif-databases)</sub>

## TFBS prediction

*Predicting transcription-factor binding sites, including sequence-based ML models.*

- **[JASPAR](http://jaspar.genereg.net/)**: The default open motif database; six taxonomic groups, versioned releases
  <sub>[code](https://github.com/asntech/pyjaspar) · [bio.tools](https://bio.tools/jaspar) · [paper](https://pubmed.ncbi.nlm.nih.gov/34850907/) · `38 stars | 1,576 cites`</sub>
- **[TFBSTools](http://bioconductor.org/packages/release/bioc/html/TFBSTools.html)**: R interface to motif matrices, scanning and JASPAR
  <sub>[code](https://github.com/ge11232002/TFBSTools) · [bio.tools](https://bio.tools/tfbstools) · [paper](https://pubmed.ncbi.nlm.nih.gov/26794315/) · `37 stars | 349 cites`</sub>
- **[RSAT suite](http://rsat.eu)**: Long-running suite covering matrix scanning, comparison and enrichment
  <sub>[bio.tools](https://bio.tools/rsat) · [paper](https://pubmed.ncbi.nlm.nih.gov/10641039/) · `184 cites`</sub>
- **[ReMap](https://remap.univ-amu.fr/)**: Large-scale atlas of regulatory regions from public DNA-binding experiments
  <sub>[bio.tools](https://bio.tools/inserm-remap) · [paper](https://pubmed.ncbi.nlm.nih.gov/25477382/) · `138 cites`</sub>
- **[UniBind](https://unibind.uio.no/)**: TFBS predictions restricted to ChIP-seq-supported, high-confidence sites
  <sub>[code](https://bitbucket.org/CBGR/unibind_enrichment/) · [bio.tools](https://bio.tools/unibind) · [preprint](https://doi.org/10.1101/2020.11.17.384578) · `7 cites`</sub>
- **[BPNet](https://github.com/kundajelab/bpnet)**: Base-resolution TF binding model that recovers motif syntax
  <sub>[code](https://github.com/kundajelab/bpnet) · [paper](https://doi.org/10.1038/s41588-021-00782-6)</sub>
- **[Enformer](https://github.com/google-deepmind/deepmind-research/tree/master/enformer)**: Long-range sequence-to-expression model; a common baseline for regulatory prediction
  <sub>[code](https://github.com/google-deepmind/deepmind-research) · [paper](https://doi.org/10.1038/s41592-021-01252-x)</sub>
- **[SCENIC](http://scenic.aertslab.org)**: Single-cell regulatory network inference; regulons rather than raw correlations
  <sub>[code](https://github.com/aertslab/SCENIC) · [bio.tools](https://bio.tools/scenic) · [paper](https://pubmed.ncbi.nlm.nih.gov/28991892/) · `491 stars`</sub>
- **[TFBSFootprinter](https://github.com/thirtysix/TFBS_footprinting3)**: Multi-evidence TFBS scoring combining conservation, CAGE, eQTL and chromatin data
  <sub>[code](https://github.com/thirtysix/TFBS_footprinting3) · [paper](https://pubmed.ncbi.nlm.nih.gov/40646689/)</sub>
- **[TOBIAS](https://github.com/loosolab/TOBIAS)**: Differential ATAC-seq footprinting between conditions
  <sub>[code](https://github.com/loosolab/TOBIAS) · [bio.tools](https://bio.tools/TOBIAS) · [paper](https://doi.org/10.1038/s41467-020-18035-1) · `251 stars`</sub>

<sub>[+ 599 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=tfbs-prediction)</sub>

## Promoter & enhancer prediction

*Prediction and annotation of promoters, enhancers and other cis-regulatory elements.*

- **[TFBSTools](http://bioconductor.org/packages/release/bioc/html/TFBSTools.html)**: R interface to motif matrices, scanning and JASPAR
  <sub>[code](https://github.com/ge11232002/TFBSTools) · [bio.tools](https://bio.tools/tfbstools) · [paper](https://pubmed.ncbi.nlm.nih.gov/26794315/) · `37 stars | 349 cites`</sub>
- **[RSAT suite](http://rsat.eu)**: Long-running suite covering matrix scanning, comparison and enrichment
  <sub>[bio.tools](https://bio.tools/rsat) · [paper](https://pubmed.ncbi.nlm.nih.gov/10641039/) · `184 cites`</sub>
- **[Enformer](https://github.com/google-deepmind/deepmind-research/tree/master/enformer)**: Long-range sequence-to-expression model; a common baseline for regulatory prediction
  <sub>[code](https://github.com/google-deepmind/deepmind-research) · [paper](https://doi.org/10.1038/s41592-021-01252-x)</sub>
- **[homer](http://homer.ucsd.edu/homer/motif/)**: Motif discovery plus peak annotation; the pragmatic first stop for ChIP-seq
  <sub>[bio.tools](https://bio.tools/homer)</sub>

<sub>[+ 477 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=regulatory-elements)</sub>

## Footprinting

*DNase/ATAC digital footprinting and phylogenetic footprinting.*

- **[RSAT suite](http://rsat.eu)**: Long-running suite covering matrix scanning, comparison and enrichment
  <sub>[bio.tools](https://bio.tools/rsat) · [paper](https://pubmed.ncbi.nlm.nih.gov/10641039/) · `184 cites`</sub>
- **[TFBSFootprinter](https://github.com/thirtysix/TFBS_footprinting3)**: Multi-evidence TFBS scoring combining conservation, CAGE, eQTL and chromatin data
  <sub>[code](https://github.com/thirtysix/TFBS_footprinting3) · [paper](https://pubmed.ncbi.nlm.nih.gov/40646689/)</sub>
- **[TOBIAS](https://github.com/loosolab/TOBIAS)**: Differential ATAC-seq footprinting between conditions
  <sub>[code](https://github.com/loosolab/TOBIAS) · [bio.tools](https://bio.tools/TOBIAS) · [paper](https://doi.org/10.1038/s41467-020-18035-1) · `251 stars`</sub>

<sub>[+ 32 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=footprinting)</sub>

## Peak calling

*Calling enriched regions from ChIP-seq, ATAC-seq, CUT&RUN and related assays.*

- **[ReMap](https://remap.univ-amu.fr/)**: Large-scale atlas of regulatory regions from public DNA-binding experiments
  <sub>[bio.tools](https://bio.tools/inserm-remap) · [paper](https://pubmed.ncbi.nlm.nih.gov/25477382/) · `138 cites`</sub>
- **[ChIP-Atlas](https://chip-atlas.org)**: Reprocessed public ChIP-seq, ATAC-seq and Bisulfite-seq across six organisms
  <sub>[code](https://github.com/inutano/chip-atlas) · [bio.tools](https://bio.tools/chip-atlas) · [paper](https://pubmed.ncbi.nlm.nih.gov/35325188/) · `84 stars`</sub>
- **[Genrich](https://github.com/jsh58/Genrich)**: Peak caller with replicate handling and an ATAC mode
  <sub>[code](https://github.com/jsh58/Genrich)</sub>
- **[TOBIAS](https://github.com/loosolab/TOBIAS)**: Differential ATAC-seq footprinting between conditions
  <sub>[code](https://github.com/loosolab/TOBIAS) · [bio.tools](https://bio.tools/TOBIAS) · [paper](https://doi.org/10.1038/s41467-020-18035-1) · `251 stars`</sub>

<sub>[+ 495 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=peak-calling)</sub>

## Peak annotation & differential binding

*Annotating peaks to genes/features and testing differential occupancy.*

<sub>[82 tools in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=peak-annotation)</sub>

## ChIP/ATAC data resources

*Portals and databases of processed binding and accessibility experiments.*

- **[GTRD](http://gtrd.biouml.org/)**: Uniformly reprocessed ChIP-seq with meta-clusters of TF binding sites
  <sub>[bio.tools](https://bio.tools/gtrd) · [paper](https://pubmed.ncbi.nlm.nih.gov/33231677/) · `306 cites`</sub>
- **[ReMap](https://remap.univ-amu.fr/)**: Large-scale atlas of regulatory regions from public DNA-binding experiments
  <sub>[bio.tools](https://bio.tools/inserm-remap) · [paper](https://pubmed.ncbi.nlm.nih.gov/25477382/) · `138 cites`</sub>
- **[ChIP-Atlas](https://chip-atlas.org)**: Reprocessed public ChIP-seq, ATAC-seq and Bisulfite-seq across six organisms
  <sub>[code](https://github.com/inutano/chip-atlas) · [bio.tools](https://bio.tools/chip-atlas) · [paper](https://pubmed.ncbi.nlm.nih.gov/35325188/) · `84 stars`</sub>

<sub>[+ 101 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=chip-resources)</sub>

## Gene regulatory networks

*Inferring and analysing TF-target networks and regulons.*

- **[pySCENIC](https://github.com/aertslab/pySCENIC)**: Fast implementation of SCENIC
  <sub>[code](https://github.com/aertslab/pySCENIC) · [paper](https://doi.org/10.1038/s41596-020-0336-2)</sub>
- **[SCENIC](http://scenic.aertslab.org)**: Single-cell regulatory network inference; regulons rather than raw correlations
  <sub>[code](https://github.com/aertslab/SCENIC) · [bio.tools](https://bio.tools/scenic) · [paper](https://pubmed.ncbi.nlm.nih.gov/28991892/) · `491 stars`</sub>

<sub>[+ 431 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=grn-inference)</sub>

## Regulatory variant effect

*Assessing the impact of sequence variants on binding and regulatory activity.*

<sub>[102 tools in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=regulatory-variants)</sub>

## Nucleosome & chromatin state

*Nucleosome positioning, chromatin accessibility and chromatin-state segmentation.*

- **[ReMap](https://remap.univ-amu.fr/)**: Large-scale atlas of regulatory regions from public DNA-binding experiments
  <sub>[bio.tools](https://bio.tools/inserm-remap) · [paper](https://pubmed.ncbi.nlm.nih.gov/25477382/) · `138 cites`</sub>

<sub>[+ 290 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=nucleosome-chromatin)</sub>

## Single-cell regulatory genomics

*Single-cell ATAC/multiome and single-cell regulatory network methods.*

- **[pySCENIC](https://github.com/aertslab/pySCENIC)**: Fast implementation of SCENIC
  <sub>[code](https://github.com/aertslab/pySCENIC) · [paper](https://doi.org/10.1038/s41596-020-0336-2)</sub>
- **[SCENIC](http://scenic.aertslab.org)**: Single-cell regulatory network inference; regulons rather than raw correlations
  <sub>[code](https://github.com/aertslab/SCENIC) · [bio.tools](https://bio.tools/scenic) · [paper](https://pubmed.ncbi.nlm.nih.gov/28991892/) · `491 stars`</sub>

<sub>[+ 120 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=single-cell)</sub>

## Comparative & evolutionary

*Cross-species conservation and evolution of regulatory sequence.*

- **[TFBSFootprinter](https://github.com/thirtysix/TFBS_footprinting3)**: Multi-evidence TFBS scoring combining conservation, CAGE, eQTL and chromatin data
  <sub>[code](https://github.com/thirtysix/TFBS_footprinting3) · [paper](https://pubmed.ncbi.nlm.nih.gov/40646689/)</sub>

<sub>[+ 32 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=comparative)</sub>

## How this list is built

```
harvest.py        wide sweep of bio.tools (EDAM operation + free-text queries)
select_domain.py  tiered precision filter -> what is in scope
enrich.py         resolve source repos, GitHub activity, OpenAlex citations
build.py          merge with curated seeds, assign categories, apply overlay
render.py         write README.md and the searchable site
audit_coverage.py measure recall against a hand-written benchmark
```

**Harvesting and selection never call an LLM.** They are set membership on EDAM terms, compiled regex and API lookups, so the scope of the catalog is reproducible and every rule is readable in [`pipeline/config.py`](pipeline/config.py). Categories and descriptions are then refined by an *optional* model pass ([`docs/llm-stage.md`](docs/llm-stage.md)) that writes to a review file merged below the hand-written overlay; `make build-strict` ignores it entirely and rebuilds on rules alone. Removing a record needs two different models to agree independently, and never overrides a hand-vetted entry. Additions get the mirror check from a third model ([`docs/addition-review.md`](docs/addition-review.md)), which is how a name collision between the MEME Suite's MAST and the unrelated single-cell package of the same name was caught.

Two design decisions are worth stating, because they are where most tool tables go wrong:

**Recall and precision are separated.** bio.tools' `operation=` parameter is a fuzzy text match, not an ontology lookup. An unquoted query for `cis-regulatory` returns 3,000 records matching "cis" *or* "regulatory". So the sweep is deliberately over-broad and precision is restored afterwards by filtering on the annotations a record actually carries.

**EDAM annotations are not trusted on their own.** They are frequently wrong: FIMO is filed under *Genotyping*, HOCOMOCO under *Data handling*, MACS under *Modelling and simulation*, and the operation *Peak detection* is used almost exclusively by mass-spectrometry tools. Operations are therefore tiered: specific terms admit a record on their own, ambiguous ones need a corroborating topic or text signal, and four terms are queried but never used to admit anything. A text-match escape hatch recovers in-domain tools with no usable annotation at all. Every accepted record stores the rule that admitted it (`_select_reason`), and every rejected one is written to [`data/raw/rejected.json`](data/raw/rejected.json) so the boundary can be argued with rather than taken on trust.

## Coverage and known gaps

- **1817 tools**: 1781 harvested from bio.tools, 36 added by hand because bio.tools does not index them.
- **906 (50%) have a resolvable source repository.** bio.tools rarely records one directly, so repository URLs are also recovered through Bioconductor, CRAN and PyPI metadata.
- **19 tools are featured** in the curated sections above; the rest are in the [full catalog](https://thirtysix.github.io/awesome-regulatory-genomics/).

Honest limitations:

- bio.tools skews toward tools with a publication and an ELIXIR-adjacent submitter. The sequence-to-function deep-learning literature is badly under-represented there; those entries come from `curation/seeds.yaml` and are necessarily incomplete.
- Citation counts are the OpenAlex `cited_by_count` of a tool's **primary** publication only. Summing every linked publication, which is what the original dissertation script did, is badly wrong here: bio.tools attaches a suite's paper to each of its members, so the EMBOSS paper is linked to dozens of EMBOSS commands and the Bioconductor paper to 23 packages in this sweep, handing each member the whole suite's count. Where a primary publication is itself shared by three or more tools, no count is shown at all, because the member's own impact is genuinely unknown. Treat what remains as a rough popularity signal, not a quality measure.
- Categories are assigned by rule, then corrected by hand where wrong. The rules catch the systematic errors (bio.tools files orthology tools under *Phylogenetic footprinting* and mass-spectrometry tools under *Peak detection*), but a tail of individual mis-categorisations remains. Please open an issue, or see [`docs/llm-stage.md`](docs/llm-stage.md) for the optional classifier that targets exactly this tail.
- A tool being listed is not an endorsement, and the absence of a repository link often means the tool is web-only, not that it is unmaintained.

Recall against a hand-written benchmark of standard resources is tracked in [`docs/coverage.md`](docs/coverage.md) and regenerated by `make audit`, so "did it find the obvious things?" is a number rather than an impression.

## Contributing

Additions, corrections and re-categorisations are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md). Edit [`curation/seeds.yaml`](curation/seeds.yaml) or [`curation/overlay.yaml`](curation/overlay.yaml); never edit `README.md` or `data/catalog.*` directly, as both are regenerated.

## Provenance

This catalog began as a table in a doctoral dissertation on transcription-factor binding site prediction. That table and the scripts that produced it are preserved unchanged in [`dissertation/`](dissertation/) for citation; [`docs/provenance.md`](docs/provenance.md) documents how it was derived and what this catalog changes.

## Licence

Catalog data: [CC BY 4.0](LICENSE-DATA). Pipeline code: [MIT](LICENSE). Tool metadata originates from [bio.tools](https://bio.tools) (CC BY 4.0) and [OpenAlex](https://openalex.org) (CC0).
