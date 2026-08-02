# Coverage audit

Generated 2026-08-02 by `make audit`, against [`curation/benchmark.yaml`](../curation/benchmark.yaml).

The benchmark is a hand-written list of resources the field treats as standard. It is not a ranking and not exhaustive. It exists so that "did the pipeline find the obvious things?" is a measurement rather than an impression.

**79 of 221 benchmark tools present (36%).** Catalog size: 204 tools.

## Misses

Each of these is a bug, and the diagnosis says which kind. *Never harvested* means no query reaches the record, so widen `QUERY_TOPICS` or `QUERY_FREETEXT`. *Rejected* means the selection rules in `pipeline/config.py` are too strict. *Absent from bio.tools* means it belongs in `curation/seeds.yaml`.

| Group | Tool | Diagnosis |
| --- | --- | --- |
| motif discovery | MEME | absent from bio.tools; add to `seeds.yaml` |
| motif discovery | STREME | absent from bio.tools; add to `seeds.yaml` |
| motif discovery | HOMER | absent from bio.tools; add to `seeds.yaml` |
| motif discovery | Weeder | absent from bio.tools; add to `seeds.yaml` |
| motif discovery | AlignACE | absent from bio.tools; add to `seeds.yaml` |
| motif discovery | MDscan | absent from bio.tools; add to `seeds.yaml` |
| motif discovery | ChIPMunk | absent from bio.tools; add to `seeds.yaml` |
| motif discovery | RSAT | absent from bio.tools; add to `seeds.yaml` |
| motif discovery | BaMMmotif | absent from bio.tools; add to `seeds.yaml` |
| motif scanning and enrichment | MOODS | absent from bio.tools; add to `seeds.yaml` |
| motif scanning and enrichment | PWMScan | absent from bio.tools; add to `seeds.yaml` |
| motif scanning and enrichment | TFBSTools | absent from bio.tools; add to `seeds.yaml` |
| motif scanning and enrichment | PWMEnrich | absent from bio.tools; add to `seeds.yaml` |
| motif and TF databases | JASPAR | absent from bio.tools; add to `seeds.yaml` |
| motif and TF databases | HOCOMOCO | absent from bio.tools; add to `seeds.yaml` |
| motif and TF databases | TRANSFAC | absent from bio.tools; add to `seeds.yaml` |
| motif and TF databases | UniBind | absent from bio.tools; add to `seeds.yaml` |
| motif and TF databases | RegulonDB | absent from bio.tools; add to `seeds.yaml` |
| motif and TF databases | AnimalTFDB | absent from bio.tools; add to `seeds.yaml` |
| motif and TF databases | hTFtarget | absent from bio.tools; add to `seeds.yaml` |
| motif and TF databases | TFLink | absent from bio.tools; add to `seeds.yaml` |
| peak calling and annotation | MACS | absent from bio.tools; add to `seeds.yaml` |
| peak calling and annotation | SEACR | absent from bio.tools; add to `seeds.yaml` |
| peak calling and annotation | SICER | absent from bio.tools; add to `seeds.yaml` |
| peak calling and annotation | ChIPseeker | absent from bio.tools; add to `seeds.yaml` |
| peak calling and annotation | GREAT | absent from bio.tools; add to `seeds.yaml` |
| peak calling and annotation | BART | absent from bio.tools; add to `seeds.yaml` |
| ChIP and ATAC resources | GTRD | absent from bio.tools; add to `seeds.yaml` |
| ChIP and ATAC resources | ReMap | absent from bio.tools; add to `seeds.yaml` |
| ChIP and ATAC resources | ChIP-Atlas | absent from bio.tools; add to `seeds.yaml` |
| ChIP and ATAC resources | ENCODE | absent from bio.tools; add to `seeds.yaml` |
| gene regulatory networks | RcisTarget | absent from bio.tools; add to `seeds.yaml` |
| gene regulatory networks | GENIE3 | absent from bio.tools; add to `seeds.yaml` |
| gene regulatory networks | chromVAR | absent from bio.tools; add to `seeds.yaml` |
| regulatory variants | SNP2TFBS | absent from bio.tools; add to `seeds.yaml` |
| regulatory variants | FABIAN-variant | absent from bio.tools; add to `seeds.yaml` |
| motif comparison and visualisation | Tomtom | absent from bio.tools; add to `seeds.yaml` |
| motif comparison and visualisation | STAMP | absent from bio.tools; add to `seeds.yaml` |
| motif comparison and visualisation | MoSBAT | absent from bio.tools; add to `seeds.yaml` |
| motif comparison and visualisation | matrix-clustering | absent from bio.tools; add to `seeds.yaml` |
| motif comparison and visualisation | universalmotif | absent from bio.tools; add to `seeds.yaml` |
| motif comparison and visualisation | seqLogo | absent from bio.tools; add to `seeds.yaml` |
| nucleosome and chromatin state | ChromHMM | absent from bio.tools; add to `seeds.yaml` |
| nucleosome and chromatin state | Segway | absent from bio.tools; add to `seeds.yaml` |
| nucleosome and chromatin state | NucleoATAC | absent from bio.tools; add to `seeds.yaml` |
| nucleosome and chromatin state | iNPS | absent from bio.tools; add to `seeds.yaml` |
| nucleosome and chromatin state | NucTools | absent from bio.tools; add to `seeds.yaml` |
| nucleosome and chromatin state | NuPoP | absent from bio.tools; add to `seeds.yaml` |
| single-cell regulatory genomics | Signac | absent from bio.tools; add to `seeds.yaml` |
| single-cell regulatory genomics | ArchR | absent from bio.tools; add to `seeds.yaml` |
| single-cell regulatory genomics | cisTopic | absent from bio.tools; add to `seeds.yaml` |
| single-cell regulatory genomics | MAESTRO | absent from bio.tools; add to `seeds.yaml` |
| single-cell regulatory genomics | chromVAR | absent from bio.tools; add to `seeds.yaml` |
| single-cell regulatory genomics | scATAC-pro | absent from bio.tools; add to `seeds.yaml` |
| harder motif discovery | MEME-ChIP | absent from bio.tools; add to `seeds.yaml` |
| harder motif discovery | Weeder | absent from bio.tools; add to `seeds.yaml` |
| harder motif discovery | Improbizer | absent from bio.tools; add to `seeds.yaml` |
| harder motif discovery | Amadeus | absent from bio.tools; add to `seeds.yaml` |
| harder motif discovery | CisFinder | absent from bio.tools; add to `seeds.yaml` |
| harder motif discovery | ProSampler | absent from bio.tools; add to `seeds.yaml` |
| harder motif discovery | GADEM | absent from bio.tools; add to `seeds.yaml` |
| harder motif discovery | XXmotif | absent from bio.tools; add to `seeds.yaml` |
| harder peak calling | MACS | absent from bio.tools; add to `seeds.yaml` |
| harder peak calling | HMMRATAC | absent from bio.tools; add to `seeds.yaml` |
| harder peak calling | SEACR | absent from bio.tools; add to `seeds.yaml` |
| harder peak calling | LanceOtron | absent from bio.tools; add to `seeds.yaml` |
| harder peak calling | THOR | absent from bio.tools; add to `seeds.yaml` |
| harder peak calling | PePr | absent from bio.tools; add to `seeds.yaml` |
| harder peak calling | csaw | absent from bio.tools; add to `seeds.yaml` |
| harder peak calling | JAMM | absent from bio.tools; add to `seeds.yaml` |
| harder peak calling | Ritornello | absent from bio.tools; add to `seeds.yaml` |
| harder peak calling | BCP | absent from bio.tools; add to `seeds.yaml` |
| harder footprinting | BaGFoot | absent from bio.tools; add to `seeds.yaml` |
| harder footprinting | DNase2TF | absent from bio.tools; add to `seeds.yaml` |
| harder footprinting | seqOutBias | absent from bio.tools; add to `seeds.yaml` |
| harder footprinting | Romulus | absent from bio.tools; add to `seeds.yaml` |
| harder gene regulatory networks | GRNBoost2 | absent from bio.tools; add to `seeds.yaml` |
| harder gene regulatory networks | CLR | absent from bio.tools; add to `seeds.yaml` |
| harder gene regulatory networks | SCODE | absent from bio.tools; add to `seeds.yaml` |
| harder gene regulatory networks | PIDC | absent from bio.tools; add to `seeds.yaml` |
| harder gene regulatory networks | CellOracle | absent from bio.tools; add to `seeds.yaml` |
| harder gene regulatory networks | Pando | absent from bio.tools; add to `seeds.yaml` |
| harder gene regulatory networks | FigR | absent from bio.tools; add to `seeds.yaml` |
| harder regulatory variants | deltaSVM | absent from bio.tools; add to `seeds.yaml` |
| harder regulatory variants | SNP2TFBS | absent from bio.tools; add to `seeds.yaml` |
| harder peak annotation | annotatr | absent from bio.tools; add to `seeds.yaml` |
| harder peak annotation | PAVIS | absent from bio.tools; add to `seeds.yaml` |
| harder peak annotation | DiffBind | absent from bio.tools; add to `seeds.yaml` |
| harder ChIP and ATAC resources | SEdb | absent from bio.tools; add to `seeds.yaml` |
| harder ChIP and ATAC resources | ChIPBase | absent from bio.tools; add to `seeds.yaml` |
| DNA methylation | Bismark | absent from bio.tools; add to `seeds.yaml` |
| DNA methylation | methylKit | absent from bio.tools; add to `seeds.yaml` |
| DNA methylation | DSS | absent from bio.tools; add to `seeds.yaml` |
| DNA methylation | BS-Seeker2 | absent from bio.tools; add to `seeds.yaml` |
| DNA methylation | MOABS | absent from bio.tools; add to `seeds.yaml` |
| DNA methylation | metilene | absent from bio.tools; add to `seeds.yaml` |
| DNA methylation | DMRcate | absent from bio.tools; add to `seeds.yaml` |
| DNA methylation | minfi | absent from bio.tools; add to `seeds.yaml` |
| DNA methylation | ChAMP | absent from bio.tools; add to `seeds.yaml` |
| DNA methylation | MethylDackel | absent from bio.tools; add to `seeds.yaml` |
| DNA methylation | RnBeads | absent from bio.tools; add to `seeds.yaml` |
| DNA methylation | SeSAMe | absent from bio.tools; add to `seeds.yaml` |
| DNA methylation | MethylSeekR | absent from bio.tools; add to `seeds.yaml` |
| DNA methylation | methylpy | absent from bio.tools; add to `seeds.yaml` |
| 3D genome and chromatin interactions | Juicer | absent from bio.tools; add to `seeds.yaml` |
| 3D genome and chromatin interactions | HiC-Pro | absent from bio.tools; add to `seeds.yaml` |
| 3D genome and chromatin interactions | cooler | absent from bio.tools; add to `seeds.yaml` |
| 3D genome and chromatin interactions | cooltools | absent from bio.tools; add to `seeds.yaml` |
| 3D genome and chromatin interactions | FAN-C | absent from bio.tools; add to `seeds.yaml` |
| 3D genome and chromatin interactions | HiCExplorer | absent from bio.tools; add to `seeds.yaml` |
| 3D genome and chromatin interactions | TADbit | absent from bio.tools; add to `seeds.yaml` |
| 3D genome and chromatin interactions | HiCCUPS | absent from bio.tools; add to `seeds.yaml` |
| 3D genome and chromatin interactions | Arrowhead | absent from bio.tools; add to `seeds.yaml` |
| 3D genome and chromatin interactions | mustache | absent from bio.tools; add to `seeds.yaml` |
| 3D genome and chromatin interactions | Peakachu | absent from bio.tools; add to `seeds.yaml` |
| 3D genome and chromatin interactions | FitHiC | absent from bio.tools; add to `seeds.yaml` |
| 3D genome and chromatin interactions | HiCRep | absent from bio.tools; add to `seeds.yaml` |
| 3D genome and chromatin interactions | CHESS | absent from bio.tools; add to `seeds.yaml` |
| 3D genome and chromatin interactions | coolpup.py | absent from bio.tools; add to `seeds.yaml` |
| 3D genome and chromatin interactions | MoDLE | absent from bio.tools; add to `seeds.yaml` |
| histone modifications | ChromHMM | absent from bio.tools; add to `seeds.yaml` |
| histone modifications | Segway | absent from bio.tools; add to `seeds.yaml` |
| histone modifications | ROSE | absent from bio.tools; add to `seeds.yaml` |
| histone modifications | SEdb | absent from bio.tools; add to `seeds.yaml` |
| histone modifications | epilogos | absent from bio.tools; add to `seeds.yaml` |
| histone modifications | chromswitch | absent from bio.tools; add to `seeds.yaml` |
| histone modifications | EpiCSeq | absent from bio.tools; add to `seeds.yaml` |
| reporter assays | MPRAnalyze | absent from bio.tools; add to `seeds.yaml` |
| reporter assays | mpralm | absent from bio.tools; add to `seeds.yaml` |
| reporter assays | MPRAflow | absent from bio.tools; add to `seeds.yaml` |
| reporter assays | starrpeaker | absent from bio.tools; add to `seeds.yaml` |
| reporter assays | CRADLE | absent from bio.tools; add to `seeds.yaml` |
| reporter assays | BasicStarrSeq | absent from bio.tools; add to `seeds.yaml` |
| molecular QTL | Matrix eQTL | absent from bio.tools; add to `seeds.yaml` |
| molecular QTL | FastQTL | absent from bio.tools; add to `seeds.yaml` |
| molecular QTL | QTLtools | absent from bio.tools; add to `seeds.yaml` |
| molecular QTL | tensorQTL | absent from bio.tools; add to `seeds.yaml` |
| molecular QTL | RASQUAL | absent from bio.tools; add to `seeds.yaml` |
| molecular QTL | mashr | absent from bio.tools; add to `seeds.yaml` |
| molecular QTL | coloc | absent from bio.tools; add to `seeds.yaml` |
| molecular QTL | SuSiE | absent from bio.tools; add to `seeds.yaml` |
| molecular QTL | QTLbase | absent from bio.tools; add to `seeds.yaml` |

## Full results

### motif discovery: 3/12

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| MEME | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| STREME | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| DREME | ✅ | DREME | curated seed |
| HOMER | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| Weeder | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| AlignACE | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| MDscan | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| ChIPMunk | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| RSAT | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| BaMMmotif | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| TF-MoDISco | ✅ | TF-MoDISco | curated seed |
| gkm-SVM | ✅ | gkm-SVM / LS-GKM | curated seed |

### motif scanning and enrichment: 7/11

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| FIMO | ✅ | FIMO | curated seed |
| CentriMo | ✅ | CentriMo | curated seed |
| AME | ✅ | AME | curated seed |
| MAST | ✅ | MAST | curated seed |
| MOODS | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| PWMScan | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| Cluster-Buster | ✅ | Cluster-Buster | curated seed |
| TFBSTools | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| motifmatchr | ✅ | motifmatchr | curated seed |
| PWMEnrich | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| monaLisa | ✅ | monaLisa | curated seed |

### motif and TF databases: 7/15

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| JASPAR | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| HOCOMOCO | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| CIS-BP | ✅ | CIS-BP | curated seed |
| TRANSFAC | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| SwissRegulon | ✅ | SwissRegulon | bio.tools |
| UniPROBE | ✅ | UniPROBE | bio.tools |
| Factorbook | ✅ | Factorbook.org | curated seed |
| UniBind | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| CollecTF | ✅ | CollecTF | curated seed |
| RegulonDB | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| footprintDB | ✅ | footprintDB | curated seed |
| AnimalTFDB | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| hTFtarget | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| TRRUST | ✅ | TRRUST | curated seed |
| TFLink | ❌ |  | absent from bio.tools; add to `seeds.yaml` |

### sequence-to-function models: 13/13

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| DeepBind | ✅ | DeepBind | curated seed |
| DeepSEA | ✅ | DeepSEA | curated seed |
| Basset | ✅ | Basset | curated seed |
| Basenji | ✅ | Basenji | curated seed |
| Enformer | ✅ | Enformer | curated seed |
| Borzoi | ✅ | Borzoi | curated seed |
| DanQ | ✅ | DanQ | curated seed |
| BPNet | ✅ | BPNet | curated seed |
| ChromBPNet | ✅ | ChromBPNet | curated seed |
| Sei | ✅ | Sei | curated seed |
| DeepSTARR | ✅ | DeepSTARR | curated seed |
| scBasset | ✅ | scBasset | curated seed |
| gReLU | ✅ | gReLU | curated seed |

### footprinting: 7/7

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| TOBIAS | ✅ | TOBIAS | curated seed |
| HINT-ATAC | ✅ | HINT-ATAC | curated seed |
| PIQ | ✅ | PIQ | curated seed |
| Wellington | ✅ | Wellington / pyDNase | curated seed |
| CENTIPEDE | ✅ | CENTIPEDE | curated seed |
| msCentipede | ✅ | msCentipede | curated seed |
| TFBSFootprinter | ✅ | TFBSFootprinter | curated seed |

### peak calling and annotation: 3/9

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| MACS | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| SEACR | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| Genrich | ✅ | Genrich | curated seed |
| GoPeaks | ✅ | GoPeaks | curated seed |
| SICER | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| ChIPseeker | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| GREAT | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| LOLA | ✅ | LOLA | curated seed |
| BART | ❌ |  | absent from bio.tools; add to `seeds.yaml` |

### ChIP and ATAC resources: 1/5

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| GTRD | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| ReMap | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| ChIP-Atlas | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| Cistrome | ✅ | CistromeMap | curated seed |
| ENCODE | ❌ |  | absent from bio.tools; add to `seeds.yaml` |

### gene regulatory networks: 6/9

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| SCENIC | ✅ | SCENIC+ | curated seed |
| pySCENIC | ✅ | pySCENIC | curated seed |
| SCENIC+ | ✅ | SCENIC+ | curated seed |
| RcisTarget | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| GENIE3 | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| ARACNe | ✅ | ARACNE | bio.tools |
| chromVAR | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| iRegulon | ✅ | iRegulon | curated seed |
| i-cisTarget | ✅ | i-cisTarget | curated seed |

### regulatory variants: 6/8

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| motifbreakR | ✅ | motifbreakR | curated seed |
| SNP2TFBS | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| atSNP | ✅ | atSNP | bio.tools |
| RegulomeDB | ✅ | RegulomeDB | curated seed |
| HaploReg | ✅ | HaploReg | bio.tools |
| GWAVA | ✅ | GWAVA | curated seed |
| FunSeq2 | ✅ | FunSeq2 | curated seed |
| FABIAN-variant | ❌ |  | absent from bio.tools; add to `seeds.yaml` |

### motif comparison and visualisation: 2/8

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| Tomtom | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| STAMP | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| MoSBAT | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| matrix-clustering | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| universalmotif | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| ggseqlogo | ✅ | ggseqlogo | bio.tools |
| Logolas | ✅ | Logolas | bio.tools |
| seqLogo | ❌ |  | absent from bio.tools; add to `seeds.yaml` |

### nucleosome and chromatin state: 2/8

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| ChromHMM | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| Segway | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| NucleoATAC | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| DANPOS | ✅ | DANPOS | bio.tools |
| iNPS | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| NucTools | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| nucleR | ✅ | nucleR | curated seed |
| NuPoP | ❌ |  | absent from bio.tools; add to `seeds.yaml` |

### single-cell regulatory genomics: 4/10

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| Signac | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| ArchR | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| SnapATAC | ✅ | SnapATAC2 | curated seed |
| cisTopic | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| scBasset | ✅ | scBasset | curated seed |
| MAESTRO | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| Cicero | ✅ | Cicero | curated seed |
| chromVAR | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| scATAC-pro | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| PeakVI | ✅ | PeakVI | curated seed |

### harder motif discovery: 0/8

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| MEME-ChIP | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| Weeder | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| Improbizer | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| Amadeus | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| CisFinder | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| ProSampler | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| GADEM | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| XXmotif | ❌ |  | absent from bio.tools; add to `seeds.yaml` |

### harder peak calling: 2/12

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| MACS | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| SICER | ✅ | epic2 | curated seed |
| HMMRATAC | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| SEACR | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| LanceOtron | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| THOR | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| PePr | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| csaw | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| MSPC | ✅ | rmspc | curated seed |
| JAMM | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| Ritornello | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| BCP | ❌ |  | absent from bio.tools; add to `seeds.yaml` |

### harder footprinting: 2/6

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| Wellington | ✅ | Wellington-bootstrap | curated seed |
| BaGFoot | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| DNase2TF | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| seqOutBias | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| Romulus | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| msCentipede | ✅ | msCentipede | curated seed |

### harder gene regulatory networks: 1/8

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| GRNBoost2 | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| CLR | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| SCODE | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| PIDC | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| CellOracle | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| Pando | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| FigR | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| Dictys | ✅ | Dictys | curated seed |

### harder regulatory variants: 6/8

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| deltaSVM | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| motifbreakR | ✅ | motifbreakR | curated seed |
| SNP2TFBS | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| GWAVA | ✅ | GWAVA | curated seed |
| FunSeq2 | ✅ | FunSeq2 | curated seed |
| RegulomeDB | ✅ | RegulomeDB | curated seed |
| Sasquatch | ✅ | Sasquatch | curated seed |
| GERV | ✅ | GERV | curated seed |

### harder peak annotation: 2/5

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| rGREAT | ✅ | rGREAT | bio.tools |
| annotatr | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| PAVIS | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| LOLA | ✅ | LOLA | curated seed |
| DiffBind | ❌ |  | absent from bio.tools; add to `seeds.yaml` |

### harder ChIP and ATAC resources: 4/6

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| Cistrome DB | ✅ | CistromeMap | curated seed |
| SEdb | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| dbSUPER | ✅ | dbSUPER | bio.tools |
| ChIPBase | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| CistromeMap | ✅ | CistromeMap | curated seed |
| hmChIP | ✅ | hmChIP | curated seed |

### DNA methylation: 0/14

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| Bismark | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| methylKit | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| DSS | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| BS-Seeker2 | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| MOABS | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| metilene | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| DMRcate | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| minfi | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| ChAMP | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| MethylDackel | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| RnBeads | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| SeSAMe | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| MethylSeekR | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| methylpy | ❌ |  | absent from bio.tools; add to `seeds.yaml` |

### 3D genome and chromatin interactions: 0/16

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| Juicer | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| HiC-Pro | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| cooler | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| cooltools | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| FAN-C | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| HiCExplorer | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| TADbit | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| HiCCUPS | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| Arrowhead | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| mustache | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| Peakachu | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| FitHiC | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| HiCRep | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| CHESS | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| coolpup.py | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| MoDLE | ❌ |  | absent from bio.tools; add to `seeds.yaml` |

### histone modifications: 1/8

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| ChromHMM | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| Segway | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| ROSE | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| dbSUPER | ✅ | dbSUPER | bio.tools |
| SEdb | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| epilogos | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| chromswitch | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| EpiCSeq | ❌ |  | absent from bio.tools; add to `seeds.yaml` |

### reporter assays: 0/6

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| MPRAnalyze | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| mpralm | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| MPRAflow | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| starrpeaker | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| CRADLE | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| BasicStarrSeq | ❌ |  | absent from bio.tools; add to `seeds.yaml` |

### molecular QTL: 0/9

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| Matrix eQTL | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| FastQTL | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| QTLtools | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| tensorQTL | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| RASQUAL | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| mashr | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| coloc | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| SuSiE | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| QTLbase | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
