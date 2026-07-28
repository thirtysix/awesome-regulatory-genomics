# Registry discovery

Generated 2026-07-28 by `make discover`.

Tools found in registries that bio.tools does not index, filtered by the same rules the bio.tools records face (`select_domain.classify`). **Nothing here is in the catalog.** Promote an entry by adding it to [`curation/seeds.yaml`](../curation/seeds.yaml); this file is regenerated and is not itself an input.

| Source | Scanned | In domain | Not yet in the catalog |
| --- | ---: | ---: | ---: |
| bioconductor | 2418 | 234 | 84 |
| galaxy | 7772 | 59 | 31 |

178 further in-domain entries are already in the catalog under the same name. That overlap is the useful control: it is evidence the filter behaves the same way on registry text as on bio.tools text, rather than admitting a different population.

## Candidates

`tier` is `core` where a strong domain phrase settled it on its own, and `extended` where a registry category corroborated a weaker signal.

| Tool | Source | Tier | Why it matched | Summary |
| --- | --- | --- | --- | --- |
| [ADImpute](https://bioconductor.org/packages/ADImpute/) | bioconductor | core | text:\bgene regulatory network\|\bregulato · GeneExpression, Network, Preprocessing | Adaptive Dropout Imputer (ADImpute) |
| [AMARETTO](https://bioconductor.org/packages/AMARETTO/) | bioconductor | core | text:\bgene regulatory network\|\bregulato · StatisticalMethod, DifferentialMethylation, GeneRegulation | Regulatory Network Inference and Driver Gene Evaluation using Integrative Multi-Omics Analysis and Penalized Regression |
| [annoLinker](https://bioconductor.org/packages/annoLinker/) | bioconductor | core | text:\bchromatin (accessibilit\|state\|loop · Network, Annotation, Visualization | Annotating genomic regions through chromatin interaction links |
| [atacInferCnv](https://bioconductor.org/packages/atacInferCnv/) | bioconductor | core | text:\bsc(ATAC\|-ATAC)\|\bsingle[- ](cell\|n · Epigenetics, Sequencing, CopyNumberVariation | Call CNV from single cell ATAC-seq data based on InferCNV adaptation |
| [bacon](https://bioconductor.org/packages/bacon/) | bioconductor | core | text:\bepigenom(e\|ic)s?\b · ImmunoOncology, StatisticalMethod, Bayesian | Controlling bias and inflation in association studies using the empirical null distribution |
| [cageminer](https://bioconductor.org/packages/cageminer/) | bioconductor | core | text:\btranscription[- ]factor · Software, SNP, FunctionalPrediction | Candidate Gene Miner |
| [Chicago](https://bioconductor.org/packages/Chicago/) | bioconductor | extended | text+topic:\bHi-?C\b\|\bChIA-?PET\b\|\bHiChIP · Epigenetics, HiC, Sequencing | CHiCAGO: Capture Hi-C Analysis of Genomic Organization |
| [coMethDMR](https://bioconductor.org/packages/coMethDMR/) | bioconductor | core | text:\bepigenom(e\|ic)s?\b · DNAMethylation, Epigenetics, MethylationArray | Accurate identification of co-methylated and differentially methylated regions in epigenome-wide association studies |
| [damidBind](https://bioconductor.org/packages/damidBind/) | bioconductor | core | text:\bchromatin (accessibilit\|state\|loop · DifferentialExpression, GeneExpression, Transcription | Differential Binding and Expression Analysis for DamID-seq Data |
| [Damsel](https://bioconductor.org/packages/Damsel/) | bioconductor | core | text:\bmotif (discovery\|enrichment\|scan\|s · DifferentialMethylation, PeakDetection, GenePrediction | Damsel: an end to end analysis of DamID |
| [decoupleR](https://bioconductor.org/packages/decoupleR/) | bioconductor | core | text:\btranscription[- ]factor · DifferentialExpression, FunctionalGenomics, GeneExpression | decoupleR: Ensemble of computational methods to infer biological activities from omics data |
| [DeMAND](https://bioconductor.org/packages/DeMAND/) | bioconductor | core | text:\bgene regulatory network\|\bregulato · SystemsBiology, NetworkEnrichment, GeneExpression | DeMAND |
| [derfinder](https://bioconductor.org/packages/derfinder/) | bioconductor | core | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b · DifferentialExpression, Sequencing, RNASeq | Annotation-agnostic differential expression analysis of RNA-seq data at base-pair resolution via the DER Finder approach |
| [dmGsea](https://bioconductor.org/packages/dmGsea/) | bioconductor | core | text:\bepigenom(e\|ic)s?\b · GeneSetEnrichment, Pathways, DNAMethylation | Efficient Gene Set Enrichment Analysis for DNA Methylation Data |
| [dominoSignal](https://bioconductor.org/packages/dominoSignal/) | bioconductor | core | text:\btranscription[- ]factor · SystemsBiology, SingleCell, Transcriptomics | Cell Communication Analysis for Single Cell RNA Sequencing |
| [eisaR](https://bioconductor.org/packages/eisaR/) | bioconductor | extended | text+topic:\btranscription(al)? regulat · Transcription, GeneExpression, GeneRegulation | Exon-Intron Split Analysis (EISA) in R |
| [epidecodeR](https://bioconductor.org/packages/epidecodeR/) | bioconductor | core | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b · DifferentialExpression, GeneRegulation, HistoneModification | epidecodeR: a functional exploration tool for epigenetic and epitranscriptomic regulation |
| [EpiDISH](https://bioconductor.org/packages/EpiDISH/) | bioconductor | core | text:\bepigenom(e\|ic)s?\b · DNAMethylation, MethylationArray, Epigenetics | Epigenetic Dissection of Intra-Sample-Heterogeneity |
| [EpiMix](https://bioconductor.org/packages/EpiMix/) | bioconductor | core | text:\bcis-regulatory\|\bregulatory elemen · Software, Epigenetics, Preprocessing | EpiMix: an integrative tool for the population-level analysis of DNA methylation |
| [EpipwR](https://bioconductor.org/packages/EpipwR/) | bioconductor | core | text:\bepigenom(e\|ic)s?\b · Epigenetics, ExperimentalDesign | Efficient Power Analysis for EWAS with Continuous or Binary Outcomes |
| [epiregulon.extra](https://bioconductor.org/packages/epiregulon.extra/) | bioconductor | core | text:\bcis-regulatory\|\bregulatory elemen · GeneRegulation, Network, GeneExpression · may package epiregulon | Companion package to epiregulon with additional plotting, differential and graph functions |
| [epiSeeker](https://bioconductor.org/packages/epiSeeker/) | bioconductor | core | text:\bmotif (discovery\|enrichment\|scan\|s · Annotation, ChIPSeq, Software | epiSeeker: an R package for Annotation, Comparison and Visualization of multi-omics epigenetic data |
| [epistack](https://bioconductor.org/packages/epistack/) | bioconductor | core | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b · RNASeq, Preprocessing, ChIPSeq | Heatmaps of Stack Profiles from Epigenetic Signals |
| [GDCRNATools](https://bioconductor.org/packages/GDCRNATools/) | bioconductor | core | text:\bgene regulatory network\|\bregulato · ImmunoOncology, GeneExpression, DifferentialExpression | GDCRNATools: an R/Bioconductor package for integrative analysis of lncRNA, mRNA, and miRNA data in GDC |
| [GenomicDistributions](https://bioconductor.org/packages/GenomicDistributions/) | bioconductor | core | text:\btranscription start site\|\bCAGE\b · Software, GenomeAnnotation, GenomeAssembly | GenomicDistributions: fast analysis of genomic intervals with Bioconductor |
| [GenomicInteractionNodes](https://bioconductor.org/packages/GenomicInteractionNodes/) | bioconductor | core | text:\bHiChIP\b\|\bChIA-?PET\b\|\bCapture-? · HiC, Sequencing, Software | A R/Bioconductor package to detect the interaction nodes from HiC/HiChIP/HiCAR data |
| [GenomicInteractions](https://bioconductor.org/packages/GenomicInteractions/) | bioconductor | core | text:\bHiChIP\b\|\bChIA-?PET\b\|\bCapture-? · Software, Infrastructure, DataImport | Utilities for handling genomic interaction data |
| [GenomicOZone](https://bioconductor.org/packages/GenomicOZone/) | bioconductor | core | text:\bepigenom(e\|ic)s?\b · Software, GeneExpression, Transcription | Delineate outstanding genomic zones of differential gene activity |
| [GenomicPlot](https://bioconductor.org/packages/GenomicPlot/) | bioconductor | core | text:\bpromoter\b\|\benhancer\b\|\bsuper-?e · AlternativeSplicing, ChIPSeq, Coverage | Plot profiles of next generation sequencing data in genomic features |
| [geomeTriD](https://bioconductor.org/packages/geomeTriD/) | bioconductor | core | text:\bchromatin (accessibilit\|state\|loop · Visualization | A R/Bioconductor package for interactive 3D plot of epigenetic data or single cell data |
| [ggmsa](https://bioconductor.org/packages/ggmsa/) | bioconductor | core | text:\bsequence logo\|\bsequence motifs?\b · Software, Visualization, Alignment | Plot Multiple Sequence Alignment using 'ggplot2' |
| [gVenn](https://bioconductor.org/packages/gVenn/) | bioconductor | core | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b · Software, Visualization, ChIPSeq | Proportional Venn and UpSet Diagrams for Gene Sets and Genomic Regions |
| [HicAggR](https://bioconductor.org/packages/HicAggR/) | bioconductor | core | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b · Software, HiC, DataImport | Set of 3D genomic interaction analysis tools |
| [HiCaptuRe](https://bioconductor.org/packages/HiCaptuRe/) | bioconductor | extended | text+topic:\bHi-?C\b\|\bChIA-?PET\b\|\bHiChIP · Epigenetics, HiC, Sequencing | HiCaptuRe: Manipulating and integrating Capture Hi-C data |
| [HiCcompare](https://bioconductor.org/packages/HiCcompare/) | bioconductor | core | text:\bchromatin (accessibilit\|state\|loop · Software, HiC, Sequencing | HiCcompare: Joint normalization and comparative analysis of multiple Hi-C datasets |
| [HiCDCPlus](https://bioconductor.org/packages/HiCDCPlus/) | bioconductor | core | text:\bHiChIP\b\|\bChIA-?PET\b\|\bCapture-? · HiC, DNA3DStructure, Software | Hi-C Direct Caller Plus |
| [HiCPotts](https://bioconductor.org/packages/HiCPotts/) | bioconductor | core | text:\bchromatin (accessibilit\|state\|loop · StatisticalMethod, FunctionalGenomics, GenomeAnnotation | HiCPotts: Hierarchical Modeling to Identify and Correct Genomic Biases in Hi-C |
| [hicVennDiagram](https://bioconductor.org/packages/hicVennDiagram/) | bioconductor | core | text:\bHiChIP\b\|\bChIA-?PET\b\|\bCapture-? · DNA3DStructure, HiC, Visualization | Venn Diagram for genomic interaction data |
| [HIREewas](https://bioconductor.org/packages/HIREewas/) | bioconductor | core | text:\bepigenom(e\|ic)s?\b · DNAMethylation, DifferentialMethylation, FeatureExtraction | Detection of cell-type-specific risk-CpG sites in epigenome-wide association studies |
| [HiSpaR](https://bioconductor.org/packages/HiSpaR/) | bioconductor | extended | text+topic:\bHi-?C\b\|\bChIA-?PET\b\|\bHiChIP · Software, Epigenetics, HiC | Hierarchical Inference of Spatial Positions from Hi-C Data |
| [InPAS](https://bioconductor.org/packages/InPAS/) | bioconductor | extended | text+topic:\btranscription(al)? regulat · Alternative Polyadenylation, Differential Polyadenylation Site Usage, RNA-seq | Identify Novel Alternative PolyAdenylation Sites (PAS) from RNA-seq data |
| [InteractionSet](https://bioconductor.org/packages/InteractionSet/) | bioconductor | core | text:\bHiChIP\b\|\bChIA-?PET\b\|\bCapture-? · Infrastructure, DataRepresentation, Software | Base Classes for Storing Genomic Interaction Data |
| [KinSwingR](https://bioconductor.org/packages/KinSwingR/) | bioconductor | core | text:\bposition (weight\|frequency\|specifi · Proteomics, SequenceMatching, Network | KinSwingR: network-based kinase activity prediction |
| [knowYourCG](https://bioconductor.org/packages/knowYourCG/) | bioconductor | core | text:\btranscription[- ]factor · Epigenetics, DNAMethylation, Sequencing | Functional analysis of DNA methylome datasets |
| [linkSet](https://bioconductor.org/packages/linkSet/) | bioconductor | core | text:\bpromoter\b\|\benhancer\b\|\bsuper-?e · Software, HiC, DataRepresentation | Base Classes for Storing Genomic Link Data |
| [MACSr](https://bioconductor.org/packages/MACSr/) | bioconductor | core | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b · Software, ChIPSeq, ATACSeq | MACS: Model-based Analysis for ChIP-Seq |
| [MEDIPS](https://bioconductor.org/packages/MEDIPS/) | bioconductor | core | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b · DNAMethylation, CpGIsland, DifferentialExpression | DNA IP-seq data analysis |
| [MetaboSignal](https://bioconductor.org/packages/MetaboSignal/) | bioconductor | core | text:\bgene regulatory network\|\bregulato · GraphAndNetwork, GeneSignaling, GeneTarget | MetaboSignal: a network-based approach to overlay and explore metabolic and signaling KEGG pathways |
| [metagene2](https://bioconductor.org/packages/metagene2/) | bioconductor | core | text:\bpromoter\b\|\benhancer\b\|\bsuper-?e · ChIPSeq, Genetics, MultipleComparison | A package to produce metagene plots |
| [metapod](https://bioconductor.org/packages/metapod/) | bioconductor | core | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b · MultipleComparison, DifferentialPeakCalling | Meta-Analyses on P-Values of Differential Analyses |
| [mistyR](https://bioconductor.org/packages/mistyR/) | bioconductor | core | text:\bfootprint · Software, BiomedicalInformatics, CellBiology | Multiview Intercellular SpaTial modeling framework |
| [mitch](https://bioconductor.org/packages/mitch/) | bioconductor | core | text:\bepigenom(e\|ic)s?\b · GeneExpression, GeneSetEnrichment, SingleCell | Multi-Contrast Gene Set Enrichment Analysis |
| [multiHiCcompare](https://bioconductor.org/packages/multiHiCcompare/) | bioconductor | core | text:\bchromatin (accessibilit\|state\|loop · Software, HiC, Sequencing | Normalize and detect differences between Hi-C datasets when replicates of each experimental condition are available |
| [MutationalPatterns](https://bioconductor.org/packages/MutationalPatterns/) | bioconductor | core | text:\bfootprint · Genetics, SomaticMutation | Comprehensive genome-wide analysis of mutational processes |
| [NoRCE](https://bioconductor.org/packages/NoRCE/) | bioconductor | core | text:\bHiChIP\b\|\bChIA-?PET\b\|\bCapture-? · BiologicalQuestion, DifferentialExpression, GenomeAnnotation | NoRCE: Noncoding RNA Sets Cis Annotation and Enrichment |
| [normalize450K](https://bioconductor.org/packages/normalize450K/) | bioconductor | core | text:\bepigenom(e\|ic)s?\b · Normalization, DNAMethylation, Microarray | Preprocessing of Illumina Infinium 450K data |
| [ORFik](https://bioconductor.org/packages/ORFik/) | bioconductor | core | text:\btranscription start site\|\bCAGE\b · ImmunoOncology, Software, Sequencing | Open Reading Frames in Genomics |
| [postNet](https://bioconductor.org/packages/postNet/) | bioconductor | extended | text+topic:\btranscription(al)? regulat · GeneExpression, GeneRegulation, Transcriptomics | Post-transcriptional network modeling |
| [qpgraph](https://bioconductor.org/packages/qpgraph/) | bioconductor | core | text:\bgene regulatory network\|\bregulato · Microarray, GeneExpression, Transcription | Estimation of Genetic and Molecular Regulatory Networks from High-Throughput Genomics Data |
| [r3Cseq](https://bioconductor.org/packages/r3Cseq/) | bioconductor | core | text:\bchromatin (accessibilit\|state\|loop · Preprocessing, Sequencing | Analysis of Chromosome Conformation Capture and Next-generation Sequencing (3C-seq) |
| [RCAS](https://bioconductor.org/packages/RCAS/) | bioconductor | core | text:\bpromoter\b\|\benhancer\b\|\bsuper-?e · Software, GeneTarget, MotifAnnotation | RNA Centric Annotation System |
| [recoup](https://bioconductor.org/packages/recoup/) | bioconductor | core | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b · ImmunoOncology, Software, GeneExpression | An R package for the creation of complex genomic profile plots |
| [REMP](https://bioconductor.org/packages/REMP/) | bioconductor | core | text:\bepigenom(e\|ic)s?\b · DNAMethylation, Microarray, MethylationArray | Repetitive Element Methylation Prediction |
| [RepViz](https://bioconductor.org/packages/RepViz/) | bioconductor | core | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b · WorkflowStep, Visualization, Sequencing | Replicate oriented Visualization of a genomic region |
| [rGenomeTracks](https://bioconductor.org/packages/rGenomeTracks/) | bioconductor | core | text:\bepigenom(e\|ic)s?\b · Software, HiC, Visualization | Integerated visualization of epigenomic data |
| [RiboDiPA](https://bioconductor.org/packages/RiboDiPA/) | bioconductor | core | text:\bfootprint · RiboSeq, GeneExpression, GeneRegulation | Differential pattern analysis for Ribo-seq data |
| [rifi](https://bioconductor.org/packages/rifi/) | bioconductor | core | text:\btranscription start site\|\bCAGE\b · RNASeq, DifferentialExpression, GeneRegulation | 'rifi' analyses data from rifampicin time series created by microarray or RNAseq |
| [Rsubread](https://bioconductor.org/packages/Rsubread/) | bioconductor | core | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b · Sequencing, Alignment, SequenceMatching | Mapping, quantification and variant analysis of sequencing data |
| [scDblFinder](https://bioconductor.org/packages/scDblFinder/) | bioconductor | core | text:\bsc(ATAC\|-ATAC)\|\bsingle[- ](cell\|n · Preprocessing, SingleCell, RNASeq | scDblFinder |
| [scHiCcompare](https://bioconductor.org/packages/scHiCcompare/) | bioconductor | core | text:\bchromatin (accessibilit\|state\|loop · Software, SingleCell, HiC | Differential Analysis of Single-cell Hi-C Data |
| [scMitoMut](https://bioconductor.org/packages/scMitoMut/) | bioconductor | core | text:\bsc(ATAC\|-ATAC)\|\bsingle[- ](cell\|n · Preprocessing, Sequencing, SingleCell | Single-cell Mitochondrial Mutation Analysis Tool |
| [scMultiSim](https://bioconductor.org/packages/scMultiSim/) | bioconductor | core | text:\bgene regulatory network\|\bregulato · SingleCell, Transcriptomics, GeneExpression | Simulation of Multi-Modality Single Cell Data Guided By Gene Regulatory Networks and Cell-Cell Interactions |
| [seq2pathway](https://bioconductor.org/packages/seq2pathway/) | bioconductor | core | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b · Software | a novel tool for functional gene-set (or termed as pathway) analysis of next-generation sequencing data |
| [Seqtometry](https://bioconductor.org/packages/Seqtometry/) | bioconductor | core | text:\bsc(ATAC\|-ATAC)\|\bsingle[- ](cell\|n · SingleCell, GeneSetEnrichment, GeneExpression | Signature scoring for single cell analysis |
| [simPIC](https://bioconductor.org/packages/simPIC/) | bioconductor | core | text:\bsc(ATAC\|-ATAC)\|\bsingle[- ](cell\|n · SingleCell, ATACSeq, Software | Flexible simulation of paired-insertion counts for single-cell ATAC-sequencing data |
| [SMITE](https://bioconductor.org/packages/SMITE/) | bioconductor | core | text:\bepigenom(e\|ic)s?\b · ImmunoOncology, DifferentialMethylation, DifferentialExpression | Significance-based Modules Integrating the Transcriptome and Epigenome |
| [SpectralTAD](https://bioconductor.org/packages/SpectralTAD/) | bioconductor | core | text:\bHiChIP\b\|\bChIA-?PET\b\|\bCapture-? · Software, HiC, Sequencing | SpectralTAD: Hierarchical TAD detection using spectral clustering |
| [SPICEY](https://bioconductor.org/packages/SPICEY/) | bioconductor | core | text:\bcis-regulatory\|\bregulatory elemen · Transcriptomics, Epigenetics, SingleCell | Calculates cell type specificity from single cell data |
| [SVP](https://bioconductor.org/packages/SVP/) | bioconductor | core | text:\btranscription[- ]factor · SingleCell, Software, Spatial | Predicting cell states and their variability in single-cell or spatial omics data |
| [TADCompare](https://bioconductor.org/packages/TADCompare/) | bioconductor | core | text:\bHiChIP\b\|\bChIA-?PET\b\|\bCapture-? · Software, HiC, Sequencing | TADCompare: Identification and characterization of differential TADs |
| [trackViewer](https://bioconductor.org/packages/trackViewer/) | bioconductor | core | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b · Visualization | A R/Bioconductor package with web interface for drawing elegant interactive tracks or lollipop plot to facilitate integrated analysis of multi-omics data |
| [tRanslatome](https://bioconductor.org/packages/tRanslatome/) | bioconductor | extended | text+topic:\btranscription(al)? regulat · CellBiology, GeneRegulation, Regulation | Comparison between multiple levels of gene expression |
| [UMI4Cats](https://bioconductor.org/packages/UMI4Cats/) | bioconductor | core | text:\bchromatin (accessibilit\|state\|loop · QualityControl, Preprocessing, Alignment | UMI4Cats: Processing, analysis and visualization of UMI-4C chromatin contact data |
| [wavClusteR](https://bioconductor.org/packages/wavClusteR/) | bioconductor | core | text:\bmotif (discovery\|enrichment\|scan\|s · ImmunoOncology, Sequencing, Technology | Sensitive and highly resolved identification of RNA-protein interaction sites in PAR-CLIP data |
| bdds | galaxy | core | text:\bfootprint | BDDS Platform and Tool Suite for DNA footprinting |
| cellranger_atac_galaxy | galaxy | core | text:\bsc(ATAC\|-ATAC)\|\bsingle[- ](cell\|n | Galaxy wrapper for Cellranger-ATAC to analyze scATAC-seq data |
| [chipseeker_annotator](https://yourdomain.com/chipseeker-docs) | galaxy | core | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b · may package ChIPseeker | ChIP-seq peak annotation using ChIPseeker R package |
| [chipseq_workflows](http://stemcellcommons.org/) | galaxy | core | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b · may package chipseq | ChIP-seq workflows annotated for use with Refinery Platform |
| codonlogo | galaxy | core | text:\bsequence logo\|\bsequence motifs?\b | Codon based sequence logo generator. |
| csem | galaxy | core | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | CSEM: Multi-read Allocation for ChIP-seq |
| ctcf_analysis | galaxy | core | text:\bHiChIP\b\|\bChIA-?PET\b\|\bCapture-? | A tool for identification of CTCF sites |
| [damidseq_findpeaks](https://github.com/owenjm/find_peaks) | galaxy | core | text:\bpeak[- ]call(er\|ing)?\b\|\bcalls? p | A simple FDR peak caller for DamID data |
| [dewseq](https://github.com/EMBL-Hentze-group/DEWSeq_analysis_helpers) | galaxy | core | text:\bpeak[- ]call(er\|ing)?\b\|\bcalls? p | DEWSeq is a sliding window based peak caller for eCLIP/iCLIP data |
| differential_expression_analysis_pipeline_for_rnaseq_data | galaxy | core | text:\bepigenom(e\|ic)s?\b | This pipeline has been founded by APLIBIO, and has been built by Yufei Luo, Marie-Agnes Dillies, Matthias Zytnicki, Delphine Steinbach (URGI, INRA Versailles an |
| dimont_motif_discovery | galaxy | core | text:\bmotif (discovery\|enrichment\|scan\|s · may package Dimont | A general approach for de-novo motif discovery from high-throughput data |
| fastaptamer_search | galaxy | core | text:\bmotif (discovery\|enrichment\|scan\|s | Degenerate nucleotide motif searching |
| [footprint](https://ohlerlab.mdc-berlin.de/software/Reproducible_footprinting_139/) | galaxy | core | text:\btranscription[- ]factor | Find transcription factor footprints |
| [hifive](http://github.com/bxlab/hifive) | galaxy | core | text:\bchromatin (accessibilit\|state\|loop | Contains tools for reading, normalizing, and plotting HiC and 5C chromatin interaction data |
| java_genomics_toolkit | galaxy | core | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | Wig math (avg/log/Z-score/etc), NGS processing (ChIP-seq, MNase-seq, FAIRE-seq, DNase-seq), and visualization (heatmaps, clustering) |
| [java_genomics_toolkit](https://tim.palpant.us/java-genomics-toolkit/) | galaxy | core | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | Wig math (avg/log/Z-score/etc), NGS processing (ChIP-seq, MNase-seq, FAIRE-seq, DNase-seq), and visualization (heatmaps, clustering) |
| macs14 | galaxy | core | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | Model-based Analysis of ChIP-Seq (macs 1.4) |
| macs2 | galaxy | core | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | Model-based Analysis of ChIP-Seq ( macs2 ).   **NOTE: This package requires Python 2.7.X and numpy (>=1.3) installed on all cluster nodes. |
| macs2 | galaxy | core | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | Model-based Analysis of ChIP-Seq (macs2) |
| meme | galaxy | core | text:\bmotif (discovery\|enrichment\|scan\|s | motif discovery |
| mtls_analysis | galaxy | core | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | A set of functions to analyze and compare multiple ChIP-seq experiments. |
| ncbi_epi_browse | galaxy | core | text:\bepigenom(e\|ic)s?\b | Browse for wiggle files from the NCBI Epigenomics server |
| nupop_0.1 | galaxy | core | text:\bnucleosome · may package NuPoP | Predict nucleosome positioning for DNA sequences of any length |
| [piranha](https://github.com/galaxyproject/tools-iuc/tree/master/tools/piranha) | galaxy | core | text:\bpeak[- ]call(er\|ing)?\b\|\bcalls? p · 2 wrappers merged | Piranha is a peak-caller for CLIP- and RIP-Seq data |
| [pureclip](https://github.com/skrakau/PureCLIP) | galaxy | core | text:\bfootprint | PureCLIP is a tool to detect protein-RNA interaction footprints from single-nucleotide CLIP-seq data, such as iCLIP and eCLIP. It accepts mapped eCLIP/iCLIP rea |
| r_signac_galaxy | galaxy | core | text:\bsc(ATAC\|-ATAC)\|\bsingle[- ](cell\|n · may package Signac | Galaxy wrappers for the r-signac package to analyze scATAC-seq data |
| region_motif_enrichment | galaxy | core | text:\bmotif (discovery\|enrichment\|scan\|s | Determine motif enrichment in genomic regions |
| sharplab_seq_motif | galaxy | core | text:\bmotif (discovery\|enrichment\|scan\|s | sharp lab sequence and motif analysis |
| [suite_hicexplorer](https://github.com/deeptools/HiCExplorer) | galaxy | core | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b · 39 wrappers merged | Sequencing techniques that probe the 3D organization of the genome generate large amounts of data whose processing, analysis and visualization is challenging. H |
| [suite_homer](http://homer.ucsd.edu/homer/index.html) | galaxy | core | text:\bmotif (discovery\|enrichment\|scan\|s · 2 wrappers merged · may package homer | HOMER (Hypergeometric Optimization of Motif EnRichment) is a suite of tools for Motif Discovery and next-gen sequencing analysis. |
| [tmhmm_and_signalp](https://github.com/peterjc/pico_galaxy/tree/master/tools/protein_analysis) | galaxy | core | text:\bpromoter\b\|\benhancer\b\|\bsuper-?e | TMHMM, SignalP, Promoter, RXLR motifs, WoLF PSORT and PSORTb |

### Reading this list

Precision is deliberately not 100%. This is a review queue, not a catalog: the cost of a wrong row here is one glance, while the cost of a missing tool is a gap nobody sees. Two caveats are worth knowing before working through it.

**Galaxy publishes one repository per wrapper, not per tool.** Entries sharing a homepage are merged automatically, which is what collapses AlphaGenome's five wrappers into one row. Where a candidate's name contains an existing catalog tool it is flagged *may package X* and left in, because name containment is exactly the evidence this project refuses to act on: `chipseq_workflows` contains `chipseq` without being a wrapper of it.

**Bioconductor's taxonomy is broader than this catalog's scope.** `Transcription` and `GeneRegulation` are applied to differential-expression and imputation packages too, so a row like an RNA-seq dropout imputer is the taxonomy being loose rather than the filter being broken.