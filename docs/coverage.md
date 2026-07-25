# Coverage audit

Generated 2026-07-26 by `make audit`, against [`curation/benchmark.yaml`](../curation/benchmark.yaml).

The benchmark is a hand-written list of resources the field treats as standard. It is not a ranking and not exhaustive. It exists so that "did the pipeline find the obvious things?" is a measurement rather than an impression.

**89 of 89 benchmark tools present (100%).** Catalog size: 1869 tools.

No misses.

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
| MAST | ✅ | MAST | bio.tools |
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
