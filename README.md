# Awesome Regulatory Genomics

[![Awesome](https://awesome.re/badge.svg)](https://awesome.re) [![Tools](https://img.shields.io/badge/tools-1951-blue)](https://thirtysix.github.io/awesome-regulatory-genomics/) [![License: CC BY 4.0](https://img.shields.io/badge/data-CC--BY--4.0-lightgrey)](LICENSE-DATA) [![Updated](https://img.shields.io/badge/updated-2026--07--28-brightgreen)](#)

A catalog of tools, databases and methods for **transcription-factor binding, sequence motifs, regulatory elements, chromatin and gene-regulatory networks**.

**[Browse and search all 1951 tools →](https://thirtysix.github.io/awesome-regulatory-genomics/)**. Filter by category, tool type, language, repository activity, and per column by name, description, links, package availability, stars, citations and year. The panel above the table charts publication year, repository activity, citations and stars **for whatever is currently filtered**, so "when were the peak callers written, and are they still maintained" is one click rather than a download.

This list is *generated and then curated*. A reproducible pipeline harvests [bio.tools](https://bio.tools), resolves source repositories, and pulls citation counts and repository activity; a hand-written overlay adds tools bio.tools does not index and promotes the entries below. Everything is rebuildable with `make all`; see [How this list is built](#how-this-list-is-built).

## Contents

- [Motif discovery](#motif-discovery), 186 tools
- [Motif scanning & enrichment](#motif-scanning--enrichment), 205 tools
- [Motif comparison & visualisation](#motif-comparison--visualisation), 30 tools
- [Motif & TF databases](#motif--tf-databases), 116 tools
- [TFBS prediction](#tfbs-prediction), 641 tools
- [Promoter & enhancer prediction](#promoter--enhancer-prediction), 486 tools
- [Reporter assays](#reporter-assays), 4 tools
- [Footprinting](#footprinting), 40 tools
- [Peak calling](#peak-calling), 518 tools
- [Peak annotation & differential binding](#peak-annotation--differential-binding), 87 tools
- [ChIP/ATAC data resources](#chipatac-data-resources), 113 tools
- [Gene regulatory networks](#gene-regulatory-networks), 452 tools
- [Regulatory variant effect](#regulatory-variant-effect), 108 tools
- [Molecular QTL](#molecular-qtl), 19 tools
- [Nucleosome & chromatin state](#nucleosome--chromatin-state), 348 tools
- [Histone modifications](#histone-modifications), 33 tools
- [3D genome & chromatin interactions](#3d-genome--chromatin-interactions), 71 tools
- [DNA methylation](#dna-methylation), 96 tools
- [Single-cell regulatory genomics](#single-cell-regulatory-genomics), 137 tools
- [Comparative & evolutionary](#comparative--evolutionary), 35 tools
- [How this list is built](#how-this-list-is-built)
- [Coverage and known gaps](#coverage-and-known-gaps)
- [Contributing](#contributing)

## Motif discovery

*De novo discovery of sequence motifs from sets of sequences or peaks.*

- **[JASPAR](http://jaspar.genereg.net/)**: The default open motif database; six taxonomic groups, versioned releases
  <sub>[code](https://github.com/asntech/pyjaspar) · [bio.tools](https://bio.tools/jaspar) · [paper](https://pubmed.ncbi.nlm.nih.gov/34850907/) · `38 stars | 1,576 cites`</sub>
- **[BPNet](https://github.com/kundajelab/bpnet)**: Base-resolution TF binding model that recovers motif syntax
  <sub>[code](https://github.com/kundajelab/bpnet) · [paper](https://doi.org/10.1038/s41588-021-00782-6) · `704 cites`</sub>
- **[TFBSTools](http://bioconductor.org/packages/release/bioc/html/TFBSTools.html)**: R interface to motif matrices, scanning and JASPAR
  <sub>[code](https://github.com/ge11232002/TFBSTools) · [bio.tools](https://bio.tools/tfbstools) · [paper](https://pubmed.ncbi.nlm.nih.gov/26794315/) · `37 stars | 349 cites`</sub>
- **[RSAT suite](http://rsat.eu)**: Long-running suite covering matrix scanning, comparison and enrichment
  <sub>[bio.tools](https://bio.tools/rsat) · [paper](https://pubmed.ncbi.nlm.nih.gov/10641039/) · `184 cites`</sub>
- **[homer](http://homer.ucsd.edu/homer/motif/)**: Motif discovery plus peak annotation; the pragmatic first stop for ChIP-seq
  <sub>[bio.tools](https://bio.tools/homer)</sub>

<sub>[+ 181 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=motif-discovery)</sub>

## Motif scanning & enrichment

*Scanning sequences with known matrices; motif enrichment and over-representation.*

- **[FIMO](https://meme-suite.org/meme/tools/fimo)**: Standard scanner for known motifs with calibrated p-values
  <sub>[code](https://github.com/cinquin/MEME) · [paper](https://doi.org/10.1093/bioinformatics/btr064) · `4,992 cites`</sub>
- **[TFBSTools](http://bioconductor.org/packages/release/bioc/html/TFBSTools.html)**: R interface to motif matrices, scanning and JASPAR
  <sub>[code](https://github.com/ge11232002/TFBSTools) · [bio.tools](https://bio.tools/tfbstools) · [paper](https://pubmed.ncbi.nlm.nih.gov/26794315/) · `37 stars | 349 cites`</sub>
- **[RSAT suite](http://rsat.eu)**: Long-running suite covering matrix scanning, comparison and enrichment
  <sub>[bio.tools](https://bio.tools/rsat) · [paper](https://pubmed.ncbi.nlm.nih.gov/10641039/) · `184 cites`</sub>
- **[homer](http://homer.ucsd.edu/homer/motif/)**: Motif discovery plus peak annotation; the pragmatic first stop for ChIP-seq
  <sub>[bio.tools](https://bio.tools/homer)</sub>
- **[motifmatchr](https://bioconductor.org/packages/motifmatchr/)**: Fast motif matching over large genomic range sets
  <sub>[code](https://github.com/GreenleafLab/motifmatchr) · [paper](https://doi.org/10.18129/B9.bioc.motifmatchr)</sub>

<sub>[+ 200 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=motif-scanning)</sub>

## Motif comparison & visualisation

*Comparing, clustering, aligning and drawing motifs and logos.*

- **[RSAT suite](http://rsat.eu)**: Long-running suite covering matrix scanning, comparison and enrichment
  <sub>[bio.tools](https://bio.tools/rsat) · [paper](https://pubmed.ncbi.nlm.nih.gov/10641039/) · `184 cites`</sub>

<sub>[+ 29 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=motif-comparison)</sub>

## Motif & TF databases

*Curated collections of binding profiles, TF families and TF-target relationships.*

- **[CIS-BP](http://cisbp.ccbr.utoronto.ca/)**: Motif inference across species by DNA-binding-domain similarity
  <sub>[paper](https://doi.org/10.1016/j.cell.2014.08.009) · `2,048 cites`</sub>
- **[JASPAR](http://jaspar.genereg.net/)**: The default open motif database; six taxonomic groups, versioned releases
  <sub>[code](https://github.com/asntech/pyjaspar) · [bio.tools](https://bio.tools/jaspar) · [paper](https://pubmed.ncbi.nlm.nih.gov/34850907/) · `38 stars | 1,576 cites`</sub>
- **[GTRD](http://gtrd.biouml.org/)**: Uniformly reprocessed ChIP-seq with meta-clusters of TF binding sites
  <sub>[bio.tools](https://bio.tools/gtrd) · [paper](https://pubmed.ncbi.nlm.nih.gov/33231677/) · `306 cites`</sub>
- **[ReMap](https://remap.univ-amu.fr/)**: Large-scale atlas of regulatory regions from public DNA-binding experiments
  <sub>[bio.tools](https://bio.tools/inserm-remap) · [paper](https://pubmed.ncbi.nlm.nih.gov/25477382/) · `138 cites`</sub>
- **[UniBind](https://unibind.uio.no/)**: TFBS predictions restricted to ChIP-seq-supported, high-confidence sites
  <sub>[code](https://bitbucket.org/CBGR/unibind_enrichment/) · [bio.tools](https://bio.tools/unibind) · [preprint](https://doi.org/10.1101/2020.11.17.384578) · `7 cites`</sub>
- **[HOCOMOCO](https://hocomoco.autosome.org)**: Human and mouse motifs derived from uniform ChIP-seq reprocessing
  <sub>[bio.tools](https://bio.tools/hocomoco) · [paper](https://pubmed.ncbi.nlm.nih.gov/29140464/)</sub>

<sub>[+ 110 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=motif-databases)</sub>

## TFBS prediction

*Predicting transcription-factor binding sites, including sequence-based ML models.*

- **[JASPAR](http://jaspar.genereg.net/)**: The default open motif database; six taxonomic groups, versioned releases
  <sub>[code](https://github.com/asntech/pyjaspar) · [bio.tools](https://bio.tools/jaspar) · [paper](https://pubmed.ncbi.nlm.nih.gov/34850907/) · `38 stars | 1,576 cites`</sub>
- **[Enformer](https://github.com/google-deepmind/deepmind-research/tree/master/enformer)**: Long-range sequence-to-expression model; a common baseline for regulatory prediction
  <sub>[code](https://github.com/google-deepmind/deepmind-research) · [paper](https://doi.org/10.1038/s41592-021-01252-x) · `1,338 cites`</sub>
- **[BPNet](https://github.com/kundajelab/bpnet)**: Base-resolution TF binding model that recovers motif syntax
  <sub>[code](https://github.com/kundajelab/bpnet) · [paper](https://doi.org/10.1038/s41588-021-00782-6) · `704 cites`</sub>
- **[TFBSTools](http://bioconductor.org/packages/release/bioc/html/TFBSTools.html)**: R interface to motif matrices, scanning and JASPAR
  <sub>[code](https://github.com/ge11232002/TFBSTools) · [bio.tools](https://bio.tools/tfbstools) · [paper](https://pubmed.ncbi.nlm.nih.gov/26794315/) · `37 stars | 349 cites`</sub>
- **[RSAT suite](http://rsat.eu)**: Long-running suite covering matrix scanning, comparison and enrichment
  <sub>[bio.tools](https://bio.tools/rsat) · [paper](https://pubmed.ncbi.nlm.nih.gov/10641039/) · `184 cites`</sub>
- **[ReMap](https://remap.univ-amu.fr/)**: Large-scale atlas of regulatory regions from public DNA-binding experiments
  <sub>[bio.tools](https://bio.tools/inserm-remap) · [paper](https://pubmed.ncbi.nlm.nih.gov/25477382/) · `138 cites`</sub>
- **[UniBind](https://unibind.uio.no/)**: TFBS predictions restricted to ChIP-seq-supported, high-confidence sites
  <sub>[code](https://bitbucket.org/CBGR/unibind_enrichment/) · [bio.tools](https://bio.tools/unibind) · [preprint](https://doi.org/10.1101/2020.11.17.384578) · `7 cites`</sub>
- **[SCENIC](http://scenic.aertslab.org)**: Single-cell regulatory network inference; regulons rather than raw correlations
  <sub>[code](https://github.com/aertslab/SCENIC) · [bio.tools](https://bio.tools/scenic) · [paper](https://pubmed.ncbi.nlm.nih.gov/28991892/) · `491 stars`</sub>
- **[TFBSFootprinter](https://github.com/thirtysix/TFBS_footprinting3)**: Multi-evidence TFBS scoring combining conservation, CAGE, eQTL and chromatin data
  <sub>[code](https://github.com/thirtysix/TFBS_footprinting3) · [paper](https://pubmed.ncbi.nlm.nih.gov/40646689/)</sub>
- **[TOBIAS](https://github.com/loosolab/TOBIAS)**: Differential ATAC-seq footprinting between conditions
  <sub>[code](https://github.com/loosolab/TOBIAS) · [bio.tools](https://bio.tools/TOBIAS) · [paper](https://doi.org/10.1038/s41467-020-18035-1) · `251 stars`</sub>

<sub>[+ 631 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=tfbs-prediction)</sub>

## Promoter & enhancer prediction

*Prediction and annotation of promoters, enhancers and other cis-regulatory elements.*

- **[Enformer](https://github.com/google-deepmind/deepmind-research/tree/master/enformer)**: Long-range sequence-to-expression model; a common baseline for regulatory prediction
  <sub>[code](https://github.com/google-deepmind/deepmind-research) · [paper](https://doi.org/10.1038/s41592-021-01252-x) · `1,338 cites`</sub>
- **[TFBSTools](http://bioconductor.org/packages/release/bioc/html/TFBSTools.html)**: R interface to motif matrices, scanning and JASPAR
  <sub>[code](https://github.com/ge11232002/TFBSTools) · [bio.tools](https://bio.tools/tfbstools) · [paper](https://pubmed.ncbi.nlm.nih.gov/26794315/) · `37 stars | 349 cites`</sub>
- **[RSAT suite](http://rsat.eu)**: Long-running suite covering matrix scanning, comparison and enrichment
  <sub>[bio.tools](https://bio.tools/rsat) · [paper](https://pubmed.ncbi.nlm.nih.gov/10641039/) · `184 cites`</sub>
- **[homer](http://homer.ucsd.edu/homer/motif/)**: Motif discovery plus peak annotation; the pragmatic first stop for ChIP-seq
  <sub>[bio.tools](https://bio.tools/homer)</sub>

<sub>[+ 482 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=regulatory-elements)</sub>

## Reporter assays

*MPRA, STARR-seq and other massively parallel tests of regulatory activity.*

<sub>[4 tools in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=reporter-assays)</sub>

## Footprinting

*DNase/ATAC digital footprinting and phylogenetic footprinting.*

- **[RSAT suite](http://rsat.eu)**: Long-running suite covering matrix scanning, comparison and enrichment
  <sub>[bio.tools](https://bio.tools/rsat) · [paper](https://pubmed.ncbi.nlm.nih.gov/10641039/) · `184 cites`</sub>
- **[TFBSFootprinter](https://github.com/thirtysix/TFBS_footprinting3)**: Multi-evidence TFBS scoring combining conservation, CAGE, eQTL and chromatin data
  <sub>[code](https://github.com/thirtysix/TFBS_footprinting3) · [paper](https://pubmed.ncbi.nlm.nih.gov/40646689/)</sub>
- **[TOBIAS](https://github.com/loosolab/TOBIAS)**: Differential ATAC-seq footprinting between conditions
  <sub>[code](https://github.com/loosolab/TOBIAS) · [bio.tools](https://bio.tools/TOBIAS) · [paper](https://doi.org/10.1038/s41467-020-18035-1) · `251 stars`</sub>

<sub>[+ 37 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=footprinting)</sub>

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

<sub>[+ 514 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=peak-calling)</sub>

## Peak annotation & differential binding

*Annotating peaks to genes/features and testing differential occupancy.*

<sub>[87 tools in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=peak-annotation)</sub>

## ChIP/ATAC data resources

*Portals and databases of processed binding and accessibility experiments.*

- **[GTRD](http://gtrd.biouml.org/)**: Uniformly reprocessed ChIP-seq with meta-clusters of TF binding sites
  <sub>[bio.tools](https://bio.tools/gtrd) · [paper](https://pubmed.ncbi.nlm.nih.gov/33231677/) · `306 cites`</sub>
- **[ReMap](https://remap.univ-amu.fr/)**: Large-scale atlas of regulatory regions from public DNA-binding experiments
  <sub>[bio.tools](https://bio.tools/inserm-remap) · [paper](https://pubmed.ncbi.nlm.nih.gov/25477382/) · `138 cites`</sub>
- **[ChIP-Atlas](https://chip-atlas.org)**: Reprocessed public ChIP-seq, ATAC-seq and Bisulfite-seq across six organisms
  <sub>[code](https://github.com/inutano/chip-atlas) · [bio.tools](https://bio.tools/chip-atlas) · [paper](https://pubmed.ncbi.nlm.nih.gov/35325188/) · `84 stars`</sub>

<sub>[+ 110 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=chip-resources)</sub>

## Gene regulatory networks

*Inferring and analysing TF-target networks and regulons.*

- **[pySCENIC](https://github.com/aertslab/pySCENIC)**: Fast implementation of SCENIC
  <sub>[code](https://github.com/aertslab/pySCENIC) · [paper](https://doi.org/10.1038/s41596-020-0336-2) · `1,574 cites`</sub>
- **[SCENIC](http://scenic.aertslab.org)**: Single-cell regulatory network inference; regulons rather than raw correlations
  <sub>[code](https://github.com/aertslab/SCENIC) · [bio.tools](https://bio.tools/scenic) · [paper](https://pubmed.ncbi.nlm.nih.gov/28991892/) · `491 stars`</sub>

<sub>[+ 450 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=grn-inference)</sub>

## Regulatory variant effect

*Assessing the impact of sequence variants on binding and regulatory activity.*

<sub>[108 tools in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=regulatory-variants)</sub>

## Molecular QTL

*eQTL, caQTL and related mapping of variants to regulatory phenotypes.*

<sub>[19 tools in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=molecular-qtl)</sub>

## Nucleosome & chromatin state

*Nucleosome positioning, chromatin accessibility and chromatin-state segmentation.*

- **[ReMap](https://remap.univ-amu.fr/)**: Large-scale atlas of regulatory regions from public DNA-binding experiments
  <sub>[bio.tools](https://bio.tools/inserm-remap) · [paper](https://pubmed.ncbi.nlm.nih.gov/25477382/) · `138 cites`</sub>

<sub>[+ 347 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=nucleosome-chromatin)</sub>

## Histone modifications

*Histone marks, super-enhancers and chromatin-state segmentation from histone data.*

<sub>[33 tools in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=histone-marks)</sub>

## 3D genome & chromatin interactions

*Hi-C, HiChIP and ChIA-PET; loops, TADs, compartments and enhancer-promoter contacts.*

<sub>[71 tools in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=chromatin-3d)</sub>

## DNA methylation

*Methylation calling, differential methylation and methylome resources.*

<sub>[96 tools in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=dna-methylation)</sub>

## Single-cell regulatory genomics

*Single-cell ATAC/multiome and single-cell regulatory network methods.*

- **[pySCENIC](https://github.com/aertslab/pySCENIC)**: Fast implementation of SCENIC
  <sub>[code](https://github.com/aertslab/pySCENIC) · [paper](https://doi.org/10.1038/s41596-020-0336-2) · `1,574 cites`</sub>
- **[SCENIC](http://scenic.aertslab.org)**: Single-cell regulatory network inference; regulons rather than raw correlations
  <sub>[code](https://github.com/aertslab/SCENIC) · [bio.tools](https://bio.tools/scenic) · [paper](https://pubmed.ncbi.nlm.nih.gov/28991892/) · `491 stars`</sub>

<sub>[+ 135 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=single-cell)</sub>

## Comparative & evolutionary

*Cross-species conservation and evolution of regulatory sequence.*

- **[TFBSFootprinter](https://github.com/thirtysix/TFBS_footprinting3)**: Multi-evidence TFBS scoring combining conservation, CAGE, eQTL and chromatin data
  <sub>[code](https://github.com/thirtysix/TFBS_footprinting3) · [paper](https://pubmed.ncbi.nlm.nih.gov/40646689/)</sub>

<sub>[+ 34 more in this category →](https://thirtysix.github.io/awesome-regulatory-genomics/?category=comparative)</sub>

## Running the pipeline

```bash
pip install -r requirements.txt
cp .env.example .env        # optional; see below
make test                   # unit-test the scope and linking rules
make curate                 # rebuild README and site from committed data
make all                    # re-select, enrich, resolve links, rebuild
make serve PORT=8000        # preview the site locally
```

`make test` needs `pip install -r requirements-dev.txt` and runs offline. It covers the three functions that decide the catalog's boundary, its repository links and its citation counts, using the real records that motivated each rule. Run it before changing [`pipeline/config.py`](pipeline/config.py): every regression this project has shipped came from loosening one of those rules, and the tests encode why each is written the way it is.

`.env` holds two optional settings, both blank by default:

- `CONTACT_EMAIL` identifies the client to the OpenAlex and Crossref *polite pools*, which give faster and more reliable service to callers that say who they are. Leave it unset and the pipeline omits the parameter rather than sending a placeholder, since a fake address there is worse than none.
- `DEEPINFRA_API_KEY` is needed only by the optional model stages (`make llm`, `make bench`, `make verify-additions`). Their results are cached and committed, so a normal build never asks for it.

## How this list is built

```
harvest.py        wide sweep of bio.tools (EDAM operation + free-text queries)
select_domain.py  tiered precision filter -> what is in scope
discover_registries.py  the same filter over Bioconductor and Galaxy,
                  for tools bio.tools does not index at all
enrich.py         resolve source repos, GitHub activity, OpenAlex citations
resolve_repos.py  find repos bio.tools omits (bioconda/PyPI/homepage), validated
resolve_pubs.py   upgrade preprint links to the published version, check DOIs
build.py          merge with curated seeds, assign categories, apply overlay
render.py         write README.md and the searchable site
audit_coverage.py measure recall against a hand-written benchmark
```

**Harvesting and selection never call an LLM.** They are set membership on EDAM terms, compiled regex and API lookups, so the scope of the catalog is reproducible and every rule is readable in [`pipeline/config.py`](pipeline/config.py). Categories and descriptions are then refined by an *optional* model pass ([`docs/llm-stage.md`](docs/llm-stage.md)) that writes to a review file merged below the hand-written overlay; `make build-strict` ignores it entirely and rebuilds on rules alone. Removing a record needs two different models to agree independently, and never overrides a hand-vetted entry. Additions get the mirror check from a third model ([`docs/addition-review.md`](docs/addition-review.md)), which is how a name collision between the MEME Suite's MAST and the unrelated single-cell package of the same name was caught.

Two design decisions are worth stating, because they are where most tool tables go wrong:

**Recall and precision are separated.** bio.tools' `operation=` parameter is a fuzzy text match, not an ontology lookup. Quoting matters more than it should: `q="cis-regulatory"` returns 107 records, while the same query unquoted returns about 3,500, matching "cis" *or* "regulatory". So the sweep is deliberately over-broad and precision is restored afterwards by filtering on the annotations a record actually carries.

**EDAM annotations are not trusted on their own.** They are frequently wrong, and wrong in ways no query can anticipate: HOCOMOCO, a motif database, is filed under *Data handling*; SICER, a ChIP-seq peak caller, under *Sequence contamination filtering*; ChIP-Atlas, a data portal, under *Genome assembly*. Whole operations belong to another field: of the 204 records carrying *Peak detection*, roughly three in four are proteomics, metabolomics or NMR tools. Operations are therefore tiered. Seventeen specific terms admit a record on their own; five ambiguous ones that bio.tools also applies to protein motifs, RNA structure and orthology need a corroborating topic or text signal; and five that belong to a different field outright are documented in `REJECTED_OPERATIONS`, never queried and never able to admit anything. A text-match escape hatch recovers in-domain tools with no usable annotation at all. Every accepted record stores the rule that admitted it (`_select_reason`), and every rejected one is written to [`data/raw/rejected.json`](data/raw/rejected.json) so the boundary can be argued with rather than taken on trust.

## Coverage and known gaps

- **1951 tools**: 1822 harvested from bio.tools, 129 added by hand because bio.tools does not index them.
- **988 (51%) have a resolvable source repository.** bio.tools rarely records one directly, so repositories are also recovered from Bioconductor, CRAN and PyPI metadata, from bioconda recipes and from links on the tool's own homepage. Every candidate is validated against the tool's description before it is used: matching on name alone resolves MEME to a meme generator and MEDUSA to a genome scaffolder that merely shares the name. Near-misses are listed in [`docs/repo-review.md`](docs/repo-review.md) rather than applied. Publication links get the same treatment in [`docs/link-check.md`](docs/link-check.md), which records every preprint upgraded to its published version and every DOI that does not resolve.

**If you maintain a tool listed here and its link is wrong, please say so.** Of the 988 links shown, 907 are recorded upstream, 31 are hand-verified and 50 are *inferred* from a homepage or a GitHub search. Inferred links are marked with a dotted underline on the [catalog site](https://thirtysix.github.io/awesome-regulatory-genomics/) and carry a one-click report button; there are [issue templates](.github/ISSUE_TEMPLATE) for a wrong repository and for a wrong category, description or scope decision. Correcting the entry at [bio.tools](https://bio.tools) instead fixes it here on the next refresh, and for every other consumer of that registry.
- **1269 (65%) have a website of their own**, meaning a project page, web server or database front end that is not just their source repository. The rest live on a code host alone. The catalog site shows this as a sortable *Site* column, so "web-only resource" and "code, no documentation site" are both answerable questions.
- **413 can be installed from a package registry** (Bioconductor, CRAN, PyPI, conda or Docker), shown as a sortable *Install* column. "Can I install this today?" is a more useful maintenance signal than a star count, and it is not a question bio.tools answers. A package is only linked when its description agrees with the tool's, never on a matching name: bioconda's `medusa` is a genome scaffolder, and this catalog's MEDUSA is a motif model.
- **130 links are known to be dead** and are struck through on the catalog site rather than quietly left to disappoint. Every homepage is checked (`make check-links`), which matters because nearly half this catalog has no repository, only a homepage, and academic URLs rot. Only a 404 or 410 counts: a timeout is as often a slow institutional host as a departed one, and 429 means the server is up and busy. The full grading is in [`docs/homepage-check.md`](docs/homepage-check.md).
- **1828 have a publication year**, recovered from OpenAlex where the registry did not record one.
- **19 tools are featured** in the curated sections above; the rest are in the [full catalog](https://thirtysix.github.io/awesome-regulatory-genomics/).

Honest limitations:

- bio.tools skews toward tools with a publication and an ELIXIR-adjacent submitter. The sequence-to-function deep-learning literature is badly under-represented there; those entries come from `curation/seeds.yaml` and are necessarily incomplete. `make discover` widens this by running the same selection rules over registries that carry their own domain taxonomy (Bioconductor's `biocViews`, the Galaxy ToolShed), which is how tools like AlphaGenome, Cicero and Chromap reached this list; candidates land in [`docs/registry-discovery.md`](docs/registry-discovery.md) for review rather than being added automatically.
- Citation counts are the OpenAlex `cited_by_count` of a tool's **primary** publication only. Summing every linked publication, which is what the original dissertation script did, is badly wrong here: bio.tools attaches a suite's paper to each of its members, so the EMBOSS paper is linked to dozens of EMBOSS commands and the Bioconductor paper to 23 packages in this sweep, handing each member the whole suite's count. Where a primary publication is itself shared by three or more tools, no count is shown at all, because the member's own impact is genuinely unknown. Treat what remains as a rough popularity signal, not a quality measure.
- Categories are assigned by rule, then corrected by hand where wrong. The rules catch the systematic errors (bio.tools files orthology tools under *Phylogenetic footprinting* and mass-spectrometry tools under *Peak detection*), but a tail of individual mis-categorisations remains. Please open an issue, or see [`docs/llm-stage.md`](docs/llm-stage.md) for the optional classifier that targets exactly this tail.
- A tool being listed is not an endorsement, and the absence of a repository link often means the tool is web-only, not that it is unmaintained.

Recall against a hand-written benchmark of standard resources is tracked in [`docs/coverage.md`](docs/coverage.md) and regenerated by `make audit`, so "did it find the obvious things?" is a number rather than an impression.

## Contributing

Additions, corrections and re-categorisations are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md). Edit [`curation/seeds.yaml`](curation/seeds.yaml) or [`curation/overlay.yaml`](curation/overlay.yaml); never edit `README.md` or `data/catalog.*` directly, as both are regenerated.

## Provenance

This catalog began as a table in a doctoral dissertation on transcription-factor binding site prediction. That table and the scripts that produced it are kept in [`dissertation/`](dissertation/) for citation, edited only to redact five absolute working-directory paths; [`docs/provenance.md`](docs/provenance.md) documents how it was derived and what this catalog changes.

## Licence

Catalog data: [CC BY 4.0](LICENSE-DATA). Pipeline code: [MIT](LICENSE). Tool metadata originates from [bio.tools](https://bio.tools) (CC BY 4.0) and [OpenAlex](https://openalex.org) (CC0).
