# Coverage audit

Generated 2026-07-31 by `make audit`, against [`curation/benchmark.yaml`](../curation/benchmark.yaml).

The benchmark is a hand-written list of resources the field treats as standard. It is not a ranking and not exhaustive. It exists so that "did the pipeline find the obvious things?" is a measurement rather than an impression.

**153 of 221 benchmark tools present (69%).** Catalog size: 1948 tools.

## Misses

Each of these is a bug, and the diagnosis says which kind. *Never harvested* means no query reaches the record, so widen `QUERY_TOPICS` or `QUERY_FREETEXT`. *Rejected* means the selection rules in `pipeline/config.py` are too strict. *Absent from bio.tools* means it belongs in `curation/seeds.yaml`.

| Group | Tool | Diagnosis |
| --- | --- | --- |
| motif comparison and visualisation | Tomtom | not found |
| motif comparison and visualisation | MoSBAT | not found |
| motif comparison and visualisation | universalmotif | not found |
| motif comparison and visualisation | ggseqlogo | not found |
| motif comparison and visualisation | Logolas | not found |
| nucleosome and chromatin state | DANPOS | not found |
| nucleosome and chromatin state | iNPS | not found |
| nucleosome and chromatin state | NucTools | not found |
| single-cell regulatory genomics | MAESTRO | not found |
| harder motif discovery | MEME-ChIP | not found |
| harder motif discovery | Improbizer | not found |
| harder motif discovery | Amadeus | not found |
| harder motif discovery | CisFinder | not found |
| harder peak calling | HMMRATAC | not found |
| harder peak calling | THOR | not found |
| harder peak calling | Ritornello | not found |
| harder peak calling | BCP | not found |
| harder footprinting | BaGFoot | not found |
| harder footprinting | DNase2TF | not found |
| harder footprinting | seqOutBias | not found |
| harder footprinting | Romulus | not found |
| harder gene regulatory networks | CLR | not found |
| harder gene regulatory networks | SCODE | not found |
| harder gene regulatory networks | PIDC | not found |
| harder gene regulatory networks | CellOracle | not found |
| harder gene regulatory networks | Pando | not found |
| harder gene regulatory networks | FigR | not found |
| harder regulatory variants | deltaSVM | not found |
| harder peak annotation | rGREAT | not found |
| harder peak annotation | PAVIS | not found |
| harder ChIP and ATAC resources | dbSUPER | not found |
| DNA methylation | methylKit | not found |
| DNA methylation | DSS | not found |
| DNA methylation | MOABS | not found |
| DNA methylation | metilene | not found |
| DNA methylation | DMRcate | not found |
| DNA methylation | minfi | not found |
| DNA methylation | ChAMP | not found |
| DNA methylation | SeSAMe | not found |
| DNA methylation | methylpy | not found |
| 3D genome and chromatin interactions | Juicer | not found |
| 3D genome and chromatin interactions | HiC-Pro | not found |
| 3D genome and chromatin interactions | cooler | not found |
| 3D genome and chromatin interactions | FAN-C | not found |
| 3D genome and chromatin interactions | HiCExplorer | not found |
| 3D genome and chromatin interactions | TADbit | not found |
| 3D genome and chromatin interactions | HiCCUPS | not found |
| 3D genome and chromatin interactions | Arrowhead | not found |
| 3D genome and chromatin interactions | FitHiC | not found |
| 3D genome and chromatin interactions | HiCRep | not found |
| 3D genome and chromatin interactions | CHESS | not found |
| 3D genome and chromatin interactions | coolpup.py | not found |
| histone modifications | ROSE | not found |
| histone modifications | dbSUPER | not found |
| histone modifications | epilogos | not found |
| histone modifications | chromswitch | not found |
| histone modifications | EpiCSeq | not found |
| reporter assays | mpralm | not found |
| reporter assays | MPRAflow | not found |
| reporter assays | CRADLE | not found |
| molecular QTL | Matrix eQTL | not found |
| molecular QTL | FastQTL | not found |
| molecular QTL | QTLtools | not found |
| molecular QTL | tensorQTL | not found |
| molecular QTL | RASQUAL | not found |
| molecular QTL | mashr | not found |
| molecular QTL | coloc | not found |
| molecular QTL | SuSiE | not found |

## Full results

### motif discovery: 12/12

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| MEME | ✅ | MEME Suite | bio.tools |
| STREME | ✅ | STREME | bio.tools |
| DREME | ✅ | DREME | curated seed |
| HOMER | ✅ | homer | bio.tools |
| Weeder | ✅ | Weeder | bio.tools |
| AlignACE | ✅ | AlignACE | bio.tools |
| MDscan | ✅ | MDscan | bio.tools |
| ChIPMunk | ✅ | ChIPMunk | bio.tools |
| RSAT | ✅ | RSAT suite | bio.tools |
| BaMMmotif | ✅ | BaMM | bio.tools |
| TF-MoDISco | ✅ | TF-MoDISco | curated seed |
| gkm-SVM | ✅ | gkm-SVM / LS-GKM | curated seed |

### motif scanning and enrichment: 11/11

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| FIMO | ✅ | FIMO | curated seed |
| CentriMo | ✅ | CentriMo | curated seed |
| AME | ✅ | AME | curated seed |
| MAST | ✅ | MAST | curated seed |
| MOODS | ✅ | MOODS | bio.tools |
| PWMScan | ✅ | PWMScan | bio.tools |
| Cluster-Buster | ✅ | Cluster Buster | bio.tools |
| TFBSTools | ✅ | TFBSTools | bio.tools |
| motifmatchr | ✅ | motifmatchr | curated seed |
| PWMEnrich | ✅ | PWMEnrich | bio.tools |
| monaLisa | ✅ | monaLisa | curated seed |

### motif and TF databases: 15/15

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| JASPAR | ✅ | JASPAR | bio.tools |
| HOCOMOCO | ✅ | HOCOMOCO | bio.tools |
| CIS-BP | ✅ | CIS-BP | curated seed |
| TRANSFAC | ✅ | TRANSFAC | bio.tools |
| SwissRegulon | ✅ | SwissRegulon | bio.tools |
| UniPROBE | ✅ | UniPROBE | bio.tools |
| Factorbook | ✅ | Factorbook | bio.tools |
| UniBind | ✅ | UniBind | bio.tools |
| CollecTF | ✅ | CollecTF | curated seed |
| RegulonDB | ✅ | RegulonDB | bio.tools |
| footprintDB | ✅ | footprintDB | curated seed |
| AnimalTFDB | ✅ | Animal Transcription Factor Database | bio.tools |
| hTFtarget | ✅ | hTFtarget | bio.tools |
| TRRUST | ✅ | TRRUST | curated seed |
| TFLink | ✅ | TFLink | bio.tools |

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
| ChromBPNet | ✅ | ChromBPNet | bio.tools |
| Sei | ✅ | Sei | curated seed |
| DeepSTARR | ✅ | DeepSTARR | curated seed |
| scBasset | ✅ | scBasset | bio.tools |
| gReLU | ✅ | gReLU | bio.tools |

### footprinting: 7/7

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| TOBIAS | ✅ | TOBIAS | bio.tools |
| HINT-ATAC | ✅ | HINT-ATAC | curated seed |
| PIQ | ✅ | PIQ | curated seed |
| Wellington | ✅ | Wellington / pyDNase | curated seed |
| CENTIPEDE | ✅ | CENTIPEDE | curated seed |
| msCentipede | ✅ | msCentipede | bio.tools |
| TFBSFootprinter | ✅ | TFBSFootprinter | curated seed |

### peak calling and annotation: 9/9

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| MACS | ✅ | MACS | bio.tools |
| SEACR | ✅ | SEACR | bio.tools |
| Genrich | ✅ | Genrich | curated seed |
| GoPeaks | ✅ | GoPeaks | bio.tools |
| SICER | ✅ | SICER | bio.tools |
| ChIPseeker | ✅ | ChIPseeker | bio.tools |
| GREAT | ✅ | GREAT | bio.tools |
| LOLA | ✅ | LOLA | curated seed |
| BART | ✅ | BART | bio.tools |

### ChIP and ATAC resources: 5/5

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| GTRD | ✅ | GTRD | bio.tools |
| ReMap | ✅ | ReMap | bio.tools |
| ChIP-Atlas | ✅ | ChIP-Atlas | bio.tools |
| Cistrome | ✅ | Cistrome | bio.tools |
| ENCODE | ✅ | ENCODE DCC | bio.tools |

### gene regulatory networks: 9/9

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| SCENIC | ✅ | SCENIC | bio.tools |
| pySCENIC | ✅ | pySCENIC | curated seed |
| SCENIC+ | ✅ | SCENIC | bio.tools |
| RcisTarget | ✅ | RcisTarget | bio.tools |
| GENIE3 | ✅ | GENIE3 | bio.tools |
| ARACNe | ✅ | ARACNE | bio.tools |
| chromVAR | ✅ | chromVAR | bio.tools |
| iRegulon | ✅ | iRegulon | curated seed |
| i-cisTarget | ✅ | i-cisTarget | curated seed |

### regulatory variants: 8/8

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| motifbreakR | ✅ | motifbreakR | bio.tools |
| SNP2TFBS | ✅ | SNP2TFBS | bio.tools |
| atSNP | ✅ | atSNP | bio.tools |
| RegulomeDB | ✅ | RegulomeDB | curated seed |
| HaploReg | ✅ | HaploReg | bio.tools |
| GWAVA | ✅ | GWAVA | curated seed |
| FunSeq2 | ✅ | FunSeq2 | curated seed |
| FABIAN-variant | ✅ | FABIAN-variant | bio.tools |

### motif comparison and visualisation: 3/8

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| Tomtom | ❌ |  | not found |
| STAMP | ✅ | STAMP | bio.tools |
| MoSBAT | ❌ |  | not found |
| matrix-clustering | ✅ | matrix-clustering | bio.tools |
| universalmotif | ❌ |  | not found |
| ggseqlogo | ❌ |  | not found |
| Logolas | ❌ |  | not found |
| seqLogo | ✅ | seqLogo | bio.tools |

### nucleosome and chromatin state: 5/8

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| ChromHMM | ✅ | ChromHMM | bio.tools |
| Segway | ✅ | Segway | bio.tools |
| NucleoATAC | ✅ | NucleoATAC | bio.tools |
| DANPOS | ❌ |  | not found |
| iNPS | ❌ |  | not found |
| NucTools | ❌ |  | not found |
| nucleR | ✅ | nucleR | curated seed |
| NuPoP | ✅ | NuPoP | bio.tools |

### single-cell regulatory genomics: 9/10

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| Signac | ✅ | Signac | bio.tools |
| ArchR | ✅ | ArchR | bio.tools |
| SnapATAC | ✅ | SnapATAC | bio.tools |
| cisTopic | ✅ | cisTopic | bio.tools |
| scBasset | ✅ | scBasset | bio.tools |
| MAESTRO | ❌ |  | not found |
| Cicero | ✅ | Cicero | curated seed |
| chromVAR | ✅ | chromVAR | bio.tools |
| scATAC-pro | ✅ | scATAC-pro | bio.tools |
| PeakVI | ✅ | PeakVI | curated seed |

### harder motif discovery: 4/8

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| MEME-ChIP | ❌ |  | not found |
| Weeder | ✅ | Weeder | bio.tools |
| Improbizer | ❌ |  | not found |
| Amadeus | ❌ |  | not found |
| CisFinder | ❌ |  | not found |
| ProSampler | ✅ | ProSampler | bio.tools |
| GADEM | ✅ | GADEM | bio.tools |
| XXmotif | ✅ | XXmotif | bio.tools |

### harder peak calling: 8/12

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| MACS | ✅ | MACS | bio.tools |
| SICER | ✅ | SICER | bio.tools |
| HMMRATAC | ❌ |  | not found |
| SEACR | ✅ | SEACR | bio.tools |
| LanceOtron | ✅ | LanceOtron | bio.tools |
| THOR | ❌ |  | not found |
| PePr | ✅ | PePr | bio.tools |
| csaw | ✅ | csaw | bio.tools |
| MSPC | ✅ | MSPC | bio.tools |
| JAMM | ✅ | JAMM | bio.tools |
| Ritornello | ❌ |  | not found |
| BCP | ❌ |  | not found |

### harder footprinting: 2/6

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| Wellington | ✅ | Wellington-bootstrap | curated seed |
| BaGFoot | ❌ |  | not found |
| DNase2TF | ❌ |  | not found |
| seqOutBias | ❌ |  | not found |
| Romulus | ❌ |  | not found |
| msCentipede | ✅ | msCentipede | bio.tools |

### harder gene regulatory networks: 2/8

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| GRNBoost2 | ✅ | Arboreto | bio.tools |
| CLR | ❌ |  | not found |
| SCODE | ❌ |  | not found |
| PIDC | ❌ |  | not found |
| CellOracle | ❌ |  | not found |
| Pando | ❌ |  | not found |
| FigR | ❌ |  | not found |
| Dictys | ✅ | Dictys | curated seed |

### harder regulatory variants: 7/8

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| deltaSVM | ❌ |  | not found |
| motifbreakR | ✅ | motifbreakR | bio.tools |
| SNP2TFBS | ✅ | SNP2TFBS | bio.tools |
| GWAVA | ✅ | GWAVA | curated seed |
| FunSeq2 | ✅ | FunSeq2 | curated seed |
| RegulomeDB | ✅ | RegulomeDB | curated seed |
| Sasquatch | ✅ | Sasquatch | curated seed |
| GERV | ✅ | GERV | curated seed |

### harder peak annotation: 3/5

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| rGREAT | ❌ |  | not found |
| annotatr | ✅ | annotatr | bio.tools |
| PAVIS | ❌ |  | not found |
| LOLA | ✅ | LOLA | curated seed |
| DiffBind | ✅ | DiffBind | bio.tools |

### harder ChIP and ATAC resources: 5/6

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| Cistrome DB | ✅ | Cistrome | bio.tools |
| SEdb | ✅ | SEdb 2.0 | bio.tools |
| dbSUPER | ❌ |  | not found |
| ChIPBase | ✅ | ChIPBase | bio.tools |
| CistromeMap | ✅ | CistromeMap | curated seed |
| hmChIP | ✅ | hmChIP | curated seed |

### DNA methylation: 5/14

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| Bismark | ✅ | Bismark | bio.tools |
| methylKit | ❌ |  | not found |
| DSS | ❌ |  | not found |
| BS-Seeker2 | ✅ | BS Seeker | bio.tools |
| MOABS | ❌ |  | not found |
| metilene | ❌ |  | not found |
| DMRcate | ❌ |  | not found |
| minfi | ❌ |  | not found |
| ChAMP | ❌ |  | not found |
| MethylDackel | ✅ | MethylDackel | bio.tools |
| RnBeads | ✅ | RnBeads | bio.tools |
| SeSAMe | ❌ |  | not found |
| MethylSeekR | ✅ | MethylSeekR | bio.tools |
| methylpy | ❌ |  | not found |

### 3D genome and chromatin interactions: 4/16

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| Juicer | ❌ |  | not found |
| HiC-Pro | ❌ |  | not found |
| cooler | ❌ |  | not found |
| cooltools | ✅ | cooltools | bio.tools |
| FAN-C | ❌ |  | not found |
| HiCExplorer | ❌ |  | not found |
| TADbit | ❌ |  | not found |
| HiCCUPS | ❌ |  | not found |
| Arrowhead | ❌ |  | not found |
| mustache | ✅ | Mustache | bio.tools |
| Peakachu | ✅ | Peakachu | bio.tools |
| FitHiC | ❌ |  | not found |
| HiCRep | ❌ |  | not found |
| CHESS | ❌ |  | not found |
| coolpup.py | ❌ |  | not found |
| MoDLE | ✅ | MoDLE | bio.tools |

### histone modifications: 3/8

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| ChromHMM | ✅ | ChromHMM | bio.tools |
| Segway | ✅ | Segway | bio.tools |
| ROSE | ❌ |  | not found |
| dbSUPER | ❌ |  | not found |
| SEdb | ✅ | SEdb 2.0 | bio.tools |
| epilogos | ❌ |  | not found |
| chromswitch | ❌ |  | not found |
| EpiCSeq | ❌ |  | not found |

### reporter assays: 3/6

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| MPRAnalyze | ✅ | MPRAnalyze | bio.tools |
| mpralm | ❌ |  | not found |
| MPRAflow | ❌ |  | not found |
| starrpeaker | ✅ | STARRPeaker | bio.tools |
| CRADLE | ❌ |  | not found |
| BasicStarrSeq | ✅ | BasicSTARRseq | bio.tools |

### molecular QTL: 1/9

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| Matrix eQTL | ❌ |  | not found |
| FastQTL | ❌ |  | not found |
| QTLtools | ❌ |  | not found |
| tensorQTL | ❌ |  | not found |
| RASQUAL | ❌ |  | not found |
| mashr | ❌ |  | not found |
| coloc | ❌ |  | not found |
| SuSiE | ❌ |  | not found |
| QTLbase | ✅ | QTLbase | bio.tools |
