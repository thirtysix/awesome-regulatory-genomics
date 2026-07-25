# Addition review

Generated 2026-07-26 by `pipeline/verify_additions.py` using `zai-org/GLM-5`, a model used for neither the adjudication nor its escalation.

Removing a record needs two models to agree. Adding one had no equivalent check, so this asks an independent third model about every record admitted by hand or by a text rule rather than an ontology term.

**1205 records checked, 132 disputed (11%).**

Nothing here is applied. A dispute is a prompt to re-read the entry, not a verdict: the model sees only the bio.tools name and description, which is exactly the text that was misleading in the first place. It has been right and wrong here: it correctly caught that bio.tools' `mast` is the single-cell package rather than the MEME Suite scanner, and it wrongly objects to plainly in-scope entries whose descriptions are terse.

| Tool | Admitted because | Model's objection |
| --- | --- | --- |
| [3DGene](https://bio.tools/3dgene) | text:\bgene regulatory network|\bregulato | confidence medium, categories none |
| [3DIV](https://bio.tools/3div) | text:\bchromatin (accessibilit|state|loop | confidence medium, categories none |
| [ACEP](https://bio.tools/acep) | text:\bposition (weight|frequency|specifi | confidence high, categories none |
| [Aging Atlas](https://bio.tools/aging-atlas) | text:\bepigenom(e|ic)s?\b | confidence high, categories none |
| [ALGGEN](https://bio.tools/alggen) | text:\btranscription[- ]factor | confidence medium, categories none |
| [Alphabet](https://bio.tools/alphabet) | text:\bsequence logo|\bsequence motifs?\b | confidence high, categories none |
| [AptCompare](https://bio.tools/aptcompare) | text:\bmotif (discovery|enrichment|scan|s | confidence high, categories none |
| [AtlasXploreTM](https://bio.tools/atlasxploretm) | text:\bepigenom(e|ic)s?\b | confidence medium, categories none |
| [BaRDIC](https://bio.tools/bardic) | text:\bpeak[- ]call(er|ing)?\b|\bcalls? p | confidence high, categories none |
| [BioSwitch](https://bio.tools/BioSwitch) | text:\bgene regulatory network|\bregulato | confidence high, categories none |
| [BiSA](https://bio.tools/bisa) | hand-listed by ID | confidence medium, categories none |
| [BSDD](https://bio.tools/bsdd) | text:\bsequence logo|\bsequence motifs?\b | confidence high, categories none |
| [BSGatlas](https://bio.tools/BSGatlas) | text:\btranscription start site|\bCAGE\b | confidence medium, categories none |
| [bwtool 1.0 gamma](https://bio.tools/bwtool) | text:\bChIP[- ]?(seq|chip|exo|nexus)\b|\b | confidence high, categories none |
| [CAGExploreR](https://bio.tools/cagexplorer) | text:\bpromoter\b|\benhancer\b|\bsuper-?e | confidence medium, categories none |
| [cDNA-detector](https://bio.tools/cdna-detector) | text:\bChIP[- ]?(seq|chip|exo|nexus)\b|\b | confidence high, categories none |
| [Cell2location](https://bio.tools/cell2location) | text:\bchromatin (accessibilit|state|loop | confidence high, categories none |
| [CellNetAnalyzer](https://bio.tools/cellnetanalyzer) | text:\bgene regulatory network|\bregulato | confidence high, categories none |
| [CeRNASeek](https://bio.tools/cernaseek) | text:\bgene regulatory network|\bregulato | confidence high, categories none |
| [ChIP-Seq](https://bio.tools/chip-seq-analysis) | text:\bChIP[- ]?(seq|chip|exo|nexus)\b|\b | confidence medium, categories none |
| [ChIPWig](https://bio.tools/chipwig) | text:\bChIP[- ]?(seq|chip|exo|nexus)\b|\b | confidence high, categories none |
| [ChroKit](https://bio.tools/chrokit) | hand-listed by ID | confidence medium, categories none |
| [CircRiC](https://bio.tools/CircRiC) | text:\bcis-regulatory|\bregulatory elemen | confidence medium, categories none |
| [cLoops2](https://bio.tools/cloops2) | text:\bchromatin (accessibilit|state|loop | confidence high, categories none |
| [CNVxplorer](https://bio.tools/cnvxplorer) | text:\btranscription[- ]factor | confidence medium, categories none |
| [CompariPSSM](https://bio.tools/comparipssm) | text:\bposition (weight|frequency|specifi | confidence high, categories none |
| [CoverageView](https://bio.tools/coverageview) | text:\bChIP[- ]?(seq|chip|exo|nexus)\b|\b | confidence high, categories none |
| [CREPE](https://bio.tools/crepe) | text:\btranscription[- ]factor | confidence low, categories none |
| [decorate](https://bio.tools/decorate) | hand-listed by ID | confidence medium, categories none |
| [DeepTFactor](https://bio.tools/deeptfactor) | text:\btranscription[- ]factor | confidence high, categories none |
| [DIANA-miRGen](https://bio.tools/diana-mirgen) | text:\btranscription[- ]factor | confidence high, categories none |
| [DNA Rchitect](https://bio.tools/DNA_Rchitect) | text:\bchromatin (accessibilit|state|loop | confidence medium, categories none |
| [E1DS](https://bio.tools/e1ds) | text:\bsequence logo|\bsequence motifs?\b | confidence high, categories none |
| [edgeR](https://bio.tools/edger) | text:\bChIP[- ]?(seq|chip|exo|nexus)\b|\b | confidence high, categories none |
| [effectR](https://bio.tools/effectR) | text:\bmotif (discovery|enrichment|scan|s | confidence high, categories none |
| [EhecRegNet](https://bio.tools/ehecregnet) | text:\bgene regulatory network|\bregulato | confidence medium, categories none |
| [erma](https://bio.tools/erma) | text:\bepigenom(e|ic)s?\b | confidence medium, categories none |
| [ESCDb](https://bio.tools/escdb) | text:\btranscription[- ]factor | confidence medium, categories none |
| [EvoAug-TF](https://bio.tools/evoaug_tf) | hand-listed by ID | confidence medium, categories none |
| [EWAS](https://bio.tools/ewas_open_platform) | text:\bepigenom(e|ic)s?\b | confidence medium, categories none |
| [exomePeak](https://bio.tools/exomepeak) | text:\bepigenom(e|ic)s?\b | confidence high, categories none |
| [eXpress](https://bio.tools/express) | text:\btranscription[- ]factor | confidence high, categories none |
| [Fertility-GRU](https://bio.tools/Fertility-GRU) | text:\bposition (weight|frequency|specifi | confidence high, categories none |
| [FGviewer](https://bio.tools/fgviewer) | text:\btranscription[- ]factor | confidence medium, categories none |
| [figeno](https://bio.tools/figeno) | text:\bepigenom(e|ic)s?\b | confidence high, categories none |
| [FingerPRINTScan (EBI)](https://bio.tools/fingerprintscan) | text:\bsequence logo|\bsequence motifs?\b | confidence high, categories none |
| [FIRE-pro](https://bio.tools/fire-pro) | text:\bmotif (discovery|enrichment|scan|s | confidence high, categories none |
| [Fly Terminalia Database](https://bio.tools/flyterminalia) | text:\btranscription[- ]factor | confidence high, categories none |
| [GibbsCluster](https://bio.tools/gibbscluster) | text:\bsequence logo|\bsequence motifs?\b | confidence high, categories none |
| [GILoop](https://bio.tools/giloop) | text:\bHiChIP\b|\bChIA-?PET\b|\bCapture-? | confidence high, categories none |
| [GLEANER](https://bio.tools/gleaner) | text:\bchromatin (accessibilit|state|loop | confidence medium, categories none |
| [GraphSite](https://bio.tools/graphsite) | text:\bDNA[- ]binding (site|preference|sp | confidence high, categories none |
| [HaForest](https://bio.tools/haforest) | text:\bepigenom(e|ic)s?\b | confidence medium, categories none |
| [Hi-C Aggregate](https://bio.tools/hi-c_aggregate) | text:\bchromatin (accessibilit|state|loop | confidence high, categories none |
| [HLungDB](https://bio.tools/hlungdb) | text:\btranscription[- ]factor | confidence medium, categories none |
| [htSeqTools](https://bio.tools/htseqtools) | text:\bChIP[- ]?(seq|chip|exo|nexus)\b|\b | confidence medium, categories none |
| [iEpiCas-DL](https://bio.tools/iepicas-dl) | text:\bepigenom(e|ic)s?\b | confidence high, categories none |
| [iGlioSub](https://bio.tools/igliosub) | text:\bepigenom(e|ic)s?\b | confidence medium, categories none |
| [iMARGI](https://bio.tools/iMARGI) | text:\bchromatin (accessibilit|state|loop | confidence high, categories none |
| [ImpulseDE2](https://bio.tools/impulsede2) | text:\bChIP[- ]?(seq|chip|exo|nexus)\b|\b | confidence high, categories none |
| [iODA](https://bio.tools/ioda) | text:\bChIP[- ]?(seq|chip|exo|nexus)\b|\b | confidence medium, categories none |
| [iProDNA-CapsNet](https://bio.tools/iProDNA-CapsNet) | text:\bposition (weight|frequency|specifi | confidence high, categories none |
| [iPromoter-5mC](https://bio.tools/ipromoter-5mc) | text:\bpromoter\b|\benhancer\b|\bsuper-?e | confidence high, categories none |
| [MAGIA2](https://bio.tools/magia2) | text:\bgene regulatory network|\bregulato | confidence high, categories none |
| [MARACAS](https://bio.tools/maracas) | text:\bChIP[- ]?(seq|chip|exo|nexus)\b|\b | confidence medium, categories none |
| [MAST](https://bio.tools/mast) | curated: fetched by ID | confidence high, categories none |
| [MATCHA](https://bio.tools/matcha) | text:\bchromatin (accessibilit|state|loop | confidence medium, categories none |
| [MaxHiC](https://bio.tools/maxhic) | text:\bchromatin (accessibilit|state|loop | confidence high, categories none |
| [MEA](https://bio.tools/mea) | text:\bepigenom(e|ic)s?\b | confidence medium, categories none |
| [MetaLogo](https://bio.tools/metalogo) | text:\bsequence logo|\bsequence motifs?\b | confidence high, categories none |
| [MicroSalmon](https://bio.tools/microsalmon) | text:\bcis-regulatory|\bregulatory elemen | confidence high, categories none |
| [MIREyA](https://bio.tools/mireya) | text:\bpromoter\b|\benhancer\b|\bsuper-?e | confidence medium, categories none |
| [miRinGO](https://bio.tools/miringo) | text:\btranscription[- ]factor | confidence high, categories none |
| [miRvestigator](https://bio.tools/mirvestigator) | text:\bsequence logo|\bsequence motifs?\b | confidence high, categories none |
| [MoonlightR](https://bio.tools/moonlightr) | text:\bgene regulatory network|\bregulato | confidence medium, categories none |
| [Motif3D](https://bio.tools/motif3d) | text:\bsequence logo|\bsequence motifs?\b | confidence high, categories none |
| [Mulan](https://bio.tools/mulan) | text:\btranscription[- ]factor | confidence high, categories none |
| [Mustache](https://bio.tools/mustache) | text:\bchromatin (accessibilit|state|loop | confidence high, categories none |
| [NBIA](https://bio.tools/nbia) | text:\bgene regulatory network|\bregulato | confidence medium, categories none |
| [ngphubinh](https://bio.tools/ngphubinh) | text:\bposition (weight|frequency|specifi | confidence high, categories none |
| [Non-B DB](https://bio.tools/non-b_db) | text:\bsequence logo|\bsequence motifs?\b | confidence medium, categories none |
| [Numbat-multiome](https://bio.tools/numbat-multiome) | text:\bchromatin (accessibilit|state|loop | confidence high, categories none |
| [oRNAment](https://bio.tools/oRNAment) | text:\bmotif (discovery|enrichment|scan|s | confidence high, categories none |
| [p53MutaGene](https://bio.tools/p53mutagene) | hand-listed by ID | confidence low, categories none |
| [PCHi-C](https://bio.tools/PCHi-C) | text:\bchromatin (accessibilit|state|loop | confidence medium, categories none |
| [Peakachu](https://bio.tools/peakachu) | text:\bchromatin (accessibilit|state|loop | confidence high, categories none |
| [PEGR](https://bio.tools/pegr) | text:\bepigenom(e|ic)s?\b | confidence high, categories none |
| [PeSA](https://bio.tools/PeSA) | text:\bposition (weight|frequency|specifi | confidence high, categories none |
| [pftools](https://bio.tools/pftools) | text:\bposition (weight|frequency|specifi | confidence high, categories none |
| [Phyto-LRR](https://bio.tools/phyto-lrr) | text:\bposition (weight|frequency|specifi | confidence high, categories none |
| [PomBase Motif search](https://bio.tools/pombase_motif_search) | text:\bmotif (discovery|enrichment|scan|s | confidence high, categories none |
| [PPI-Miner](https://bio.tools/ppi-miner) | text:\bsequence logo|\bsequence motifs?\b | confidence high, categories none |
| [PresRAT](https://bio.tools/presrat) | text:\bcis-regulatory|\bregulatory elemen | confidence medium, categories none |
| [primirTSS](https://bio.tools/primirtss) | text:\bChIP[- ]?(seq|chip|exo|nexus)\b|\b | confidence medium, categories none |
| [ProbeRating](https://bio.tools/proberating) | text:\btranscription[- ]factor | confidence medium, categories none |
| [progeny](https://bio.tools/progeny) | text:\bfootprint | confidence medium, categories none |
| [ProteDNA](https://bio.tools/protedna) | text:\btranscription[- ]factor | confidence medium, categories none |
| [Protomata](https://bio.tools/protomata) | text:\bmotif (discovery|enrichment|scan|s | confidence high, categories none |
| [PsyMuKB](https://bio.tools/PsyMuKB) | text:\bcis-regulatory|\bregulatory elemen | confidence medium, categories none |
| [qBED](https://bio.tools/qbed) | text:\btranscription[- ]factor | confidence medium, categories none |
| [qDRIP](https://bio.tools/qdrip) | text:\bpeak[- ]call(er|ing)?\b|\bcalls? p | confidence high, categories none |
| [RBscore](https://bio.tools/rbscore) | text:\bDNA[- ]binding (site|preference|sp | confidence high, categories none |
| [ReadOut](https://bio.tools/readout) | hand-listed by ID | confidence high, categories none |
| [RENCO](https://bio.tools/renco) | text:\bgene regulatory network|\bregulato | confidence high, categories none |
| [REPIC](https://bio.tools/REPIC) | text:\bChIP[- ]?(seq|chip|exo|nexus)\b|\b | confidence high, categories ['peak-calling'] |
| [RNAMotifScanX](https://bio.tools/rnamotifscanx) | text:\bmotif (discovery|enrichment|scan|s | confidence high, categories none |
| [RSAT retrieve-ensembl-seq](https://bio.tools/rsat-retrieve-ensembl-seq) | hand-listed by ID | confidence high, categories none |
| [RsHSF](https://bio.tools/RsHSF) | text:\btranscription[- ]factor | confidence medium, categories none |
| [Samscope](https://bio.tools/samscope) | text:\bChIP[- ]?(seq|chip|exo|nexus)\b|\b | confidence high, categories none |
| [SCAN-ATAC](https://bio.tools/scan-atac) | text:\bsc(ATAC|-ATAC)|\bsingle[- ](cell|n | confidence high, categories none |
| [seeMotif](https://bio.tools/seemotif) | text:\bsequence logo|\bsequence motifs?\b | confidence high, categories none |
| [SELANSI](https://bio.tools/selansi) | text:\bgene regulatory network|\bregulato | confidence high, categories none |
| [SeqAcademy](https://bio.tools/seqacademy) | text:\bChIP[- ]?(seq|chip|exo|nexus)\b|\b | confidence high, categories none |
| [SLiMFinder](https://bio.tools/slimfinder) | text:\bmotif (discovery|enrichment|scan|s | confidence high, categories none |
| [SLiMScape 3](https://bio.tools/slimscape) | text:\bmotif (discovery|enrichment|scan|s | confidence high, categories none |
| [SMARTIV](https://bio.tools/smartiv) | text:\bposition (weight|frequency|specifi | confidence high, categories none |
| [SnapHiC](https://bio.tools/snaphic) | text:\bchromatin (accessibilit|state|loop | confidence high, categories none |
| [Snapshot](https://bio.tools/snapshot) | hand-listed by ID | confidence medium, categories none |
| [Strand NGS](https://bio.tools/strand_ngs) | text:\bChIP[- ]?(seq|chip|exo|nexus)\b|\b | confidence medium, categories none |
| [SurvivalMeth](https://bio.tools/survivalmeth) | text:\bpromoter\b|\benhancer\b|\bsuper-?e | confidence medium, categories none |
| [systemPipeR](https://bio.tools/systempiper) | text:\bChIP[- ]?(seq|chip|exo|nexus)\b|\b | confidence high, categories none |
| [Tcbf](https://bio.tools/tcbf) | text:\bHiChIP\b|\bChIA-?PET\b|\bCapture-? | confidence medium, categories none |
| [TFBMiner](https://bio.tools/tfbminer) | text:\btranscription[- ]factor | confidence medium, categories none |
| [TMB](https://bio.tools/TMB) | text:\bnucleosome | confidence low, categories none |
| [transcriptR](https://bio.tools/transcriptr) | text:\bChIP[- ]?(seq|chip|exo|nexus)\b|\b | confidence high, categories none |
| [transCRISPR](https://bio.tools/transcrispr) | text:\bsequence logo|\bsequence motifs?\b | confidence high, categories none |
| [Tulip](https://bio.tools/Tulip) | text:\bChIP[- ]?(seq|chip|exo|nexus)\b|\b | confidence high, categories none |
| [VGO](https://bio.tools/vgo) | text:\bmotif (discovery|enrichment|scan|s | confidence high, categories none |
| [ViennNGS](https://bio.tools/viennngs) | text:\bsequence logo|\bsequence motifs?\b | confidence medium, categories none |
| [VirtualCytometry](https://bio.tools/VirtualCytometry) | text:\btranscription[- ]factor | confidence medium, categories none |
| [vSampler](https://bio.tools/vsampler) | text:\btranscription start site|\bCAGE\b | confidence medium, categories none |
| [Wiggler](https://bio.tools/wiggler) | text:\bChIP[- ]?(seq|chip|exo|nexus)\b|\b | confidence high, categories none |
