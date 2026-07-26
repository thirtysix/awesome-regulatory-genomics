# Repository resolution review

Generated 2026-07-26 by `make repos`.

bio.tools records whatever links a submitter supplied, which for older entries is often only an institutional homepage. This stage looks for the source repository in bioconda recipes, Bioconductor DESCRIPTION fields, PyPI metadata and the tool's own homepage.

**Every candidate is validated.** Guessing by name alone is dangerous: a bare PyPI lookup returns `katylava/memepy` for MEME and `shyal/vulcan`, a flashcard app, for vulcan. A wrong repository link is the same class of error as a wrong DOI, so a candidate is accepted only on an exact name match or real vocabulary overlap between repository and tool.

- **61 accepted** and applied to the catalog.
- **164 held for review** below; none of these are applied.

## Held for review

| Tool | Candidate | Source | Why it was not accepted | Repo description |
| --- | --- | --- | --- | --- |
| ACTION | [xhjkl/action.py](https://github.com/xhjkl/action.py) | pypi | name matches but only 0 shared terms () | Command-line arguments parser |
| ADASTRA | [kyegomez/astra](https://github.com/kyegomez/astra) | pypi | no name match and only 0 shared terms () | Astra is an language/compiler designed to unleash the true power of artificial… |
| Allegro | [BioTools-Tek/packages](https://github.com/BioTools-Tek/packages) | bioconda | no name match and only 0 shared terms () | Collection of bioinformatic packages for public access |
| Alphabet | [reale/alphabet](https://github.com/reale/alphabet) | pypi | name matches but only 0 shared terms () | Uses various methods to recognize text. |
| APPLES | [balabanmetin/apples](https://github.com/balabanmetin/apples) | pypi | name matches but only 0 shared terms () | distance based phylogenetic placement |
| ARGO | [xinehc/argo](https://github.com/xinehc/argo) | bioconda | name matches but only 1 shared terms (genes) | Argo: species-resolved profiling of antibiotic resistance genes in complex meta… |
| BART Cancer | [zanglab/bart2](https://github.com/zanglab/bart2) | homepage | no name match and only 1 shared terms (bart) | bart2 package |
| BARTweb | [zanglab/bart2](https://github.com/zanglab/bart2) | homepage | no name match and only 1 shared terms (bart) | bart2 package |
| BAT | [SuperCowPowers/zat](https://github.com/SuperCowPowers/zat) | pypi | no name match and only 2 shared terms (analysis, data) | Zeek Analysis Tools (ZAT):  Processing and analysis of Zeek network data with P… |
| BioSwitch | [google/safevalues](https://github.com/google/safevalues) | homepage | no name match and only 3 shared terms (com, google, https) |  |
| BioWord | [newrelic/newrelic-browser-agent](https://github.com/newrelic/newrelic-browser-agent) | homepage | no name match and only 0 shared terms () | New Relic Browser Agent |
| BLSSPELLER | [drdwitte/CloudSpeller](https://github.com/drdwitte/CloudSpeller) | homepage | no name match and only 2 shared terms (comparative, discove… | Comparative motif discovery in the cloud: Hadoop implementation |
| BROCKMAN | [FocusLab/brockman](https://github.com/FocusLab/brockman) | pypi | name matches but only 0 shared terms () | A Python client for working with the FocusLab API |
| BSDD | [IfcOpenShell/IfcOpenShell](https://github.com/IfcOpenShell/IfcOpenShell) | pypi | no name match and only 0 shared terms () | Open source IFC library and geometry engine |
| Bubble GUM | [azuline/bubblegum](https://github.com/azuline/bubblegum) | pypi | name matches but only 0 shared terms () | deprecated; just write your own simple script; you can find my replacement in g… |
| CAGExploreR | [hkawaji/dpi1](https://github.com/hkawaji/dpi1) | homepage | no name match and only 1 shared terms (transcription) | Decomposition-based peak identification, which find peaks across a large number… |
| CaiNet | [whatwg/fetch](https://github.com/whatwg/fetch) | homepage | no name match and only 0 shared terms () | Fetch Standard |
| CARMEN | [mdredze/carmen-python](https://github.com/mdredze/carmen-python) | pypi | name matches but only 0 shared terms () | Geolocation for Twitter. |
| CARRIE | [mjem/carrie](https://github.com/mjem/carrie) | pypi | name matches but only 0 shared terms () | Media remote control |
| Cat-E | [usablica/intro.js](https://github.com/usablica/intro.js) | homepage | no name match and only 0 shared terms () | Lightweight, user-friendly onboarding tour library |
| CATCH | [broadinstitute/catch](https://github.com/broadinstitute/catch) | bioconda | name matches but only 0 shared terms () | A package for designing compact and comprehensive capture probe sets. |
| CellRegulonDB | [Teichlab/cellregulondb](https://github.com/Teichlab/cellregulondb) | pypi | name matches but only 0 shared terms () | CellRegulon database code |
| ChAMP | [wweir827/champ](https://github.com/wweir827/champ) | pypi | name matches but only 1 shared terms (selection) |  |
| ChIC | [psaavedra/chic](https://github.com/psaavedra/chic) | pypi | name matches but only 0 shared terms () | CHecker for Items and Components |
| ChIP-GSM | [samtools/samtools](https://github.com/samtools/samtools) | homepage | no name match and only 0 shared terms () | Tools (written in C using htslib) for manipulating next-generation sequencing d… |
| ChIPMunk | [Rigdon/chipmunk](https://github.com/Rigdon/chipmunk) | pypi | name matches but only 0 shared terms () | A very small and simple usage mechanism for Python threadlocals. |
| ChromHMM | [jernst98/ChromHMM](https://github.com/jernst98/ChromHMM) | bioconda | name matches but only 1 shared terms (chromhmm) |  |
| CIRI | [ericb/ciri](https://github.com/ericb/ciri) | pypi | name matches but only 0 shared terms () | Python Object Serialization |
| Clarion | [chishxd/clarion](https://github.com/chishxd/clarion) | pypi | name matches but only 0 shared terms () | A lightweight, cloud-deployed web API for serving machine learning classificati… |
| cobind | [liguowang/cobind](https://github.com/liguowang/cobind) | homepage | name matches but only 1 shared terms (analysis) | collocation analysis of genomics regions |
| CoBRA | [opencobra/cobrapy](https://github.com/opencobra/cobrapy) | pypi | name matches but only 1 shared terms (cobra) | COBRApy is a package for constraint-based modeling of metabolic networks. |
| Cogito | [freepik-company/fc-py-cogito](https://github.com/freepik-company/fc-py-cogito) | pypi | name matches but only 1 shared terms (cogito) |  |
| CoMeBack | [agamm/comeback](https://github.com/agamm/comeback) | pypi | name matches but only 1 shared terms (comeback) | Project restoration in one command, auto open everything! |
| ComHub | [whatwg/fetch](https://github.com/whatwg/fetch) | homepage | no name match and only 1 shared terms (standard) | Fetch Standard |
| createcontrolsubset | [samtools/htslib](https://github.com/samtools/htslib) | homepage | no name match and only 2 shared terms (bam, sam) | C library for high-throughput sequencing data formats |
| CREMA | [bmcfee/crema](https://github.com/bmcfee/crema) | pypi | name matches but only 0 shared terms () | convolutional and recurrent estimators for music analysis |
| CREME | [creme-ml/creme](https://github.com/creme-ml/creme) | pypi | name matches but only 0 shared terms () | 🌊 Online machine learning in Python |
| CRISPRFinder | [hyattpd/Prodigal](https://github.com/hyattpd/Prodigal) | homepage | no name match and only 0 shared terms () | Prodigal Gene Prediction Software |
| Cropper | [astronouth7303/cropper](https://github.com/astronouth7303/cropper) | pypi | name matches but only 1 shared terms (crop) | A simple application to crop images into multiple pieces. |
| CRUNCH | [kracekumar/crunch](https://github.com/kracekumar/crunch) | pypi | name matches but only 1 shared terms (line) | Command line utitlity to download files from terminal |
| CSAR | [ajfriend/csar_py](https://github.com/ajfriend/csar_py) | pypi | name matches but only 0 shared terms () | Conic spherical aspect ratio: tightest enclosing cone of a point set on the uni… |
| csaw | [NicholasCullenCooper/csaw](https://github.com/NicholasCullenCooper/csaw) | pypi | name matches but only 0 shared terms () | AI config governance for every repo: mount layered agent instructions, skills,… |
| CSDeconv | [newrelic/newrelic-browser-agent](https://github.com/newrelic/newrelic-browser-agent) | homepage | no name match and only 0 shared terms () | New Relic Browser Agent |
| CSSQ | [Tatsh/cssq](https://github.com/Tatsh/cssq) | pypi | name matches but only 0 shared terms () | Filter HTML with a CSS query |
| cuffdiff | [cole-trapnell-lab/cufflinks](https://github.com/cole-trapnell-lab/cufflinks) | homepage | no name match and only 2 shared terms (expression, find) |  |
| DamMapper | [readthedocs/sphinx_rtd_theme](https://github.com/readthedocs/sphinx_rtd_theme) | homepage | no name match and only 0 shared terms () | Sphinx theme from Read the Docs |
| dbGAP | [crDDI/dbgap](https://github.com/crDDI/dbgap) | pypi | name matches but only 1 shared terms (dbgap) | dbGaP to biocaddie conversion utilities |
| DBTSS | [DBKERO/genome_browser](https://github.com/DBKERO/genome_browser) | homepage | no name match and only 0 shared terms () | Simple and fast html5 canvas based genome browser |
| DECODE | [deshima-dev/decode](https://github.com/deshima-dev/decode) | pypi | name matches but only 0 shared terms () | :zap: DESHIMA code for data analysis |
| DeFuse | [antsticky/defuse](https://github.com/antsticky/defuse) | pypi | name matches but only 0 shared terms () |  |
| DExTER | [igormagalhaesr/dexter](https://github.com/igormagalhaesr/dexter) | pypi | name matches but only 1 shared terms (analysis) | Data Exploration Terser |
| DiRE | [kyclark/dire](https://github.com/kyclark/dire) | pypi | name matches but only 0 shared terms () | Python equivalent of Perl's warn/die functions |
| DMFpred | [soedinglab/hh-suite](https://github.com/soedinglab/hh-suite) | homepage | no name match and only 1 shared terms (protein) | Remote protein homology detection suite. |
| ENdb | [endatabas/endb](https://github.com/endatabas/endb) | pypi | name matches but only 1 shared terms (database) | SQL document database with full history. |
| EP3 | [thespacedoctor/ep3](https://github.com/thespacedoctor/ep3) | pypi | name matches but only 0 shared terms () | Tools to help verify astronomical data meets the standards required for ESO Pha… |
| epiGeEC | [galaxyproject/galaxy-test-data](https://github.com/galaxyproject/galaxy-test-data) | homepage | no name match and only 0 shared terms () | Test data files used by Galaxy. |
| EpiSegMix | [whatwg/fetch](https://github.com/whatwg/fetch) | homepage | no name match and only 0 shared terms () | Fetch Standard |
| EPIXplorer | [bioinfomaticsCSU/LoopPredictor](https://github.com/bioinfomaticsCSU/LoopPredictor) | homepage | no name match and only 1 shared terms (enhancer) | LoopPredictor: Predicting unknown enhancer-mediated genome topology by an ensem… |
| FIRE | [google/python-fire](https://github.com/google/python-fire) | pypi | name matches but only 0 shared terms () | Python Fire is a library for automatically generating command line interfaces (… |
| FiToM | [newrelic/newrelic-browser-agent](https://github.com/newrelic/newrelic-browser-agent) | homepage | no name match and only 0 shared terms () | New Relic Browser Agent |
| FITs | [ntessore/fits](https://github.com/ntessore/fits) | pypi | name matches but only 1 shared terms (fits) | FITS file reader for Python |
| FlexFlux | [lmarmiesse/FlexFlux](https://github.com/lmarmiesse/FlexFlux) | homepage | name matches but only 1 shared terms (metabolic) | FlexFlux is a tool for metabolic fluxes analysis. It is a java application usab… |
| FXR | [pmav99/fxr](https://github.com/pmav99/fxr) | pypi | name matches but only 0 shared terms () | An ag/sed replacement |
| GeneCodis | [GENyO-BioInformatics/GeneCodis](https://github.com/GENyO-BioInformatics/GeneCodis) | homepage | name matches but only 1 shared terms (genecodis) |  |
| getintrons | [TecharoHQ/anubis](https://github.com/TecharoHQ/anubis) | homepage | no name match and only 0 shared terms () | Weighs the soul of incoming HTTP requests to stop AI crawlers |
| GGEA | [clement-alexandre/TotemBionet](https://github.com/clement-alexandre/TotemBionet) | pypi | no name match and only 1 shared terms (networks) | Interactive Jupyter notebook for an accessible and reproducible computational a… |
| GINsim | [GINsim/GINsim-python](https://github.com/GINsim/GINsim-python) | pypi | name matches but only 0 shared terms () | Python bindings for GINsim and bioLQM |
| GPMiner | [LHanLi/GPminer](https://github.com/LHanLi/GPminer) | pypi | name matches but only 0 shared terms () |  |
| GRaNIE | [whatwg/fetch](https://github.com/whatwg/fetch) | homepage | no name match and only 0 shared terms () | Fetch Standard |
| GRaNPA | [whatwg/fetch](https://github.com/whatwg/fetch) | homepage | no name match and only 0 shared terms () | Fetch Standard |
| GREAT | [Julian/Great](https://github.com/Julian/Great) | pypi | name matches but only 0 shared terms () | A ratings aggregator |
| GREGOR | [modelblocks-org/gregor](https://github.com/modelblocks-org/gregor) | pypi | name matches but only 0 shared terms () | Disaggregation and aggregation of spatial data |
| GReNaDIne | [whatwg/fetch](https://github.com/whatwg/fetch) | homepage | no name match and only 0 shared terms () | Fetch Standard |
| GROK | [zopefoundation/grok](https://github.com/zopefoundation/grok) | pypi | name matches but only 1 shared terms (grok) | Grok: Now even cavemen can use Zope 3! |
| Hammock | [kadirpekel/hammock](https://github.com/kadirpekel/hammock) | pypi | name matches but only 0 shared terms () | rest like a boss |
| HINT | [parklab/HiNT](https://github.com/parklab/HiNT) | bioconda | name matches but only 0 shared terms () | HiC for  copy Number variation and Translocation detection |
| HOCOMOCO | [autosome-ru/hocomoco_v9](https://github.com/autosome-ru/hocomoco_v9) | homepage | name matches but only 0 shared terms () | Old version of HOCOMOCO TFBS motif database, version 9: https://autosome.ru/HOC… |
| ICEberg | [iceberg-project/iceberg-middleware](https://github.com/iceberg-project/iceberg-middleware) | pypi | name matches but only 0 shared terms () | This repo contains the ICEBERG middleware as it is agreed by the members of the… |
| INCLUSive | [numpde/inclusive](https://github.com/numpde/inclusive) | pypi | name matches but only 0 shared terms () | Python package for 'range' and 'slice' with inclusive boundary. |
| INSECT | [somasays/insect](https://github.com/somasays/insect) | pypi | name matches but only 0 shared terms () |  |
| IntOMICS | [whatwg/fetch](https://github.com/whatwg/fetch) | homepage | no name match and only 0 shared terms () | Fetch Standard |
| iSeq | [BioOmics/iSeq](https://github.com/BioOmics/iSeq) | bioconda | name matches but only 1 shared terms (data) | Download sequencing data and metadata from  GSA, SRA, ENA, and DDBJ databases.   |
| LAP | [gatagat/lap](https://github.com/gatagat/lap) | pypi | name matches but only 0 shared terms () | Linear Assignment Problem solver (LAPJV/LAPMOD). |
| LBFextract | [readthedocs/sphinx_rtd_theme](https://github.com/readthedocs/sphinx_rtd_theme) | homepage | no name match and only 0 shared terms () | Sphinx theme from Read the Docs |
| LiPLike | [whatwg/fetch](https://github.com/whatwg/fetch) | homepage | no name match and only 0 shared terms () | Fetch Standard |
| MAGA | [whtsky/maga](https://github.com/whtsky/maga) | pypi | name matches but only 0 shared terms () | Another DHT crawler written in Python using asyncio |
| Manhattan Harvester | [bvilhjal/ldpred](https://github.com/bvilhjal/ldpred) | homepage | no name match and only 1 shared terms (gwas) |  |
| MARGE | [suwangbio/MARGE_py3](https://github.com/suwangbio/MARGE_py3) | bioconda | name matches but only 1 shared terms (marge) | MARGE:Model-based Analysis of Regulation of Gene Expression (for python3) |
| Match | [EducationalTestingService/match](https://github.com/EducationalTestingService/match) | pypi | name matches but only 0 shared terms () | Match tokenized words and phrases within the original, untokenized, often messy… |
| MDscan | [LQCT/MDScan](https://github.com/LQCT/MDScan) | pypi | name matches but only 0 shared terms () | An efficient approach to RMSD-Based HDBSCAN Clustering of long Molecular Dynami… |
| MEDUSA | [combogenomics/medusa](https://github.com/combogenomics/medusa) | bioconda | name matches but only 1 shared terms (approach) | A draft genome scaffolder that uses multiple reference genomes in a graph-based… |
| MEME | [katylava/memepy](https://github.com/katylava/memepy) | pypi | name matches but only 0 shared terms () | Generate memes from http://memegenerator.co |
| methodical | [lalinguette/methodical](https://github.com/lalinguette/methodical) | pypi | name matches but only 0 shared terms () | A simple tool that scans markdown pages for headlines and assembles them in a t… |
| MKT | [danchev/openmarkets](https://github.com/danchev/openmarkets) | pypi | no name match and only 0 shared terms () | A Model Context Protocol (MCP) server for agentic retrieval of financial market… |
| MODalyseR | [jgm/pandoc](https://github.com/jgm/pandoc) | homepage | no name match and only 0 shared terms () | Universal markup converter |
| MPRAlib | [kircherlab/MPRAlib](https://github.com/kircherlab/MPRAlib) | bioconda | name matches but only 1 shared terms (data) | Library to analyse, filter and plot MPRA count data. |
| Mulan | [Ailln/mulan](https://github.com/Ailln/mulan) | pypi | name matches but only 0 shared terms () | 📻 人类的本质之木兰诗「复读机」～ |
| MultiBind | [BecksteinLab/multibind](https://github.com/BecksteinLab/multibind) | pypi | name matches but only 0 shared terms () | A Python package for building thermodynamically consistent state graphs. |
| MuStARD | [heyman/mustard](https://github.com/heyman/mustard) | pypi | name matches but only 0 shared terms () | DIY Docker PAAS |
| Netview | [danielgiampaolo/CIS4930_Python](https://github.com/danielgiampaolo/CIS4930_Python) | pypi | no name match and only 0 shared terms () | Network_Graphs |
| NIACS | [pebrown88/pettsy](https://github.com/pebrown88/pettsy) | homepage | no name match and only 0 shared terms () | Perturbation Theory Software for Systems |
| Non-B DB | [abcsFrederick/non-B_gfa](https://github.com/abcsFrederick/non-B_gfa) | homepage | no name match and only 3 shared terms (forming, motifs, non) | Identify non-B forming motifs |
| NucPosDB | [TeifLab/ChromHL](https://github.com/TeifLab/ChromHL) | homepage | no name match and only 1 shared terms (dna) | Predicting microdomain formation in chromatin from the DNA sequence and protein… |
| ODIN | [python-odin/odin](https://github.com/python-odin/odin) | pypi | name matches but only 1 shared terms (data) | Data-structure definition/validation/traversal, mapping and serialisation toolk… |
| oPOSSUM | [jgitr/opossum](https://github.com/jgitr/opossum) | pypi | name matches but only 1 shared terms (opossum) |  |
| ORIO | [brnorris03/Orio](https://github.com/brnorris03/Orio) | pypi | name matches but only 1 shared terms (generation) | Orio is an open-source extensible framework for the definition of domain-specif… |
| oRNAment | [scravy/ornament](https://github.com/scravy/ornament) | pypi | name matches but only 0 shared terms () | Pattern Matching for Python 3.7+ in a simple, yet powerful, extensible manner. |
| P-SCAN | [brunobeltran/pscan](https://github.com/brunobeltran/pscan) | pypi | name matches but only 0 shared terms () |  |
| Parseq | [kklmn/ParSeq](https://github.com/kklmn/ParSeq) | pypi | name matches but only 0 shared terms () | Python software library for Parallel execution of Sequential data analysis. |
| PatternChrome | [whatwg/fetch](https://github.com/whatwg/fetch) | homepage | no name match and only 0 shared terms () | Fetch Standard |
| peakcalling_findpeaks | [samtools/htslib](https://github.com/samtools/htslib) | homepage | no name match and only 0 shared terms () | C library for high-throughput sequencing data formats |
| PERFUMES | [whatwg/fetch](https://github.com/whatwg/fetch) | homepage | no name match and only 0 shared terms () | Fetch Standard |
| PINES | [jpn--/pines](https://github.com/jpn--/pines) | pypi | name matches but only 0 shared terms () | reusable code tools |
| PipMaker | [DanteAnnetta/pipmaker](https://github.com/DanteAnnetta/pipmaker) | pypi | name matches but only 0 shared terms () | A simple module to create your own modules and upload it in pip! |
| POBO | [mschubert/python-obo](https://github.com/mschubert/python-obo) | pypi | no name match and only 0 shared terms () | Python parser and network representation of Open Biological and Biomedical Onto… |
| PomBase Motif search | [angular/angular](https://github.com/angular/angular) | homepage | no name match and only 0 shared terms () | Deliver web apps with confidence 🚀 |
| Porpoise | [alecthomas/porpoise](https://github.com/alecthomas/porpoise) | pypi | name matches but only 0 shared terms () | Porpoise - A Redis-based analytics framework |
| PoSSuM | [brysontyrrell/Possum](https://github.com/brysontyrrell/Possum) | pypi | name matches but only 0 shared terms () | A packaging tool for Python based AWS serverless applications. |
| Possum | [brysontyrrell/Possum](https://github.com/brysontyrrell/Possum) | pypi | name matches but only 0 shared terms () | A packaging tool for Python based AWS serverless applications. |
| POXO | [sashakile/poco](https://github.com/sashakile/poco) | pypi | no name match and only 1 shared terms (poxo) | Small and lazy panda |
| PPD | [mikiTesf/ppd](https://github.com/mikiTesf/ppd) | pypi | name matches but only 0 shared terms () | Download any periodic JW publication (g, wp, w, mwb) in any format from the com… |
| PPGR | [PolarPayne/ppgr](https://github.com/PolarPayne/ppgr) | pypi | name matches but only 0 shared terms () | Python Piped GRapher |
| Precise | [microprediction/precise](https://github.com/microprediction/precise) | pypi | name matches but only 0 shared terms () | Online Covariance and Correlation Estimation |
| PREDICT | [Svdvoort/PREDICTFastr](https://github.com/Svdvoort/PREDICTFastr) | pypi | name matches but only 1 shared terms (predict) |  |
| PWMScan | [mbreese/pwmscan](https://github.com/mbreese/pwmscan) | pypi | name matches but only 0 shared terms () |  |
| qsea | [lbiryukov/qsea](https://github.com/lbiryukov/qsea) | pypi | name matches but only 0 shared terms () | Working with Qlik Sense Engine API in a pythonic way |
| QSeq | [newrelic/newrelic-browser-agent](https://github.com/newrelic/newrelic-browser-agent) | homepage | no name match and only 0 shared terms () | New Relic Browser Agent |
| racoon_clip | [readthedocs/sphinx_rtd_theme](https://github.com/readthedocs/sphinx_rtd_theme) | homepage | no name match and only 0 shared terms () | Sphinx theme from Read the Docs |
| ReadOut | [lainproliant/readout](https://github.com/lainproliant/readout) | pypi | name matches but only 0 shared terms () | A framework for detecting changes and reacting to them. |
| RECON | [Dfam-consortium/RepeatModeler](https://github.com/Dfam-consortium/RepeatModeler) | bioconda | no name match and only 0 shared terms () | De-Novo Repeat Discovery Tool |
| REDUCE | [rlabduke/reduce](https://github.com/rlabduke/reduce) | bioconda | name matches but only 0 shared terms () | Reduce - tool for adding and correcting hydrogens in PDB files |
| Regulus | [whatwg/fetch](https://github.com/whatwg/fetch) | homepage | no name match and only 0 shared terms () | Fetch Standard |
| REPIC | [ccameron/REPIC](https://github.com/ccameron/REPIC) | bioconda | name matches but only 1 shared terms (repic) | REliable PIcking by Consensus (REPIC) - an ensemble learning methodology for cr… |
| S-MART | [TecharoHQ/anubis](https://github.com/TecharoHQ/anubis) | homepage | no name match and only 0 shared terms () | Weighs the soul of incoming HTTP requests to stop AI crawlers |
| SALAD | [wieden-kennedy/salad](https://github.com/wieden-kennedy/salad) | pypi | name matches but only 0 shared terms () | Salad has moved!  |
| SBSA | [google/safevalues](https://github.com/google/safevalues) | homepage | no name match and only 0 shared terms () |  |
| SCOPE | [danijar/scope](https://github.com/danijar/scope) | pypi | name matches but only 0 shared terms () | Scalable metrics logging and analysis |
| SCRAT | [javiber/scrat](https://github.com/javiber/scrat) | pypi | name matches but only 0 shared terms () | Persistent Caching of Expensive Function Results |
| SEA | [shanbay/sea](https://github.com/shanbay/sea) | pypi | name matches but only 0 shared terms () | rpc framework built on grpc |
| SeqBox | [iOLIGO/SeqBox](https://github.com/iOLIGO/SeqBox) | pypi | name matches but only 0 shared terms () | seq process tools box |
| SEQSIM | [tresoldi/seqsim](https://github.com/tresoldi/seqsim) | pypi | name matches but only 1 shared terms (sequence) | Python package for calculating sequence similarity (especially string similarit… |
| SHARK.capture | [whatwg/fetch](https://github.com/whatwg/fetch) | homepage | no name match and only 0 shared terms () | Fetch Standard |
| SMARTIV | [babel/babel](https://github.com/babel/babel) | homepage | no name match and only 0 shared terms () | 🐠 Babel is a compiler for writing next generation JavaScript. |
| Snapper | [DNKonanov/snapper-man-test](https://github.com/DNKonanov/snapper-man-test) | homepage | name matches but only 0 shared terms () | Readthedocs manual for Snapper |
| SPONGE | [IamBusy/sponge](https://github.com/IamBusy/sponge) | pypi | name matches but only 0 shared terms () | An elegant  cache library for python  一个高性能优雅的缓存库 |
| SPP | [hit9/spp_py](https://github.com/hit9/spp_py) | pypi | name matches but only 0 shared terms () | SSDB Protocol Parser For Python, Built For Speed. |
| SSA | [yannikschaelte/ssa](https://github.com/yannikschaelte/ssa) | pypi | name matches but only 0 shared terms () | Stochastic Simulation Algorithms. |
| SteinerNet | [afshinsadeghi/steinernetpy](https://github.com/afshinsadeghi/steinernetpy) | pypi | name matches but only 0 shared terms () | Python library implementing Steiner tree algorithms  |
| STREAM | [pinellolab/STREAM](https://github.com/pinellolab/STREAM) | bioconda | name matches but only 0 shared terms () | STREAM: Single-cell Trajectories Reconstruction, Exploration And Mapping of sin… |
| SwissRegulon | [jmbreda/Sanity](https://github.com/jmbreda/Sanity) | homepage | no name match and only 0 shared terms () | Filtering of Poison noise on a single-cell RNA-seq UMI count matrix |
| T-WEoN | [networkbiolab/WEoN](https://github.com/networkbiolab/WEoN) | homepage | no name match and only 2 shared terms (networks, weighted) | Inference method for Weighted Epigenomics Networks |
| TACT | [jonchang/tact](https://github.com/jonchang/tact) | pypi | name matches but only 0 shared terms () | Taxonomy addition for complete trees |
| TFmotifView | [steinmann/peakzilla](https://github.com/steinmann/peakzilla) | homepage | no name match and only 2 shared terms (factor, transcriptio… | Peakzilla is a self-learning algorithm to identify transcription factor binding… |
| TFPred | [vivekka93/tfpred](https://github.com/vivekka93/tfpred) | pypi | name matches but only 1 shared terms (model) | Use tensorflow model to run predictions with resource constraints |
| TimeNexus | [cytoscape/cytoscape](https://github.com/cytoscape/cytoscape) | homepage | no name match and only 1 shared terms (cytoscape) | Cytoscape: an open source platform for network analysis and visualization |
| TMB | [bioinfo-pf-curie/TMB](https://github.com/bioinfo-pf-curie/TMB) | bioconda | name matches but only 0 shared terms () | Tumor Mutational Burden |
| TripLexicon | [SchulzLab/TriplexAligner](https://github.com/SchulzLab/TriplexAligner) | homepage | no name match and only 2 shared terms (dna, rna) | A method for sequence based prediction of RNA-DNA triplices. |
| UROPA | [loosolab/UROPA](https://github.com/loosolab/UROPA) | bioconda | name matches but only 1 shared terms (universal) | Universal RObust Peak Annotator |
| VISION | [guanjue/IDEAS_2018](https://github.com/guanjue/IDEAS_2018) | homepage | no name match and only 1 shared terms (data) | Jointly characterizing epigenetic dynamics across multiple cell types |
| WaveSeqR | [rdrr-io/rdrr-issues](https://github.com/rdrr-io/rdrr-issues) | homepage | no name match and only 0 shared terms () | rdrr.io issues |
| WebLogo 3 | [WebLogo/weblogo](https://github.com/WebLogo/weblogo) | homepage | no name match and only 2 shared terms (logos, sequence) | WebLogo 3: Sequence Logos redrawn |
| Weeder | [GambitResearch/weeder](https://github.com/GambitResearch/weeder) | pypi | name matches but only 0 shared terms () | Remove unneeded historical files |
| X2K Web | [MaayanLab/x2k_web](https://github.com/MaayanLab/x2k_web) | homepage | name matches but only 0 shared terms () | The X2K Web project |
| YAPP | [hathora/yapp-sdk](https://github.com/hathora/yapp-sdk) | pypi | name matches but only 0 shared terms () |  |
