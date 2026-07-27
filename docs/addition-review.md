# Addition review

Generated 2026-07-27 by `pipeline/verify_additions.py` using `zai-org/GLM-5`, a model used for neither the adjudication nor its escalation.

Removing a record needs two models to agree. Adding one had no equivalent check, so this asks an independent third model about every record admitted by hand or by a text rule rather than an ontology term.

**1206 records checked, 147 disputed (12%).**

Nothing here is applied. A dispute is a prompt to re-read the entry, not a verdict: the model sees only the bio.tools name and description, which is exactly the text that was misleading in the first place. It has been right and wrong here: it correctly caught that bio.tools' `mast` is the single-cell package rather than the MEME Suite scanner, and it wrongly objects to plainly in-scope entries whose descriptions are terse.

| Tool | Admitted because | Model's objection |
| --- | --- | --- |
| [Aging Atlas](https://bio.tools/aging-atlas) | text:\bepigenom(e\|ic)s?\b | confidence high, categories none |
| [AllEnricher](https://bio.tools/allenricher) | text:\bepigenom(e\|ic)s?\b | confidence high, categories none |
| [AptCompare](https://bio.tools/aptcompare) | text:\bmotif (discovery\|enrichment\|scan\|s | confidence high, categories none |
| [AtlasXploreTM](https://bio.tools/atlasxploretm) | text:\bepigenom(e\|ic)s?\b | confidence medium, categories none |
| [bacon](https://bio.tools/bacon) | text:\bepigenom(e\|ic)s?\b | confidence high, categories none |
| [BAT](https://bio.tools/bat) | text:\btranscription[- ]factor | confidence high, categories none |
| [BEADS](https://bio.tools/beads) | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | confidence high, categories none |
| [BIJ Database](https://bio.tools/bij) | text:\bgene regulatory network\|\bregulato | confidence high, categories none |
| [BioSwitch](https://bio.tools/BioSwitch) | text:\bgene regulatory network\|\bregulato | confidence high, categories none |
| [BiSA](https://bio.tools/bisa) | hand-listed by ID | confidence low, categories none |
| [BpForms](https://bio.tools/bpforms) | text:\bepigenom(e\|ic)s?\b | confidence high, categories none |
| [BSDD](https://bio.tools/bsdd) | text:\bsequence logo\|\bsequence motifs?\b | confidence high, categories none |
| [BSGatlas](https://bio.tools/BSGatlas) | text:\btranscription start site\|\bCAGE\b | confidence high, categories none |
| [bwtool 1.0 gamma](https://bio.tools/bwtool) | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | confidence high, categories none |
| [CancerLSP](https://bio.tools/CancerLSP) | text:\bepigenom(e\|ic)s?\b | confidence high, categories none |
| [cDNA-detector](https://bio.tools/cdna-detector) | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | confidence high, categories none |
| [Cell2location](https://bio.tools/cell2location) | text:\bchromatin (accessibilit\|state\|loop | confidence high, categories none |
| [CellNetAnalyzer](https://bio.tools/cellnetanalyzer) | text:\bgene regulatory network\|\bregulato | confidence high, categories none |
| [CeRNASeek](https://bio.tools/cernaseek) | text:\bgene regulatory network\|\bregulato | confidence high, categories none |
| [ChiCMaxima](https://bio.tools/ChiCMaxima) | hand-listed by ID | confidence high, categories none |
| [ChIPexoQual](https://bio.tools/chipexoqual) | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | confidence high, categories none |
| [ChIPsim](https://bio.tools/chipsim) | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | confidence high, categories none |
| [ChIPWig](https://bio.tools/chipwig) | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | confidence high, categories none |
| [cLoops](https://bio.tools/cLoops) | text:\bcis-regulatory\|\bregulatory elemen | confidence high, categories none |
| [cobind](https://bio.tools/cobind) | hand-listed by ID | confidence low, categories none |
| [CplexA](https://bio.tools/cplexa) | text:\btranscription[- ]factor | confidence medium, categories none |
| [CREPE](https://bio.tools/crepe) | text:\btranscription[- ]factor | confidence low, categories none |
| [D-miRT](https://bio.tools/d-mirt) | text:\btranscription start site\|\bCAGE\b | confidence high, categories none |
| [DACT](https://bio.tools/dact) | text:\bepigenom(e\|ic)s?\b | confidence medium, categories none |
| [dbGAP](https://bio.tools/dbgap) | text:\bepigenom(e\|ic)s?\b | confidence high, categories none |
| [decorate](https://bio.tools/decorate) | hand-listed by ID | confidence medium, categories none |
| [DeepTFactor](https://bio.tools/deeptfactor) | text:\btranscription[- ]factor | confidence high, categories none |
| [DeepTools](https://bio.tools/deeptools) | hand-listed by ID | confidence high, categories none |
| [Discovery Environment](https://bio.tools/discovery_environment) | text:\bpromoter\b\|\benhancer\b\|\bsuper-?e | confidence medium, categories none |
| [DLO Hi-C](https://bio.tools/DLO_Hi-C) | text:\bcis-regulatory\|\bregulatory elemen | confidence high, categories none |
| [DNA Rchitect](https://bio.tools/DNA_Rchitect) | text:\bchromatin (accessibilit\|state\|loop | confidence high, categories none |
| [DriverPower](https://bio.tools/driverpower) | hand-listed by ID | confidence high, categories none |
| [edgeR](https://bio.tools/edger) | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | confidence high, categories none |
| [effectR](https://bio.tools/effectR) | text:\bmotif (discovery\|enrichment\|scan\|s | confidence high, categories none |
| [Enhort](https://bio.tools/enhort) | hand-listed by ID | confidence medium, categories none |
| [EpiVisR](https://bio.tools/epivisr) | text:\bepigenom(e\|ic)s?\b | confidence high, categories none |
| [erma](https://bio.tools/erma) | text:\bepigenom(e\|ic)s?\b | confidence medium, categories none |
| [EvoAug-TF](https://bio.tools/evoaug_tf) | hand-listed by ID | confidence medium, categories none |
| [EWAS](https://bio.tools/ewas_open_platform) | text:\bepigenom(e\|ic)s?\b | confidence high, categories none |
| [exomePeak](https://bio.tools/exomepeak) | text:\bepigenom(e\|ic)s?\b | confidence high, categories none |
| [eXpress](https://bio.tools/express) | text:\btranscription[- ]factor | confidence high, categories none |
| [Fertility-GRU](https://bio.tools/Fertility-GRU) | text:\bposition (weight\|frequency\|specifi | confidence high, categories none |
| [FGviewer](https://bio.tools/fgviewer) | text:\btranscription[- ]factor | confidence high, categories none |
| [figeno](https://bio.tools/figeno) | text:\bepigenom(e\|ic)s?\b | confidence high, categories none |
| [FingerPRINTScan (EBI)](https://bio.tools/fingerprintscan) | text:\bsequence logo\|\bsequence motifs?\b | confidence high, categories none |
| [FIRE-pro](https://bio.tools/fire-pro) | text:\bmotif (discovery\|enrichment\|scan\|s | confidence high, categories none |
| [FIREcaller](https://bio.tools/firecaller) | text:\bchromatin (accessibilit\|state\|loop | confidence high, categories none |
| [FlexFlux](https://bio.tools/flexflux) | text:\bgene regulatory network\|\bregulato | confidence high, categories none |
| [GDCRNATools](https://bio.tools/gdcrnatools) | text:\bgene regulatory network\|\bregulato | confidence high, categories none |
| [GeneCodis](https://bio.tools/genecodis) | text:\btranscription[- ]factor | confidence high, categories none |
| [GenePalette](https://bio.tools/genepalette) | text:\btranscription[- ]factor | confidence high, categories none |
| [GILoop](https://bio.tools/giloop) | text:\bHiChIP\b\|\bChIA-?PET\b\|\bCapture-? | confidence high, categories none |
| [GPCR-SAS](https://bio.tools/gpcr-sas) | text:\bsequence logo\|\bsequence motifs?\b | confidence high, categories none |
| [GROK](https://bio.tools/grok) | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | confidence high, categories none |
| [HaForest](https://bio.tools/haforest) | text:\bepigenom(e\|ic)s?\b | confidence high, categories none |
| [Hi-C Aggregate](https://bio.tools/hi-c_aggregate) | text:\bchromatin (accessibilit\|state\|loop | confidence medium, categories none |
| [HiCNAtra](https://bio.tools/HiCNAtra) | text:\bchromatin (accessibilit\|state\|loop | confidence high, categories none |
| [HiSIF](https://bio.tools/hisif) | text:\bpromoter\b\|\benhancer\b\|\bsuper-?e | confidence high, categories none |
| [HLungDB](https://bio.tools/hlungdb) | text:\btranscription[- ]factor | confidence high, categories none |
| [IDDomainSpotter](https://bio.tools/IDDomainSpotter) | text:\btranscription[- ]factor | confidence high, categories none |
| [iEpiCas-DL](https://bio.tools/iepicas-dl) | text:\bepigenom(e\|ic)s?\b | confidence high, categories none |
| [iGlioSub](https://bio.tools/igliosub) | text:\bepigenom(e\|ic)s?\b | confidence high, categories none |
| [iMARGI](https://bio.tools/iMARGI) | text:\bchromatin (accessibilit\|state\|loop | confidence medium, categories none |
| [ImpulseDE2](https://bio.tools/impulsede2) | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | confidence high, categories none |
| [Introme](https://bio.tools/introme) | text:\b(non-?coding\|regulatory) (variant\| | confidence high, categories none |
| [iODA](https://bio.tools/ioda) | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | confidence high, categories none |
| [LongGeneDB](https://bio.tools/longgenedb) | text:\bepigenom(e\|ic)s?\b | confidence high, categories none |
| [MARACAS](https://bio.tools/maracas) | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | confidence medium, categories none |
| [MATCHA](https://bio.tools/matcha) | text:\bchromatin (accessibilit\|state\|loop | confidence medium, categories none |
| [MaxHiC](https://bio.tools/maxhic) | text:\bchromatin (accessibilit\|state\|loop | confidence high, categories none |
| [MEA](https://bio.tools/mea) | text:\bepigenom(e\|ic)s?\b | confidence medium, categories none |
| [Meffil](https://bio.tools/Meffil) | text:\bepigenom(e\|ic)s?\b | confidence high, categories none |
| [MicroSalmon](https://bio.tools/microsalmon) | text:\bcis-regulatory\|\bregulatory elemen | confidence high, categories none |
| [MinePath](https://bio.tools/minepath) | text:\bgene regulatory network\|\bregulato | confidence medium, categories none |
| [MIREyA](https://bio.tools/mireya) | text:\bpromoter\b\|\benhancer\b\|\bsuper-?e | confidence medium, categories none |
| [miRinGO](https://bio.tools/miringo) | text:\btranscription[- ]factor | confidence high, categories none |
| [miRvestigator](https://bio.tools/mirvestigator) | text:\bsequence logo\|\bsequence motifs?\b | confidence high, categories none |
| [Motif3D](https://bio.tools/motif3d) | text:\bsequence logo\|\bsequence motifs?\b | confidence high, categories none |
| [MultiMM](https://bio.tools/multimm) | text:\bnucleosome | confidence high, categories none |
| [Mustache](https://bio.tools/mustache) | text:\bchromatin (accessibilit\|state\|loop | confidence high, categories none |
| [ngphubinh](https://bio.tools/ngphubinh) | text:\bposition (weight\|frequency\|specifi | confidence high, categories none |
| [NGS-QC Generator](https://bio.tools/ngs-qc_generator) | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | confidence high, categories none |
| [nucleoSim](https://bio.tools/nucleosim) | text:\bnucleosome | confidence high, categories none |
| [Numbat-multiome](https://bio.tools/numbat-multiome) | text:\bchromatin (accessibilit\|state\|loop | confidence high, categories none |
| [Onto-Tools](https://bio.tools/onto-tools) | text:\bpromoter\b\|\benhancer\b\|\bsuper-?e | confidence high, categories none |
| [p53MutaGene](https://bio.tools/p53mutagene) | hand-listed by ID | confidence high, categories none |
| [pareidolia](https://bio.tools/pareidolia) | text:\bchromatin (accessibilit\|state\|loop | confidence high, categories none |
| [PASH](https://bio.tools/pash) | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | confidence high, categories none |
| [PathwayCommons SPARQL endpoint](https://bio.tools/PathwayCommons_SPARQL_endpoint) | text:\bgene regulatory network\|\bregulato | confidence high, categories none |
| [patmatdb](https://bio.tools/patmatdb) | text:\bsequence logo\|\bsequence motifs?\b | confidence high, categories none |
| [PEGR](https://bio.tools/pegr) | text:\bepigenom(e\|ic)s?\b | confidence medium, categories none |
| [pftools](https://bio.tools/pftools) | text:\bposition (weight\|frequency\|specifi | confidence high, categories none |
| [piPipes](https://bio.tools/pipipes) | text:\btranscription start site\|\bCAGE\b | confidence high, categories none |
| [PlantTFcat](https://bio.tools/planttfcat) | text:\btranscription[- ]factor | confidence medium, categories none |
| [Pluto Bio](https://bio.tools/pluto_bio) | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | confidence high, categories none |
| [PomBase Motif search](https://bio.tools/pombase_motif_search) | text:\bmotif (discovery\|enrichment\|scan\|s | confidence high, categories none |
| [PPI-Miner](https://bio.tools/ppi-miner) | text:\bsequence logo\|\bsequence motifs?\b | confidence high, categories none |
| [PredicTF](https://bio.tools/predictf) | text:\btranscription[- ]factor | confidence high, categories none |
| [PresRAT](https://bio.tools/presrat) | text:\bcis-regulatory\|\bregulatory elemen | confidence high, categories none |
| [progeny](https://bio.tools/progeny) | text:\bfootprint | confidence high, categories none |
| [Protomata](https://bio.tools/protomata) | text:\bmotif (discovery\|enrichment\|scan\|s | confidence high, categories none |
| [PsyMuKB](https://bio.tools/PsyMuKB) | text:\bcis-regulatory\|\bregulatory elemen | confidence high, categories none |
| [qBED](https://bio.tools/qbed) | text:\btranscription[- ]factor | confidence medium, categories none |
| [RBscore](https://bio.tools/rbscore) | text:\bDNA[- ]binding (site\|preference\|sp | confidence high, categories none |
| [ReadOut](https://bio.tools/readout) | hand-listed by ID | confidence high, categories none |
| [RENCO](https://bio.tools/renco) | text:\bgene regulatory network\|\bregulato | confidence high, categories none |
| [REPIC](https://bio.tools/REPIC) | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | confidence high, categories none |
| [RNAMotifScanX](https://bio.tools/rnamotifscanx) | text:\bmotif (discovery\|enrichment\|scan\|s | confidence high, categories none |
| [RSAT retrieve-ensembl-seq](https://bio.tools/rsat-retrieve-ensembl-seq) | hand-listed by ID | confidence high, categories none |
| [RsHSF](https://bio.tools/RsHSF) | text:\btranscription[- ]factor | confidence medium, categories none |
| [Samscope](https://bio.tools/samscope) | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | confidence high, categories none |
| [SBGN bricks](https://bio.tools/sbgn_bricks) | text:\bgene regulatory network\|\bregulato | confidence high, categories none |
| [SCAN-ATAC](https://bio.tools/scan-atac) | text:\bsc(ATAC\|-ATAC)\|\bsingle[- ](cell\|n | confidence high, categories none |
| [seeMotif](https://bio.tools/seemotif) | text:\bsequence logo\|\bsequence motifs?\b | confidence high, categories none |
| [SeqAcademy](https://bio.tools/seqacademy) | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | confidence high, categories none |
| [Sequence Searcher](https://bio.tools/sequence_searcher) | text:\bsequence logo\|\bsequence motifs?\b | confidence high, categories none |
| [SHARK.capture](https://bio.tools/shark.capture) | text:\bsequence logo\|\bsequence motifs?\b | confidence high, categories none |
| [SigProfilerTopography](https://bio.tools/sigprofilertopography) | text:\bchromatin (accessibilit\|state\|loop | confidence medium, categories none |
| [SIRW](https://bio.tools/sirw) | text:\bsequence logo\|\bsequence motifs?\b | confidence high, categories none |
| [SnapFISH](https://bio.tools/snapfish) | text:\bchromatin (accessibilit\|state\|loop | confidence high, categories none |
| [SnapHiC](https://bio.tools/snaphic) | text:\bchromatin (accessibilit\|state\|loop | confidence high, categories none |
| [Snapshot](https://bio.tools/snapshot) | hand-listed by ID | confidence medium, categories none |
| [StanEx1](https://bio.tools/StanEx1) | text:\bpromoter\b\|\benhancer\b\|\bsuper-?e | confidence medium, categories none |
| [StoneMod](https://bio.tools/stonemod) | text:\bpromoter\b\|\benhancer\b\|\bsuper-?e | confidence high, categories none |
| [SubSeqer](https://bio.tools/subseqer) | text:\bsequence logo\|\bsequence motifs?\b | confidence high, categories none |
| [SULDEX](https://bio.tools/suldex) | hand-listed by ID | confidence medium, categories none |
| [SurvivalMeth](https://bio.tools/survivalmeth) | text:\bpromoter\b\|\benhancer\b\|\bsuper-?e | confidence high, categories none |
| [systemPipeR](https://bio.tools/systempiper) | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | confidence high, categories none |
| [TADeus2](https://bio.tools/tadeus2) | hand-listed by ID | confidence high, categories none |
| [Tcbf](https://bio.tools/tcbf) | text:\bHiChIP\b\|\bChIA-?PET\b\|\bCapture-? | confidence high, categories none |
| [TFBMiner](https://bio.tools/tfbminer) | text:\btranscription[- ]factor | confidence medium, categories none |
| [tfextract](https://bio.tools/tfextract) | text:\btranscription[- ]factor | confidence medium, categories none |
| [TFPred](https://bio.tools/tfpred) | text:\btranscription[- ]factor | confidence high, categories none |
| [TMB](https://bio.tools/TMB) | text:\bnucleosome | confidence high, categories none |
| [transCRISPR](https://bio.tools/transcrispr) | text:\bsequence logo\|\bsequence motifs?\b | confidence medium, categories none |
| [TransView](https://bio.tools/transview) | text:\bChIP[- ]?(seq\|chip\|exo\|nexus)\b\|\b | confidence medium, categories none |
| [TRDistiller](https://bio.tools/trdistiller) | text:\bsequence logo\|\bsequence motifs?\b | confidence medium, categories none |
| [TripLexicon](https://bio.tools/triplexicon) | text:\bcis-regulatory\|\bregulatory elemen | confidence medium, categories none |
| [VGO](https://bio.tools/vgo) | text:\bmotif (discovery\|enrichment\|scan\|s | confidence medium, categories none |
| [ViennNGS](https://bio.tools/viennngs) | text:\bsequence logo\|\bsequence motifs?\b | confidence high, categories none |
| [VirtualCytometry](https://bio.tools/VirtualCytometry) | text:\btranscription[- ]factor | confidence high, categories none |
| [WashU Epigenome Browser](https://bio.tools/washu_epigenome_browser) | text:\bepigenom(e\|ic)s?\b | confidence high, categories none |
