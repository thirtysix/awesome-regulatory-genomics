# Category audit

558 rows display categories the LLM pass assigned; 1430 (tool, category) pairs were judged.

- **253** assigned categories every sample from both families rejected.
- **77** categories the pass discarded that both families restore.
- A row left with nothing falls back to the rule-derived set.

| tool | removed | restored |
| --- | --- | --- |
| 3DGene | regulatory-elements | - |
| 3DIV | regulatory-elements, chip-resources | - |
| AgingReG | grn-inference, regulatory-variants | - |
| ANANASTRA | - | tfbs-prediction |
| Animal Transcription Factor Database | tfbs-prediction | - |
| APEC | - | nucleosome-chromatin |
| APPLES | motif-discovery | - |
| ArchR | peak-annotation | regulatory-elements |
| ASAP | - | regulatory-elements |
| Asymmetron | tfbs-prediction, regulatory-elements | - |
| ATACgraph | - | nucleosome-chromatin |
| Attune | - | nucleosome-chromatin |
| BayesPI-BAR2 | - | tfbs-prediction |
| BCRANK | - | motif-discovery |
| BindSpace | motif-scanning | - |
| BioProspector | - | motif-scanning |
| BioTapestry | grn-inference | - |
| BiSA | motif-scanning, tfbs-prediction | - |
| BIT | peak-calling | tfbs-prediction |
| BooleanNet | grn-inference | - |
| BROCKMAN | - | single-cell |
| BSGatlas | regulatory-elements | - |
| CAGEfightR | - | regulatory-elements |
| CamRegBase | regulatory-elements, chip-resources | - |
| CanASM | regulatory-variants | regulatory-elements |
| Cancer CRC | peak-calling | - |
| capC-MAP | peak-calling, peak-annotation | - |
| CARNIVAL | grn-inference | - |
| CATCH | peak-calling, peak-annotation, chip-resources | - |
| CCIP | regulatory-elements | - |
| CCSeq | peak-calling, peak-annotation | - |
| CEAS | motif-discovery | - |
| CellWalkR | grn-inference | - |
| CENTDIST | motif-scanning | - |
| CFSP | regulatory-elements | - |
| CharID | grn-inference | - |
| ChIA-PET | regulatory-elements, peak-annotation | - |
| ChiCMaxima | regulatory-elements, peak-calling | - |
| ChIP-AP | motif-discovery | - |
| ChIP-Hub | peak-calling | - |
| chipchipnorm | peak-calling | - |
| CHIPIN | peak-calling | - |
| ChIPseqR | - | nucleosome-chromatin |
| ChIPSeqSpike | peak-annotation | - |
| ChIPuana | peak-annotation | - |
| ChIPWig | chip-resources | - |
| ChIPXpress | tfbs-prediction, chip-resources | - |
| ChromaSig | motif-discovery | - |
| ChromBPNet | - | tfbs-prediction |
| CisCross | motif-discovery, motif-scanning | - |
| CisMols | - | comparative |
| CITRUS | - | nucleosome-chromatin |
| ClinTAD | regulatory-variants | - |
| cobind | peak-annotation | - |
| COCAS | peak-calling | - |
| COCOA | - | nucleosome-chromatin |
| CombSAFE | chip-resources | regulatory-elements |
| CompareProspector | motif-comparison | - |
| CONFAC | - | tfbs-prediction |
| convert-matrix | motif-comparison | - |
| CoRec | peak-annotation | - |
| COUGER | motif-discovery, motif-scanning, peak-annotation | - |
| CplexA | regulatory-elements | - |
| CPModule | peak-annotation | - |
| CREAM | peak-annotation, grn-inference | - |
| CREMA | - | peak-calling |
| CREPE | regulatory-elements | - |
| CRISPRepi | regulatory-elements, peak-calling | - |
| CRUNCH | peak-annotation | - |
| CSA | chip-resources | - |
| DAStk - Differential ATAC-seq toolkit | peak-annotation, regulatory-variants | - |
| dbInDel | - | chip-resources |
| dbscATAC | - | chip-resources |
| DeconPeaker | peak-annotation, single-cell | - |
| decorate | regulatory-elements | - |
| Deep-loop | regulatory-elements | - |
| deepC | regulatory-elements | - |
| DeepCAGE | - | nucleosome-chromatin |
| DeepGMAP | grn-inference | - |
| DeepLUCIA | grn-inference | - |
| DeepMR | motif-discovery, tfbs-prediction | - |
| DeepRegFinder | - | tfbs-prediction |
| DeepTools | peak-annotation, nucleosome-chromatin | - |
| DeepVISP | motif-discovery, tfbs-prediction | - |
| DGW | peak-calling, comparative | nucleosome-chromatin |
| DLoopCaller | peak-calling | - |
| EAT-UpTF | tfbs-prediction | - |
| EhecRegNet | regulatory-variants | - |
| ElemeNT 2023 | motif-discovery | - |
| ENCODE DCC | peak-calling | - |
| EpiAlign | comparative | - |
| EpiAlignment | peak-annotation | - |
| EpiCompare | peak-calling, peak-annotation | - |
| epiRomics | peak-calling, peak-annotation | - |
| epiScanpy | - | nucleosome-chromatin |
| Eucalyptus Multi-omics Database (EucaMOD) | regulatory-elements, chip-resources, regulatory-variants | - |
| ezGeno | peak-calling, grn-inference | - |
| fcScan | tfbs-prediction | - |
| figeno | regulatory-elements, peak-annotation | - |
| findpromoter | - | regulatory-elements |
| FlexFlux | grn-inference | - |
| Footer | - | motif-scanning |
| FORGE2 | - | regulatory-elements |
| FunChIP | peak-calling | - |
| FunSiP | tfbs-prediction, regulatory-elements | - |
| GeneCodis | regulatory-elements | - |
| Genome Surveyor | motif-discovery | - |
| genomeSidekick | peak-annotation | - |
| GENOVA | nucleosome-chromatin | - |
| GGB | peak-annotation | - |
| Gibbs Motif Sampler | - | tfbs-prediction, regulatory-elements |
| GimmeMotifs | - | motif-comparison |
| GOTHiC | regulatory-elements | - |
| GPro | motif-discovery | - |
| GRAFIMO | - | tfbs-prediction |
| graphsim | grn-inference | - |
| GREAP | regulatory-elements | - |
| gReLU | - | tfbs-prediction |
| GRiNCH | grn-inference | - |
| GRNdb | chip-resources | - |
| GroovDB | tfbs-prediction | - |
| Haystack | motif-discovery, motif-scanning | - |
| HemAtlas | single-cell | - |
| HHCDB | - | chip-resources, nucleosome-chromatin |
| HRTBLDb | - | regulatory-elements |
| Human-scATAC-Corpus | - | chip-resources, nucleosome-chromatin |
| IAnimal | chip-resources | - |
| iCis i-Cardio | regulatory-variants | - |
| ICN | grn-inference | - |
| iMARGI | regulatory-elements | - |
| ImmuneRegulation | - | regulatory-variants |
| iModulonDB | chip-resources | - |
| iRegNet | regulatory-elements, peak-calling | - |
| jPREdictor | - | tfbs-prediction |
| LASAGNA-Search | - | tfbs-prediction |
| LBFextract | tfbs-prediction, regulatory-variants | - |
| LncSEA | regulatory-elements, chip-resources | - |
| LOLAweb | peak-annotation | - |
| MACPET | peak-annotation | - |
| MAGGIE | - | regulatory-variants |
| Magma | - | tfbs-prediction |
| MAnorm_2 | peak-annotation | - |
| MAPS | peak-calling, peak-annotation | - |
| MARGE | peak-calling | - |
| MCLand | grn-inference | - |
| MET | motif-discovery | tfbs-prediction |
| META-BASE | chip-resources | - |
| MicroFootPrinter | - | regulatory-elements |
| MicroSalmon | tfbs-prediction | - |
| MIRA | regulatory-elements | - |
| MochiView | chip-resources | - |
| MONKEY | - | tfbs-prediction |
| MotifGenie | peak-annotation | - |
| Motto | motif-comparison | - |
| MuGVRE | comparative | - |
| Multiomix | regulatory-variants | - |
| mutalisk | regulatory-elements, regulatory-variants | - |
| MYBS | peak-annotation | regulatory-elements |
| NarrowPeaks | peak-calling | - |
| NCBI Epigenomics | - | nucleosome-chromatin |
| Nebula | chip-resources | - |
| NetProphet | - | tfbs-prediction |
| Non-B DB | motif-databases | - |
| NRL | regulatory-elements, peak-calling | - |
| OneSC | grn-inference | - |
| OWAS | - | nucleosome-chromatin |
| PCHi-C | regulatory-elements | - |
| Peakachu | peak-calling | - |
| PhaeoEpiView | peak-calling, chip-resources | - |
| phantompeakqualtools | peak-calling | - |
| PHIRE | - | regulatory-elements |
| PhyloCTCFLooping | motif-scanning | - |
| PhyloPGM | - | comparative |
| PIRCh-seq | peak-calling, peak-annotation | - |
| Plant Regulomics | chip-resources | - |
| PlantTFcat | motif-databases, tfbs-prediction | - |
| PlantTFDB | tfbs-prediction, regulatory-elements, grn-inference | - |
| PlnTFDB | grn-inference | - |
| plot2DO | peak-annotation | - |
| PPGR | regulatory-elements, chip-resources | - |
| Predector | motif-discovery | - |
| PreDREM | - | motif-databases |
| progeny | grn-inference | - |
| PRP | regulatory-elements | - |
| Pyicoteo | peak-annotation | - |
| Q-nexus | peak-calling | - |
| R-loop | regulatory-elements | - |
| R3CPET | grn-inference | - |
| RACIPE | grn-inference | - |
| RCADE | motif-discovery, chip-resources | - |
| ReadOut | motif-scanning | - |
| recoup | peak-annotation | - |
| RegAnalyst | - | motif-discovery, motif-databases |
| Regeneration Roadmap | chip-resources | - |
| RegPrecise | - | motif-databases |
| RELICS | motif-discovery | - |
| ReMap | peak-calling, peak-annotation | - |
| RHPCG | grn-inference | - |
| RSAT retrieve-ensembl-seq | regulatory-elements | - |
| RSAT suite | motif-comparison | - |
| RSAT Var-tools | - | motif-scanning |
| rVista | - | tfbs-prediction |
| SATORI | - | regulatory-elements |
| SBSA | peak-annotation | - |
| sc-MAESTRO | regulatory-elements | - |
| scATAC-pro | - | regulatory-elements |
| scBasset | - | nucleosome-chromatin |
| scEpiSearch | - | nucleosome-chromatin |
| scEpiTools | chip-resources | - |
| scGRNom | regulatory-variants | single-cell |
| SCOIT | grn-inference | - |
| SCOPE | - | tfbs-prediction |
| SDDA | - | motif-discovery |
| SEGCOND | peak-calling | - |
| SEgene | grn-inference | - |
| Segtools | peak-annotation | - |
| SeqCode | regulatory-elements | - |
| seqplots | motif-scanning, peak-annotation | - |
| seqsetvis | peak-annotation | - |
| SexAnnoDB | chip-resources, regulatory-variants | - |
| Signaling Pathways Project | - | grn-inference |
| SilencerDB | regulatory-variants | - |
| SimBindProfiles | peak-annotation | - |
| SimSearch | comparative | - |
| sismonr | grn-inference | - |
| SnapATAC | footprinting, peak-calling | nucleosome-chromatin |
| SnapHiC | nucleosome-chromatin | - |
| Snapshot | single-cell | - |
| SraTailor | chip-resources | - |
| SSA | motif-scanning, motif-comparison | - |
| Strand NGS | chip-resources | - |
| SULDEX | motif-discovery, motif-scanning | - |
| SVM2CRM | peak-annotation | - |
| SwissRegulon | - | tfbs-prediction |
| SynoR | - | tfbs-prediction |
| systemPipeR | peak-calling, peak-annotation | - |
| T2 | peak-calling, peak-annotation | - |
| Target Explorer | motif-discovery | - |
| TargetGeneReg | regulatory-variants | - |
| TcoF-DB | chip-resources | - |
| TCseq | regulatory-elements, peak-annotation | - |
| TDTHub | - | regulatory-elements |
| TEISER | - | motif-discovery |
| TF-Prioritizer | peak-calling | - |
| TFBIND | - | motif-scanning |
| TFBS | - | motif-scanning |
| TFEA.ChIP | chip-resources | - |
| TFmotifView | motif-comparison | - |
| TFpredict | tfbs-prediction | - |
| TFutils | chip-resources | - |
| ThreaDNA | motif-scanning | - |
| TraFaC | - | comparative |
| TransView | peak-calling, peak-annotation | - |
| UniBind | - | chip-resources |
| UniPath | regulatory-elements | - |
| universal TTSs | motif-discovery, motif-scanning | - |
| VISION | grn-inference | - |
| VISIONET | grn-inference | - |
| WashU Epigenome Browser | regulatory-elements, peak-annotation, chip-resources | - |
| X-CNN | peak-calling | - |
