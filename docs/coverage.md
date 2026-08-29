# Coverage audit

Generated 2026-08-29 by `make audit`, against [`curation/benchmark.yaml`](../curation/benchmark.yaml).

The benchmark is a hand-written list of resources the field treats as standard. It is not a ranking and not exhaustive. It exists so that "did the pipeline find the obvious things?" is a measurement rather than an impression.

**171 of 221 benchmark tools present (77%).** Catalog size: 2184 tools.

## Misses

Each of these is a bug, and the diagnosis says which kind. *Never harvested* means no query reaches the record, so widen `QUERY_TOPICS` or `QUERY_FREETEXT`. *Rejected* means the selection rules in `pipeline/config.py` are too strict. *Absent from bio.tools* means it belongs in `curation/seeds.yaml`.

| Group | Tool | Diagnosis |
| --- | --- | --- |
| motif comparison and visualisation | Tomtom | absent from bio.tools; add to `seeds.yaml` |
| motif comparison and visualisation | MoSBAT | absent from bio.tools; add to `seeds.yaml` |
| motif comparison and visualisation | universalmotif | absent from bio.tools; add to `seeds.yaml` |
| nucleosome and chromatin state | iNPS | a bio.tools record is *named* `inps` but was never harvested. **Open it before acting**: the match is on name alone, and roughly a third of these are a different tool. If it is the right one, add it to `SEED_BIOTOOLS_IDS`; if not, it belongs in `seeds.yaml` |
| nucleosome and chromatin state | NucTools | absent from bio.tools; add to `seeds.yaml` |
| single-cell regulatory genomics | MAESTRO | a bio.tools record is *named* `maestro` but was never harvested. **Open it before acting**: the match is on name alone, and roughly a third of these are a different tool. If it is the right one, add it to `SEED_BIOTOOLS_IDS`; if not, it belongs in `seeds.yaml` |
| harder motif discovery | MEME-ChIP | absent from bio.tools; add to `seeds.yaml` |
| harder motif discovery | Improbizer | absent from bio.tools; add to `seeds.yaml` |
| harder motif discovery | Amadeus | absent from bio.tools; add to `seeds.yaml` |
| harder motif discovery | CisFinder | absent from bio.tools; add to `seeds.yaml` |
| harder peak calling | HMMRATAC | absent from bio.tools; add to `seeds.yaml` |
| harder peak calling | THOR | a bio.tools record is *named* `Thor` but was never harvested. **Open it before acting**: the match is on name alone, and roughly a third of these are a different tool. If it is the right one, add it to `SEED_BIOTOOLS_IDS`; if not, it belongs in `seeds.yaml` |
| harder peak calling | BCP | absent from bio.tools; add to `seeds.yaml` |
| harder footprinting | BaGFoot | absent from bio.tools; add to `seeds.yaml` |
| harder footprinting | DNase2TF | absent from bio.tools; add to `seeds.yaml` |
| harder footprinting | seqOutBias | absent from bio.tools; add to `seeds.yaml` |
| harder gene regulatory networks | CLR | absent from bio.tools; add to `seeds.yaml` |
| harder gene regulatory networks | SCODE | absent from bio.tools; add to `seeds.yaml` |
| harder gene regulatory networks | PIDC | absent from bio.tools; add to `seeds.yaml` |
| harder gene regulatory networks | CellOracle | absent from bio.tools; add to `seeds.yaml` |
| harder gene regulatory networks | Pando | absent from bio.tools; add to `seeds.yaml` |
| harder gene regulatory networks | FigR | absent from bio.tools; add to `seeds.yaml` |
| harder regulatory variants | deltaSVM | absent from bio.tools; add to `seeds.yaml` |
| harder peak annotation | PAVIS | absent from bio.tools; add to `seeds.yaml` |
| DNA methylation | DSS | a bio.tools record is *named* `dss` but was never harvested. **Open it before acting**: the match is on name alone, and roughly a third of these are a different tool. If it is the right one, add it to `SEED_BIOTOOLS_IDS`; if not, it belongs in `seeds.yaml` |
| DNA methylation | MOABS | absent from bio.tools; add to `seeds.yaml` |
| DNA methylation | metilene | absent from bio.tools; add to `seeds.yaml` |
| DNA methylation | minfi | a bio.tools record is *named* `minfi` but was never harvested. **Open it before acting**: the match is on name alone, and roughly a third of these are a different tool. If it is the right one, add it to `SEED_BIOTOOLS_IDS`; if not, it belongs in `seeds.yaml` |
| DNA methylation | ChAMP | harvested as `champ` but not selected; check `select_domain.py` |
| DNA methylation | methylpy | absent from bio.tools; add to `seeds.yaml` |
| 3D genome and chromatin interactions | Juicer | a bio.tools record is *named* `juicer` but was never harvested. **Open it before acting**: the match is on name alone, and roughly a third of these are a different tool. If it is the right one, add it to `SEED_BIOTOOLS_IDS`; if not, it belongs in `seeds.yaml` |
| 3D genome and chromatin interactions | HiC-Pro | a bio.tools record is *named* `hic-pro` but was never harvested. **Open it before acting**: the match is on name alone, and roughly a third of these are a different tool. If it is the right one, add it to `SEED_BIOTOOLS_IDS`; if not, it belongs in `seeds.yaml` |
| 3D genome and chromatin interactions | cooler | absent from bio.tools; add to `seeds.yaml` |
| 3D genome and chromatin interactions | TADbit | harvested as `tadbit`, then rejected (no-match); selection rule too strict |
| 3D genome and chromatin interactions | HiCCUPS | absent from bio.tools; add to `seeds.yaml` |
| 3D genome and chromatin interactions | Arrowhead | absent from bio.tools; add to `seeds.yaml` |
| 3D genome and chromatin interactions | HiCRep | a bio.tools record is *named* `hicrep` but was never harvested. **Open it before acting**: the match is on name alone, and roughly a third of these are a different tool. If it is the right one, add it to `SEED_BIOTOOLS_IDS`; if not, it belongs in `seeds.yaml` |
| 3D genome and chromatin interactions | CHESS | absent from bio.tools; add to `seeds.yaml` |
| histone modifications | ROSE | absent from bio.tools; add to `seeds.yaml` |
| histone modifications | epilogos | absent from bio.tools; add to `seeds.yaml` |
| histone modifications | chromswitch | a bio.tools record is *named* `chromswitch` but was never harvested. **Open it before acting**: the match is on name alone, and roughly a third of these are a different tool. If it is the right one, add it to `SEED_BIOTOOLS_IDS`; if not, it belongs in `seeds.yaml` |
| histone modifications | EpiCSeq | absent from bio.tools; add to `seeds.yaml` |
| reporter assays | mpralm | absent from bio.tools; add to `seeds.yaml` |
| reporter assays | MPRAflow | absent from bio.tools; add to `seeds.yaml` |
| reporter assays | CRADLE | absent from bio.tools; add to `seeds.yaml` |
| molecular QTL | Matrix eQTL | a bio.tools record is *named* `matrix_eqtl` but was never harvested. **Open it before acting**: the match is on name alone, and roughly a third of these are a different tool. If it is the right one, add it to `SEED_BIOTOOLS_IDS`; if not, it belongs in `seeds.yaml` |
| molecular QTL | FastQTL | absent from bio.tools; add to `seeds.yaml` |
| molecular QTL | tensorQTL | absent from bio.tools; add to `seeds.yaml` |
| molecular QTL | mashr | absent from bio.tools; add to `seeds.yaml` |
| molecular QTL | SuSiE | absent from bio.tools; add to `seeds.yaml` |

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
| TFBSFootprinter | ✅ | TFBSFootprinter | bio.tools |

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

### motif comparison and visualisation: 5/8

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| Tomtom | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| STAMP | ✅ | STAMP | bio.tools |
| MoSBAT | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| matrix-clustering | ✅ | matrix-clustering | bio.tools |
| universalmotif | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| ggseqlogo | ✅ | ggseqlogo | bio.tools |
| Logolas | ✅ | Logolas | bio.tools |
| seqLogo | ✅ | seqLogo | bio.tools |

### nucleosome and chromatin state: 6/8

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| ChromHMM | ✅ | ChromHMM | bio.tools |
| Segway | ✅ | Segway | bio.tools |
| NucleoATAC | ✅ | NucleoATAC | bio.tools |
| DANPOS | ✅ | DANPOS | bio.tools |
| iNPS | ❌ |  | a bio.tools record is *named* `inps` but was never harvested. **Open it before acting**: the match is on name alone, and roughly a third of these are a different tool. If it is the right one, add it to `SEED_BIOTOOLS_IDS`; if not, it belongs in `seeds.yaml` |
| NucTools | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
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
| MAESTRO | ❌ |  | a bio.tools record is *named* `maestro` but was never harvested. **Open it before acting**: the match is on name alone, and roughly a third of these are a different tool. If it is the right one, add it to `SEED_BIOTOOLS_IDS`; if not, it belongs in `seeds.yaml` |
| Cicero | ✅ | Cicero | curated seed |
| chromVAR | ✅ | chromVAR | bio.tools |
| scATAC-pro | ✅ | scATAC-pro | bio.tools |
| PeakVI | ✅ | PeakVI | curated seed |

### harder motif discovery: 4/8

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| MEME-ChIP | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| Weeder | ✅ | Weeder | bio.tools |
| Improbizer | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| Amadeus | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| CisFinder | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| ProSampler | ✅ | ProSampler | bio.tools |
| GADEM | ✅ | GADEM | bio.tools |
| XXmotif | ✅ | XXmotif | bio.tools |

### harder peak calling: 9/12

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| MACS | ✅ | MACS | bio.tools |
| SICER | ✅ | SICER | bio.tools |
| HMMRATAC | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| SEACR | ✅ | SEACR | bio.tools |
| LanceOtron | ✅ | LanceOtron | bio.tools |
| THOR | ❌ |  | a bio.tools record is *named* `Thor` but was never harvested. **Open it before acting**: the match is on name alone, and roughly a third of these are a different tool. If it is the right one, add it to `SEED_BIOTOOLS_IDS`; if not, it belongs in `seeds.yaml` |
| PePr | ✅ | PePr | bio.tools |
| csaw | ✅ | csaw | bio.tools |
| MSPC | ✅ | MSPC | bio.tools |
| JAMM | ✅ | JAMM | bio.tools |
| Ritornello | ✅ | Ritornello | curated seed |
| BCP | ❌ |  | absent from bio.tools; add to `seeds.yaml` |

### harder footprinting: 3/6

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| Wellington | ✅ | Wellington-bootstrap | curated seed |
| BaGFoot | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| DNase2TF | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| seqOutBias | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| Romulus | ✅ | Romulus | curated seed |
| msCentipede | ✅ | msCentipede | bio.tools |

### harder gene regulatory networks: 2/8

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| GRNBoost2 | ✅ | Arboreto | bio.tools |
| CLR | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| SCODE | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| PIDC | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| CellOracle | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| Pando | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| FigR | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| Dictys | ✅ | Dictys | curated seed |

### harder regulatory variants: 7/8

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| deltaSVM | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| motifbreakR | ✅ | motifbreakR | bio.tools |
| SNP2TFBS | ✅ | SNP2TFBS | bio.tools |
| GWAVA | ✅ | GWAVA | curated seed |
| FunSeq2 | ✅ | FunSeq2 | curated seed |
| RegulomeDB | ✅ | RegulomeDB | curated seed |
| Sasquatch | ✅ | Sasquatch | curated seed |
| GERV | ✅ | GERV | curated seed |

### harder peak annotation: 4/5

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| rGREAT | ✅ | rGREAT | bio.tools |
| annotatr | ✅ | annotatr | bio.tools |
| PAVIS | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| LOLA | ✅ | LOLA | curated seed |
| DiffBind | ✅ | DiffBind | bio.tools |

### harder ChIP and ATAC resources: 6/6

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| Cistrome DB | ✅ | Cistrome | bio.tools |
| SEdb | ✅ | SEdb 2.0 | bio.tools |
| dbSUPER | ✅ | dbSUPER | bio.tools |
| ChIPBase | ✅ | ChIPBase | bio.tools |
| CistromeMap | ✅ | CistromeMap | curated seed |
| hmChIP | ✅ | hmChIP | curated seed |

### DNA methylation: 8/14

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| Bismark | ✅ | Bismark | bio.tools |
| methylKit | ✅ | methylKit | bio.tools |
| DSS | ❌ |  | a bio.tools record is *named* `dss` but was never harvested. **Open it before acting**: the match is on name alone, and roughly a third of these are a different tool. If it is the right one, add it to `SEED_BIOTOOLS_IDS`; if not, it belongs in `seeds.yaml` |
| BS-Seeker2 | ✅ | BS-Seeker2 | bio.tools |
| MOABS | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| metilene | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| DMRcate | ✅ | DMRcate | bio.tools |
| minfi | ❌ |  | a bio.tools record is *named* `minfi` but was never harvested. **Open it before acting**: the match is on name alone, and roughly a third of these are a different tool. If it is the right one, add it to `SEED_BIOTOOLS_IDS`; if not, it belongs in `seeds.yaml` |
| ChAMP | ❌ |  | harvested as `champ` but not selected; check `select_domain.py` |
| MethylDackel | ✅ | MethylDackel | bio.tools |
| RnBeads | ✅ | RnBeads | bio.tools |
| SeSAMe | ✅ | SeSAMe | bio.tools |
| MethylSeekR | ✅ | MethylSeekR | bio.tools |
| methylpy | ❌ |  | absent from bio.tools; add to `seeds.yaml` |

### 3D genome and chromatin interactions: 8/16

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| Juicer | ❌ |  | a bio.tools record is *named* `juicer` but was never harvested. **Open it before acting**: the match is on name alone, and roughly a third of these are a different tool. If it is the right one, add it to `SEED_BIOTOOLS_IDS`; if not, it belongs in `seeds.yaml` |
| HiC-Pro | ❌ |  | a bio.tools record is *named* `hic-pro` but was never harvested. **Open it before acting**: the match is on name alone, and roughly a third of these are a different tool. If it is the right one, add it to `SEED_BIOTOOLS_IDS`; if not, it belongs in `seeds.yaml` |
| cooler | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| cooltools | ✅ | cooltools | bio.tools |
| FAN-C | ✅ | FAN-C | bio.tools |
| HiCExplorer | ✅ | HiCExplorer | bio.tools |
| TADbit | ❌ |  | harvested as `tadbit`, then rejected (no-match); selection rule too strict |
| HiCCUPS | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| Arrowhead | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| mustache | ✅ | Mustache | bio.tools |
| Peakachu | ✅ | Peakachu | bio.tools |
| FitHiC | ✅ | FitHiC | bio.tools |
| HiCRep | ❌ |  | a bio.tools record is *named* `hicrep` but was never harvested. **Open it before acting**: the match is on name alone, and roughly a third of these are a different tool. If it is the right one, add it to `SEED_BIOTOOLS_IDS`; if not, it belongs in `seeds.yaml` |
| CHESS | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| coolpup.py | ✅ | coolpup.py | bio.tools |
| MoDLE | ✅ | MoDLE | bio.tools |

### histone modifications: 4/8

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| ChromHMM | ✅ | ChromHMM | bio.tools |
| Segway | ✅ | Segway | bio.tools |
| ROSE | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| dbSUPER | ✅ | dbSUPER | bio.tools |
| SEdb | ✅ | SEdb 2.0 | bio.tools |
| epilogos | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| chromswitch | ❌ |  | a bio.tools record is *named* `chromswitch` but was never harvested. **Open it before acting**: the match is on name alone, and roughly a third of these are a different tool. If it is the right one, add it to `SEED_BIOTOOLS_IDS`; if not, it belongs in `seeds.yaml` |
| EpiCSeq | ❌ |  | absent from bio.tools; add to `seeds.yaml` |

### reporter assays: 3/6

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| MPRAnalyze | ✅ | MPRAnalyze | bio.tools |
| mpralm | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| MPRAflow | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| starrpeaker | ✅ | STARRPeaker | bio.tools |
| CRADLE | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| BasicStarrSeq | ✅ | BasicSTARRseq | bio.tools |

### molecular QTL: 4/9

| Benchmark tool | Present | Catalog entry | Source / diagnosis |
| --- | :---: | --- | --- |
| Matrix eQTL | ❌ |  | a bio.tools record is *named* `matrix_eqtl` but was never harvested. **Open it before acting**: the match is on name alone, and roughly a third of these are a different tool. If it is the right one, add it to `SEED_BIOTOOLS_IDS`; if not, it belongs in `seeds.yaml` |
| FastQTL | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| QTLtools | ✅ | QTLtools | bio.tools |
| tensorQTL | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| RASQUAL | ✅ | RASQUAL | bio.tools |
| mashr | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| coloc | ✅ | COLOCdb | bio.tools |
| SuSiE | ❌ |  | absent from bio.tools; add to `seeds.yaml` |
| QTLbase | ✅ | QTLbase | bio.tools |
