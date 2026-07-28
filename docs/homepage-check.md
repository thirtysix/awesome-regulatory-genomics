# Homepage check

Generated 2026-07-28 by `make check-links`.

Nearly half of this catalog has no source repository, only a homepage, and academic URLs rot. This is the link check for those.

**A non-200 is not a dead link.** The DOI checker learned this the expensive way: it once reported 152 broken DOIs, of which 151 were rate-limiting. Web servers fail in more ways than Crossref does, so the outcomes are graded and only `dead` is asserted anywhere the reader sees.

| State | Count | Share | Meaning |
| --- | ---: | ---: | --- |
| `ok` | 1384 | 75% | answered 2xx, possibly after a redirect |
| `blocked` | 19 | 1% | 401/403/405. The page is there; the server refuses us or the method |
| `ratelimited` | 20 | 1% | 429 or 5xx. The server is up and struggling. Recheck, never report |
| `unreachable` | 283 | 15% | DNS, TLS, refused or timeout. Often real death, often a slow institutional host |
| `dead` | 131 | 7% | 404 or 410. The server answered and said no |

## Dead links (131)

These are the ones worth acting on. Fix the entry at bio.tools where possible, so the correction reaches every consumer of that registry.

| Tool | URL | Detail |
| --- | --- | --- |
| RNABindR | http://ailab1.ist.psu.edu/RNABindR/ | HTTP 404 |
| GREAT | http://bejerano.stanford.edu/great/public/html/ | HTTP 404 |
| ESCDb | http://biit.cs.ut.ee/escd | HTTP 404 |
| TRlnc | http://bio.licpathway.net/TRlnc | HTTP 404 |
| CATA | http://bio.licpathway.net/cata/ | HTTP 404 |
| BAC | http://bioconductor.org/packages/release/bioc/html/BAC.html | HTTP 404 |
| BayesPeak | http://bioconductor.org/packages/release/bioc/html/BayesPeak.html | HTTP 404 |
| CSSP | http://bioconductor.org/packages/release/bioc/html/CSSP.html | HTTP 404 |
| ChIC | http://bioconductor.org/packages/release/bioc/html/ChIC.html | HTTP 404 |
| ChIPSeqSpike | http://bioconductor.org/packages/release/bioc/html/ChIPSeqSpike.html | HTTP 404 |
| CoRegNet | http://bioconductor.org/packages/release/bioc/html/CoRegNet.html | HTTP 404 |
| DBChIP | http://bioconductor.org/packages/release/bioc/html/DBChIP.html | HTTP 404 |
| DChIPRep | http://bioconductor.org/packages/release/bioc/html/DChIPRep.html | HTTP 404 |
| FunChIP | http://bioconductor.org/packages/release/bioc/html/FunChIP.html | HTTP 404 |
| FunciSNP | http://bioconductor.org/packages/release/bioc/html/FunciSNP.html | HTTP 404 |
| GenoGAM | http://bioconductor.org/packages/release/bioc/html/GenoGAM.html | HTTP 404 |
| IPPD | http://bioconductor.org/packages/release/bioc/html/IPPD.html | HTTP 404 |
| ImpulseDE2 | http://bioconductor.org/packages/release/bioc/html/ImpulseDE2.html | HTTP 404 |
| MACPET | http://bioconductor.org/packages/release/bioc/html/MACPET.html | HTTP 404 |
| Mirsynergy | http://bioconductor.org/packages/release/bioc/html/Mirsynergy.html | HTTP 404 |
| MotIV | http://bioconductor.org/packages/release/bioc/html/MotIV.html | HTTP 404 |
| NarrowPeaks | http://bioconductor.org/packages/release/bioc/html/NarrowPeaks.html | HTTP 404 |
| PICS | http://bioconductor.org/packages/release/bioc/html/PICS.html | HTTP 404 |
| PING | http://bioconductor.org/packages/release/bioc/html/PING.html | HTTP 404 |
| RIPSeeker | http://bioconductor.org/packages/release/bioc/html/RIPSeeker.html | HTTP 404 |
| Rcade | http://bioconductor.org/packages/release/bioc/html/Rcade.html | HTTP 404 |
| Repitools | http://bioconductor.org/packages/release/bioc/html/Repitools.html | HTTP 404 |
| Ringo | http://bioconductor.org/packages/release/bioc/html/Ringo.html | HTTP 404 |
| SEPIRA | http://bioconductor.org/packages/release/bioc/html/SEPIRA.html | HTTP 404 |
| STAN | http://bioconductor.org/packages/release/bioc/html/STAN.html | HTTP 404 |
| SVM2CRM | http://bioconductor.org/packages/release/bioc/html/SVM2CRM.html | HTTP 404 |
| SimBindProfiles | http://bioconductor.org/packages/release/bioc/html/SimBindProfiles.html | HTTP 404 |
| SpidermiR | http://bioconductor.org/packages/release/bioc/html/SpidermiR.html | HTTP 404 |
| TDARACNE | http://bioconductor.org/packages/release/bioc/html/TDARACNE.html | HTTP 404 |
| TransView | http://bioconductor.org/packages/release/bioc/html/TransView.html | HTTP 404 |
| chroGPS | http://bioconductor.org/packages/release/bioc/html/chroGPS.html | HTTP 404 |
| chromstaR | http://bioconductor.org/packages/release/bioc/html/chromstaR.html | HTTP 404 |
| cobindR | http://bioconductor.org/packages/release/bioc/html/cobindR.html | HTTP 404 |
| exomePeak | http://bioconductor.org/packages/release/bioc/html/exomePeak.html | HTTP 404 |
| htSeqTools | http://bioconductor.org/packages/release/bioc/html/htSeqTools.html | HTTP 404 |
| joda | http://bioconductor.org/packages/release/bioc/html/joda.html | HTTP 404 |
| mQTL.NMR | http://bioconductor.org/packages/release/bioc/html/mQTL.NMR.html | HTTP 404 |
| motifRG | http://bioconductor.org/packages/release/bioc/html/motifRG.html | HTTP 404 |
| paxtoolsr | http://bioconductor.org/packages/release/bioc/html/paxtoolsr.html | HTTP 404 |
| pcaGoPromoter | http://bioconductor.org/packages/release/bioc/html/pcaGoPromoter.html | HTTP 404 |
| rGADEM | http://bioconductor.org/packages/release/bioc/html/rGADEM.html | HTTP 404 |
| rMAT | http://bioconductor.org/packages/release/bioc/html/rMAT.html | HTTP 404 |
| seqplots | http://bioconductor.org/packages/release/bioc/html/seqplots.html | HTTP 404 |
| trena | http://bioconductor.org/packages/release/bioc/html/trena.html | HTTP 404 |
| triform | http://bioconductor.org/packages/release/bioc/html/triform.html | HTTP 404 |
| trigger | http://bioconductor.org/packages/release/bioc/html/trigger.html | HTTP 404 |
| DNaseR | http://bioconductor.riken.jp/packages/2.14/bioc/html/DNaseR.html | HTTP 404 |
| Expresso | http://bioinformatics.cs.vt.edu/expresso/ | HTTP 404 |
| TFBSfinder | http://bits.iis.sinica.edu.tw/~TFBSfinder/ | HTTP 404 |
| MYBS | http://bits.iis.sinica.edu.tw/~mybs/ | HTTP 404 |
| SCANMOT | http://caps.ncbs.res.in/scanmot/scanmot.html | HTTP 404 |
| MEDUSA | http://cbio.mskcc.org/leslielab/software/medusa | HTTP 404 |
| MARGE | http://cistrome.org/MARGE/ | HTTP 404 |
| SAMPDI-3D | http://compbio.clemson.edu/SAMPDI-3D/ | HTTP 404 |
| HotNet | http://compbio.cs.brown.edu/projects/hotnet/ | HTTP 404 |
| RPMCMC | http://daweb.ism.ac.jp/yoshidalab/motif/ | HTTP 404 |
| POBO | http://ekhidna.biocenter.helsinki.fi/poxo/pobo/ | HTTP 404 |
| POCO | http://ekhidna.biocenter.helsinki.fi/poxo/poco/ | HTTP 404 |
| scEnhancer | http://enhanceratlas.net/scenhancer/ | HTTP 404 |
| RSAT peak-motifs | http://floresta.eead.csic.es/rsat/peak-motifs_form.cgi | HTTP 404 |
| BayesPI-BAR2 | http://folk.uio.no/junbaiw/BayesPI-BAR2/ | HTTP 404 |
| WebMOTIFS | http://fraenkel.mit.edu/webmotifs/ | HTTP 404 |
| McPromoter | http://genes.mit.edu/McPromoter.html | HTTP 404 |
| PINES | http://genetics.bwh.harvard.edu/pines/ | HTTP 404 |
| MAPPER Database | http://genome.ufl.edu/mapperdb | HTTP 404 |
| GenomeTraFaC | http://genometrafac.cchmc.org/genome-trafac/index.jsp | HTTP 404 |
| TFBScluster | http://hscl.cimr.cam.ac.uk/TFBScluster_genome_portal.html | HTTP 404 |
| ChIP-Array | http://jjwanglab.org/chip-array/ | HTTP 404 |
| GWAS3D | http://jjwanglab.org/gwas3d | HTTP 404 |
| MochiView | http://johnsonlab.ucsf.edu/sj/mochiview-start/ | HTTP 404 |
| LOLAweb | http://lolaweb.databio.org | HTTP 404 |
| MetalDetector | http://metaldetector.dsi.unifi.it/v2.0/ | HTTP 404 |
| Imaging-AMARETTO | http://portals.broadinstitute.org/pochetlab/amaretto.html | HTTP 404 |
| PupasView | http://pupasuite.bioinfo.cipf.es/ | HTTP 404 |
| RENATO | http://renato.bioinfo.cipf.es | HTTP 404 |
| PePr | http://sartorlab.ccmb.med.umich.edu/node/6 | HTTP 404 |
| RDb2C2 | http://structpred.life.tsinghua.edu.cn/rdb2c2.html | HTTP 404 |
| TraFaC | http://trafac.cchmc.org/trafac/index.jsp | HTTP 404 |
| Genome Surveyor | http://veda.cs.uiuc.edu/gs | HTTP 404 |
| TransModis | http://wanglab.ucsd.edu/star/download.php | HTTP 404 |
| Porpoise | http://web.unimelb-bioinfortools.cloud.edu.au/Porpoise/ | HTTP 404 |
| PolyaPeak | http://web1.sph.emory.edu/users/hwu30/software/polyaPeak.html | HTTP 404 |
| WebGMAP | http://www.bioinfolab.org/software/webgmap | HTTP 404 |
| PredictRegulon | http://www.cdfd.org.in/predictregulon/ | HTTP 404 |
| p53MutaGene | http://www.chemoprofiling.org/cgi-bin/GEO/tp53/web_run_tp53.V1.pl | HTTP 404 |
| RsHSF | http://www.cibiv.at/services/hsf/info | HTTP 404 |
| Bubble GUM | http://www.ciml.univ-mrs.fr/applications/BubbleGUM/index.html | HTTP 404 |
| oPOSSUM | http://www.cisreg.ca/oPOSSUM/ | HTTP 404 |
| Cistrome | http://www.cistrome.org/Cistrome/Cistrome_Project.html# | HTTP 404 |
| CoryneRegNet | http://www.coryneregnet.de | HTTP 404 |
| UnderIICRMS | http://www.dei.unipd.it/~ciompin/main/UnderIICRMS.html | HTTP 404 |
| Lasergene | http://www.dnastar.com/t-products-dnastar-lasergene-core.aspx | HTTP 404 |
| EnhancerAtlas | http://www.enhanceratlas.org/indexv2.php | HTTP 404 |
| PROBC | http://www.github.com/seferlab/probc | HTTP 404 |
| WEB-THERMODYN | http://www.gsa.buffalo.edu/dna/dk/WEBTHERMODYN/ | HTTP 404 |
| BSDB | http://www.ifpan.edu.pl/BSDB/ | HTTP 404 |
| FlyTF | http://www.mrc-lmb.cam.ac.uk/genomes/FlyTF/old_index.html | HTTP 404 |
| NCBI Epigenomics | http://www.ncbi.nlm.nih.gov/epigenomics | HTTP 410 |
| RegAnalyst | http://www.nii.ac.in/~deepak/RegAnalyst/ | HTTP 404 |
| HMRFBayesHiC | http://www.unc.edu/~yunmli/HMRFBayesHiC/ | HTTP 404 |
| CASSys | http://www.zbh.uni-hamburg.de/en/research/application-oriented-bioinformatics/researchproj | HTTP 404 |
| MPRA design tools | https://andrewghazi.shinyapps.io/designmpra/ | HTTP 404 |
| PanoromiX | https://bioinfo-abcc.ncifcrf.gov/panoromics/ | HTTP 404 |
| AIModules | https://bioinfo-wuerz.de/aimodules/ | HTTP 404 |
| CUT and RUNTools | https://bitbucket.org/qzhudfci/cutruntools/ | HTTP 404 |
| Deep Sequence and Shape Motif (DESSO) | https://bmbl.bmi.osumc.edu/DESSO | HTTP 404 |
| IRIS3 | https://bmbl.bmi.osumc.edu/iris3/ | HTTP 404 |
| VISTA Enhancer Browser | https://enhancer.lbl.gov/frnt_page_n.shtml | HTTP 404 |
| annotategenes | https://galaxy.pasteur.fr/tool_runner?tool_id=toolshed.pasteur.fr/repos/fmareuil/annotateg | HTTP 404 |
| annotatepeaks | https://galaxy.pasteur.fr/tool_runner?tool_id=toolshed.pasteur.fr/repos/fmareuil/annotatep | HTTP 404 |
| extractcentralregions | https://galaxy.pasteur.fr/tool_runner?tool_id=toolshed.pasteur.fr/repos/fmareuil/extractce | HTTP 404 |
| filtercontrol | https://galaxy.pasteur.fr/tool_runner?tool_id=toolshed.pasteur.fr/repos/fmareuil/filtercon | HTTP 404 |
| makestatschipseq | https://galaxy.pasteur.fr/tool_runner?tool_id=toolshed.pasteur.fr/repos/fmareuil/makestats | HTTP 404 |
| maketssdist | https://galaxy.pasteur.fr/tool_runner?tool_id=toolshed.pasteur.fr/repos/fmareuil/maketssdi | HTTP 404 |
| findpromoter | https://galaxy.pasteur.fr/tool_runner?tool_id=toolshed.pasteur.fr/repos/fmareuil/promoteur | HTTP 404 |
| setuppromoter | https://galaxy.pasteur.fr/tool_runner?tool_id=toolshed.pasteur.fr/repos/fmareuil/promoteur | HTTP 404 |
| BioSWITCH | https://github.com/CBigOxf/BioSWITCH | HTTP 404 |
| mixNBHMM | https://github.com/plbaldoni/mixNBHMM | HTTP 404 |
| methylscaper | https://github.com/rhondabacher/acmethylscaper | HTTP 404 |
| MatrixMotif | https://peterslab.org/downloads.php | HTTP 404 |
| rSeqTU-A | https://s18692001.github.io/rSeqTU/ | HTTP 404 |
| SiTaR | https://sbi.hki-jena.de/sitar/index.php | HTTP 404 |
| SEQSIM | https://sites.ualberta.ca/~joyramie/SEQSIM.html | HTTP 404 |
| NaviSE | https://sourceforge.net/projects/navise-superenhancer/ | HTTP 404 |
| BIDCHIPS | https://www.perkinslab.ca/software | HTTP 404 |
| gCUP | https://www.uni-due.de/~hy0546/gCUP/ | HTTP 410 |

## Unreachable (283)

Not asserted as dead. Two runs on different days should agree before treating any of these as gone.

| Tool | URL | Detail |
| --- | --- | --- |
| iCYP-MFE | http://103.130.219.193:5002 | ConnectTimeout |
| mscDPB | http://121.5.71.120/mscDPB/ | ConnectTimeout |
| iPromoter-Seqvec | http://124.197.54.240:5001 | ConnectTimeout |
| GeNOSA | http://140.113.239.45/GeNOSA/ | ConnectTimeout |
| CRSD | http://140.120.213.10:8080/crsd/main/home.jsp | ConnectTimeout |
| COMAN | http://147.8.185.62/COMAN/ | ConnectTimeout |
| MoD Tools, Web Weeder | http://159.149.160.51/modtools/ | ConnectTimeout |
| PhysMPrePro | http://202.207.14.87:8032/bioinformation/PhysMPrePro/index.asp | ConnectionError |
| iCR | http://210.212.215.199/icr/index.html | ConnectTimeout |
| DeepPromise | http://DeepPromise.erc.monash.edu/ | ConnectTimeout |
| P-SCAN | http://abs.cit.nih.gov/pscan/ | ConnectionError |
| Allegro | http://acgt.cs.tau.ac.il/allegro/ | ConnectionError |
| ModEnt | http://acgt.cs.tau.ac.il/modent/ | ConnectionError |
| TDTHub | http://acrab.cnb.csic.es/TDTHub/ | ConnectTimeout |
| ALGGEN | http://alggen.lsi.upc.es/ | ConnectTimeout |
| SPACER | http://allostery.bii.a-star.edu.sg/ | ReadTimeout |
| WikiGene | http://andromeda.gsf.de/wiki | ConnectionError |
| JasparDB | http://api.bioinfo.no/wsdl/JasparDB.wsdl | ConnectionError |
| Jaspar WS | http://api.bioinfo.no/wsdl/Jaspar_webservice_0.2.wsdl | ConnectionError |
| ASAP | http://asap.binf.ku.dk/Asap/Home.html | ConnectionError |
| Sequence Searcher | http://athena.bioc.uvic.ca/virology-ca-tools/sequence-searcher/ | ConnectionError |
| VGO | http://athena.bioc.uvic.ca/virology-ca-tools/vgo/ | ConnectionError |
| BayesMD | http://bayesmd.binf.ku.dk/ | ConnectionError |
| Phyloscan | http://bayesweb.wadsworth.org/phyloscan/ | ConnectionError |
| GeneNetFinder | http://bclab.inha.ac.kr/GeneNetFinder/ | ConnectTimeout |
| jPREdictor | http://bibiserv.techfak.uni-bielefeld.de/jpredictor/ | ConnectionError |
| DeepGenGrep | http://bigdata.biocie.cn/deepgengrep/home | ConnectionError |
| CABERNET | http://bimib.disco.unimib.it/index.php/CABERNET | ConnectTimeout |
| MicroFootPrinter | http://bio.cs.washington.edu/MicroFootPrinter.html | ConnectionError |
| BioBIKE | http://biobike.csbc.vcu.edu/ | ConnectionError |
| Footer | http://biodev.hgen.pitt.edu/Footer/ | ConnectionError |
| SEME | http://biogpu.ddns.comp.nus.edu.sg/~chipseq/SEME/ | ConnectionError |
| CENTDIST | http://biogpu.ddns.comp.nus.edu.sg/~chipseq/webseqtools2/TASKS/Motif_Enrichment/submit.php | ConnectionError |
| LASAGNA-Search | http://biogrid-lasagna.engr.uconn.edu/lasagna_search/ | ConnectionError |
| SeqSite | http://bioinfo.au.tsinghua.edu.cn/software/seqsite/ | ConnectionError |
| Animal Transcription Factor Database | http://bioinfo.life.hust.edu.cn/AnimalTFDB/ | ConnectionError |
| FFLtool | http://bioinfo.life.hust.edu.cn/FFLtool/ | ConnectionError |
| hTFtarget | http://bioinfo.life.hust.edu.cn/hTFtarget | ConnectionError |
| TFM-Explorer | http://bioinfo.lifl.fr/TFM | ConnectTimeout |
| IRESPred | http://bioinfo.net.in/IRESPred/ | ConnectTimeout |
| MicroInspector | http://bioinfo.uni-plovdiv.bg/microinspector/ | ConnectTimeout |
| BPAC | http://bioinfo.wilmer.jhu.edu/BPAC/ | ConnectTimeout |
| MultiBind | http://bioinfo3d.cs.tau.ac.il/MultiBind | ConnectionError |
| ChromaSig | http://bioinformatics-renlab.ucsd.edu/rentrac/wiki/ChromaSig | ConnectTimeout |
| INSECT | http://bioinformatics.ibioba-mpsp-conicet.gov.ar/INSECT2/ | SSLError |
| Mammalian Promoter Database (MPromDb) | http://bioinformatics.wistar.upenn.edu/MPromDb/ | ConnectionError |
| PAP | http://bioinformatics.wustl.edu/webTools/portalModule/PromoterSearch.do | ConnectionError |
| ProMateus | http://bioportal.weizmann.ac.il/promate/ | ConnectTimeout |
| rMotif | http://bioportal.weizmann.ac.il/~lapidotm/rMotif/html/ | ConnectTimeout |
| MotifViz | http://biowulf.bu.edu/MotifViz/ | ConnectionError |
| PromoSer | http://biowulf.bu.edu/zlab/PromoSer/ | ConnectionError |
| seqMINER | http://bips.u-strasbg.fr/seqminer/tiki-index.php | ConnectionError |
| PlantNATsDB | http://bis.zju.edu.cn/pnatdb/ | ReadTimeout |
| BiologicalNetworks | http://brak.sdsc.edu/pub/BiologicalNetworks/ | ConnectionError |
| REDUCE | http://bussemaker.bio.columbia.edu/reduce/ | ConnectTimeout |
| CATCH | http://catch.cmbi.ru.nl | ConnectionError |
| MOST+ | http://cbb.sjtu.edu.cn/~ccwei/pub/software/MOST/MOST.php | ConnectionError |
| IBM Bioinformatics and Pattern Discovery Group | http://cbcsrv.watson.ibm.com/Tspd.html | ConnectTimeout |
| Promoter | http://cbs.dtu.dk/services/Promoter/ | ConnectionError |
| Gibbs Motif Sampler | http://ccmbweb.ccv.brown.edu/gibbs/gibbs.html | ConnectTimeout |
| CEAS | http://ceas.cbi.pku.edu.cn | ConnectionError |
| cgNA+web | http://cgDNAweb.epfl.ch | ConnectTimeout |
| AnnoMiner | http://chimborazo.ibdm.univ-mrs.fr/AnnoMiner/ | ConnectTimeout |
| iRegNet | http://chromatindynamics.snu.ac.kr:8082/iRegNet_main | ConnectionError |
| WordSpy | http://cic.cs.wustl.edu/wordspy/ | ConnectionError |
| DESSO-DB | http://cloud.osubmi.com/DESSO/ | ConnectionError |
| CCAT | http://cmb.gis.a-star.edu.sg/ChIPSeq/paperCCAT.htm | ConnectionError |
| regCNN | http://cobisHSS0.im.nuk.edu.tw/regCNN/ | ConnectionError |
| Human IRES Atlas | http://cobishss0.im.nuk.edu.tw/Human_IRES_Atlas/ | ConnectionError |
| Tn-Core | http://combo.dbe.unifi.it/tncore | ConnectTimeout |
| CompareProspector | http://compareprospector.stanford.edu/ | ConnectionError |
| BELT | http://compbio.uthscsa.edu/BELT_Web/ | ConnectTimeout |
| W-ChIPMotifs | http://compbio.uthscsa.edu/ChIPMotifs/ | ConnectTimeout |
| W-ChIPeaks | http://compbio.uthscsa.edu/W-ChIPeaks/ | ConnectTimeout |
| HRTBLDb | http://compbio.uthscsa.edu/hrtbldb/ | ConnectTimeout |
| ES-ARCNN | http://compgenomics.utsa.edu/ES-ARCNN/ | ConnectionError |
| CSA | http://compubio.csu.edu.cn | ConnectTimeout |
| CONREAL | http://conreal.niob.knaw.nl/ | ConnectionError |
| COUGER | http://couger.oit.duke.edu | ConnectionError |
| DMINDA | http://csbl.bmb.uga.edu/DMINDA/ | ConnectTimeout |
| BoBro | http://csbl.bmb.uga.edu/~maqin/motif_finding/ | ConnectTimeout |
| DBD2BS | http://dbd2bs.csie.ntu.edu.tw/ | ConnectionError |
| DeepBlue Epigenomic Data Server | http://deepblue.mpi-inf.mpg.de/ | ConnectionError |
| DOMINO | http://domino.cs.tau.ac.il | ConnectionError |
| Enhort | http://enhort.mni.thm.de | ConnectionError |
| ePIANNO | http://epianno.stat.sinica.edu.tw/index.html | ConnectionError |
| EpiGRAPH | http://epigraph.mpi-inf.mpg.de/WebGRAPH/ | ConnectionError |
| ASIAN | http://eureka.cbrc.jp/asian/ | ConnectionError |
| BART | http://faculty.virginia.edu/zanglab/bart/ | ReadTimeout |
| XG-m7G | http://flagship.erc.monash.edu/XG-m7G/ | ConnectionError |
| FLyOde | http://flyode.boun.edu.tr | TooManyRedirects |
| FMSClusterFinder | http://fmsclusterfinder.fmsbiog.com | ConnectionError |
| MAGIA2 | http://gencomp.bio.unipd.it/magia2/start/ | ConnectTimeout |
| SCOPE | http://genie.dartmouth.edu/scope/ | ConnectionError |
| CisMiner | http://genome.ugr.es:9000/cisminer | ConnectionError |
| ReadOut | http://gibk26.bio.kyutech.ac.jp/jouhou/readout/ | ConnectionError |
| GINsim | http://ginsim.org/ | ConnectionError |
| BEARR | http://giscompute.gis.a-star.edu.sg/~vega/BEARR1.0/ | ConnectionError |
| Animal-eRNAdb | http://gong_lab.hzau.edu.cn/Animal-eRNAdb/ | SSLError |
| GPMiner | http://gpminer.mbc.nctu.edu.tw/ | ConnectionError |
| CLNN-loop | http://hwclnn.sdu.edu.cn/ | ConnectTimeout |
| ImitateDB | http://imitatedb.sblab-nsit.net | ConnectionError |
| BSDD | http://iris.physics.iisc.ernet.in/bsdd/ | ConnectionError |
| TACT | http://jbirc.jbic.or.jp/tact/ | ConnectTimeout |
| Key Pathway Miner | http://keypathwayminer.compbio.sdu.dk/ | ConnectionError |
| kmer-SVM | http://kmersvm.beerlab.org | SSLError |
| iNuc-PseKNC | http://lin.uestc.edu.cn/server/iNuc-PseKNC | ConnectionError |
| LISE | http://lise.ibms.sinica.edu.tw | ConnectTimeout |
| MACS | http://liulab.dfci.harvard.edu/MACS/ | ConnectTimeout |
| NPS | http://liulab.dfci.harvard.edu/NPS/ | ConnectTimeout |
| DGW | http://lukauskas.co.uk/dgw/ | ConnectionError |
| Target Explorer | http://luna.bioc.columbia.edu/Target_Explorer/ | ConnectTimeout |
| MALBoost | http://malboost.bi.up.ac.za | ConnectTimeout |
| PMSearch | http://mcube.nju.edu.cn/jwang/lab/soft/PMS/home.html | ReadTimeout |
| QuEST | http://mendel.stanford.edu/sidowlab/downloads/quest/ | ConnectionError |
| Meta-MEME | http://metameme.sdsc.edu/ | ConnectionError |
| GeneSet2miRNA | http://mips.helmholtz-muenchen.de/proj/gene2mir/ | ConnectTimeout |
| miRNAmotif | http://mirnamotif.ibch.poznan.pl | ConnectionError |
| MKT | http://mkt.uab.es | ConnectTimeout |
| MoAn | http://moan.binf.ku.dk/ | ConnectionError |
| Clarion | http://monash.bioweb.cloud.edu.au/Clarion/ | ConnectionError |
| CONFAC | http://morenolab.whitehead.emory.edu/cgi-bin/confac/login.pl | ConnectTimeout |
| BML | http://motif.t-ridership.com/ | ConnectionError |
| MotifCut 0.1 beta | http://motifcut.stanford.edu/ | ConnectionError |
| GWAS4D | http://mulinlab.tmu.edu.cn/gwas4d | ConnectTimeout |
| Netview | http://netview.tigem.it/netview_project/netview_tools.html | ConnectionError |
| NPLB | http://nplb.ncl.res.in/ | ConnectTimeout |
| PromPredict | http://nucleix.mbu.iisc.ernet.in/prompredict/prompredict.html | ConnectionError |
| NUCwave | http://nucleosome.usal.es/nucwave/ | ConnectionError |
| PBSword | http://pbs.rnet.missouri.edu | ConnectionError |
| RSAT - Retrieve Sequence | http://pedagogix-tagc.univ-mrs.fr/rsat/retrieve-seq_form.cgi | ConnectTimeout |
| PIQ | http://piq.csail.mit.edu/ | ConnectTimeout |
| PlantTFcat | http://plantgrn.noble.org/PlantTFcat/ | ConnectionError |
| PlantPAN | http://plantpan2.itps.ncku.edu.tw/ | ConnectTimeout |
| REGENOMICS | http://plantregeneration.snu.ac.kr/regenomics/?species=Ath | ReadTimeout |
| PlnTFDB | http://plntfdb.bio.uni-potsdam.de/ | ConnectTimeout |
| PlantTFDB | http://plntfdb.bio.uni-potsdam.de/v1.0/ | ConnectTimeout |
| PoSSuM | http://possum.cbrc.jp/PoSSuM/ | ConnectionError |
| PredictProtein Open | http://ppopen.informatik.tu-muenchen.de/ | ConnectionError |
| EAT-Rice | http://predictor.nchu.edu.tw/EAT-Rice | ConnectTimeout |
| PocketAnnotate | http://proline.biochem.iisc.ernet.in/pocketannotate/ | ConnectionError |
| PromoterCAD | http://promotercad.org/ | ConnectionError |
| PromoterPlot | http://promoterplot.fmi.ch/ | ConnectionError |
| PsyMuKB | http://psymukb.net | ConnectionError |
| QBiC-Pred | http://qbic.genome.duke.edu | ConnectionError |
| SemanticBI | http://qianglab.scst.suda.edu.cn/semantic/ | ConnectionError |
| SemanticCS | http://qianglab.scst.suda.edu.cn/semanticCS/ | ConnectionError |
| RegulonDB | http://regulondb.ccg.unam.mx/ | ConnectionError |
| RNAWRE | http://rnawre.bio2db.com | ConnectTimeout |
| SiteSeer | http://rocky.bms.umist.ac.uk/SiteSeer/ | ConnectTimeout |
| RSAT retrieve matrix | http://rsat-tagc.univ-mrs.fr/rsat/retrieve-matrix_form.cgi | ConnectTimeout |
| RSAT retrieve-ensembl-seq | http://rsat.sb-roscoff.fr/retrieve-ensembl-seq_form.cgi | ConnectionError |
| Ingeneue | http://rusty.fhl.washington.edu/ingeneue/index.html | ConnectTimeout |
| Samscope | http://samscope.dna.bio.keio.ac.jp/ | ConnectTimeout |
| cWords | http://servers.binf.ku.dk/cwords/ | ConnectionError |
| MutaNET | http://service.bioinformatik.uni-saarland.de/mutanet/ | ConnectTimeout |
| TFmiR2 | http://service.bioinformatik.uni-saarland.de/tfmir2 | ConnectTimeout |
| DeFuse | http://shahlab.ca/projects/defuse/ | ConnectionError |
| SITEHOUND-web | http://sitehound.sanchezlab.org | ConnectionError |
| HTHmotif | http://stormo.wustl.edu/HTHmotif | ConnectionError |
| Magma | http://stormo.wustl.edu/Magma/ | ConnectionError |
| PhyloNet | http://stormo.wustl.edu/PhyloNet/ | ConnectionError |
| ScerTF | http://stormo.wustl.edu/ScerTF/ | ConnectionError |
| PromFD | http://stormo.wustl.edu/src/PromFD/ | ConnectionError |
| STREAM | http://stream.imb.uq.edu.au/ | ConnectionError |
| ProDFace | http://structbioinfo.iitj.ac.in/resources/bioinfo/pd_interface/ | ConnectionError |
| ChIPSummitDB | http://summit.med.unideb.hu/summitdb/ | ConnectTimeout |
| iTAR | http://syslab3.nchu.edu.tw/iTAR/ | ConnectionError |
| MAPanalyzer | http://systbio.cau.edu.cn/mappred/ | ConnectTimeout |
| BDdb | http://t21omics.cngb.org | ConnectTimeout |
| RSAT dyad-analysis | http://teaching.rsat.eu/dyad-analysis_form.cgi | ReadTimeout |
| RSAT oligo-analysis | http://teaching.rsat.eu/oligo-analysis_form.cgi | ReadTimeout |
| RSAT position-analysis | http://teaching.rsat.eu/position-analysis_form.cgi | ReadTimeout |
| TransFind | http://transfind.sys-bio.net/ | ConnectionError |
| T-Reg Comparator | http://treg.molgen.mpg.de/ | ConnectionError |
| UPObase | http://upobase.bioinformaticsreview.com | ReadTimeout |
| visGReMLIN | http://vagner.dti.ufv.br/visgremlin4 | ConnectTimeout |
| Vernal | http://vernal.cs.mcgill.ca | ConnectionError |
| HIPPIE | http://wanglab.pcbi.upenn.edu/hippie/ | ConnectionError |
| BSCM2TDb | http://webtom.cabgrid.res.in/BSCM2TDb | ConnectionError |
| SCMVTDb | http://webtom.cabgrid.res.in/scmvtdb/ | ConnectionError |
| YMF 3.0 | http://wingless.cs.washington.edu/YMF/YMFWeb/YMFInput.pl | ConnectionError |
| PRI-CAT | http://www.ab.wur.nl/pricat | ConnectTimeout |
| AthaMap | http://www.athamap.de/ | ConnectTimeout |
| LnCeCell | http://www.bio-bigdata.net/LnCeCell/ | ReadTimeout |
| POXO | http://www.bioinfo.biocenter.helsinki.fi/poxo | ConnectionError |
| sRNATargetDigger | http://www.bioinfolab.cn/sRNATD.html | ConnectTimeout |
| SeqBox | http://www.bioinformatica.unito.it/reproducibile.bioinformatics.html | ConnectionError |
| DeepHLAPred | http://www.biolscience.cn/DeepHLApred/ | ConnectTimeout |
| Enhancer-LSTMAtt | http://www.biolscience.cn/Enhancer-LSTMAtt/ | ConnectTimeout |
| BioMaster | http://www.biomaster-uestc.cn | ConnectionError |
| TSSer | http://www.clipz.unibas.ch/downloads/TSSer/index.php | ConnectTimeout |
| SraTailor | http://www.devbio.med.kyushu-u.ac.jp/sra_tailor/ | ConnectTimeout |
| INCLUSive | http://www.esat.kuleuven.ac.be/inclusive | SSLError |
| TOUCAN 2 | http://www.esat.kuleuven.ac.be/~saerts/software/toucan.php | SSLError |
| Drosophila DNase I footprint database | http://www.flyreg.org/ | ConnectTimeout |
| GeneProf | http://www.geneprof.org/GeneProf/ | ConnectTimeout |
| INTERFEROME | http://www.interferome.org/ | ConnectTimeout |
| iPromoter-5mC | http://www.jci-bioinfo.cn/iPromoter-5mC | ConnectionError |
| Parseq | http://www.lcqb.upmc.fr/parseq/ | SSLError |
| NOBAI | http://www.manet.uiuc.edu/nobai/nobai.php | ConnectionError |
| MotifRegressor | http://www.math.umass.edu/~conlon/mr.html | ConnectTimeout |
| HLungDB | http://www.megabionet.org/bio/hlung/ | ConnectionError |
| miRFFLDB | http://www.mirffldb.in | ConnectionError |
| trans-PCO | http://www.networks-liulab.org/transPCO | ConnectionError |
| ORegAnno | http://www.oreganno.org/ | ConnectionError |
| Predicted Prokaryotic Regulatory Proteins (P2RP) | http://www.p2rp.org/index.php?PHPSESSID=a025bb831c57e0ec4c48933ac0685725 | ConnectTimeout |
| PAZAR | http://www.pazar.info/ | ConnectTimeout |
| ProdoNet | http://www.prodonet.tu-bs.de | ConnectionError |
| Promzea | http://www.promzea.org | ConnectionError |
| ModuleMaster | http://www.ra.cs.uni-tuebingen.de/software/ModuleMaster/welcome_e.html | ConnectionError |
| RegulomePA | http://www.regulome.pcyt.unam.mx | ConnectionError |
| RevUP | http://www.revup-classifier.ca | ConnectTimeout |
| EPDRNA | http://www.s-bioinformatics.cn/epdrna | ConnectTimeout |
| Treegl | http://www.sailing.cs.cmu.edu/main/?page_id=495 | ConnectionError |
| SEProm | http://www.scfbio-iitd.res.in/software/SEProm_Data_TSS.jsp | SSLError |
| SeqAcademy | http://www.seqacademy.org/ | ConnectionError |
| PromH | http://www.softberry.com/berry.phtml?topic=promhg&group=programs&subgroup=promoter | ConnectTimeout |
| TopoGSA | http://www.topogsa.net | ConnectionError |
| Precise | http://www.wageningenur.nl/en/show/PRECISE-Prediction-of-REgulatory-CISacting-Elements.htm | ConnectionError |
| eccDB | http://www.xiejjlab.bio/eccDB | ConnectionError |
| MiRfold | http://wwwabi.snv.jussieu.fr/research/publi/small_ncRNA/ | ConnectTimeout |
| ARGO | http://wwwmgs.bionet.nsc.ru/mgs/programs/argo/ | SSLError |
| RECON | http://wwwmgs.bionet.nsc.ru/mgs/programs/recon/ | SSLError |
| SITECON | http://wwwmgs.bionet.nsc.ru/mgs/programs/sitecon/ | SSLError |
| rSNP_Guide | http://wwwmgs.bionet.nsc.ru/mgs/systems/rsnp/ | SSLError |
| CASAVA | http://zhanglabtools.org/CASAVA | ConnectionError |
| m5CPred-SVM | http://zhulab.ahu.edu.cn/m5CPred-SVM | ConnectTimeout |
| CARRIE | http://zlab.bu.edu/CARRIE-web | ConnectionError |
| ICSF | http://zlab.bu.edu/ICSF/ | ConnectionError |
| Cluster Buster | http://zlab.bu.edu/cluster-buster/ | ConnectionError |
| Possum | http://zlab.bu.edu/~mfrith/possum/ | ConnectionError |
| 4DGenome | https://4dgenome.research.chop.edu | ConnectionError |
| ConnecTF | https://ConnecTF.org | ConnectTimeout |
| CDBProm | https://aw.iimas.unam.mx/cdbprom/ | SSLError |
| miRStart 2.0 | https://awi.cuhk.edu.cn/~miRStart2 | SSLError |
| agReg-SNPdb | https://azifi.tz.agrar.uni-goettingen.de/agreg-snpdb | SSLError |
| agReg-SNPdb-Plants | https://azifi.tz.agrar.uni-goettingen.de/agreg-snpdb-plants/ | SSLError |
| Bipartite Motif Finder | https://bmf.soedinglab.org | ConnectionError |
| TALE-NT | https://boglab.plp.iastate.edu/ | SSLError |
| CBNplot | https://cbnplot.com | ConnectionError |
| PredictiveNetworks | https://compbio.dfci.harvard.edu/predictivenetworks// | ConnectTimeout |
| WheatCRISPR | https://crispr.bioinfo.nrc.ca/WheatCrispr/ | ReadTimeout |
| CSI NGS Portal | https://csibioinfo.nus.edu.sg/csingsportal | ReadTimeout |
| DEEPCYPs | https://deepcyps.idruglab.cn/ | SSLError |
| Depicter | https://depicter.erc.monash.edu/ | ConnectTimeout |
| DNA Readout Viewer | https://drv.brc.hu | SSLError |
| BoxShade | https://embnet.vital-it.ch/software/BOX_form.html | ConnectionError |
| ENTRAF | https://entraf.iimas.unam.mx | SSLError |
| EpiAlignment | https://epialign.ucsd.edu/ | SSLError |
| EvoPrinter | https://evoprinter.ninds.nih.gov/evoprintprogramHD/evphd.html | ConnectionError |
| Expansin Engineering Database | https://exed.biocatnet.de | SSLError |
| RLBase | https://gccri.bishop-lab.uthscsa.edu/rlbase/ | ConnectionError |
| DExTER | https://gite.lirmm.fr/menichelli/DExTER | ConnectTimeout |
| MCOT | https://gitlab.sysbio.cytogen.ru/academiq/mcot-kernel | SSLError |
| nASAP | https://grobase.top/nasap/ | SSLError |
| HeRA | https://hanlab.uth.edu/HeRA/ | ConnectTimeout |
| MethMotif Toolkit | https://methmotif.org | ConnectTimeout |
| Multioviz | https://multioviz.ccv.brown.edu/ | SSLError |
| MyPROSLE | https://myprosle.genyo.es/ | SSLError |
| Nebula | https://nebula.curie.fr/ | ConnectionError |
| CisCross | https://plamorph.sysbio.ru/ciscross/ | ConnectTimeout |
| proChIPdb | https://prochipdb.org | ConnectionError |
| SalMotifDB | https://salmobase.org/apps/SalMotifDB/ | ConnectionError |
| SciApps | https://sciapps.org/ | ConnectionError |
| iMARGI | https://sysbio.ucsd.edu/imargi_pipeline | ConnectTimeout |
| TarpiD | https://tarpid.nitrkl.ac.in/tarpid_db/ | ReadTimeout |
| FIRE | https://tavazoielab.c2b2.columbia.edu/FIRE/ | SSLError |
| TEISER | https://tavazoielab.c2b2.columbia.edu/TEISER/ | SSLError |
| DeepBind | https://tools.genes.toronto.edu/deepbind/ | ConnectTimeout |
| TRIPBASE | https://tripbase.iis.sinica.edu.tw/ | ConnectionError |
| NetVenn | https://wheat.pw.usda.gov/NetVenn/ | ConnectionError |
| CHiCP | https://www.chicp.org/ | SSLError |
| TissueNexus | https://www.diseaselinks.com/TissueNexus/ | SSLError |
| FABIAN-variant | https://www.genecascade.org/fabian/ | ConnectTimeout |
| MuGVRE | https://www.multiscalegenomics.eu/ | SSLError |
| ePOSSUM | https://www.mutationdistiller.org/ePOSSUM2/index.html | ConnectTimeout |
| motifeR | https://www.omicsolution.org/wukong/motifeR | ConnectionError |
| cGRNB | https://www.scbit.org/cgrnb/ | ConnectionError |
| Plant_SNP_TATA_Z-tester | https://www.sysbio.ru/Plant_SNP_TATAdb/ | SSLError |
| VOMBAT | https://www2.informatik.uni-halle.de:8443/VOMBAT/faces/pages/choose.jsp | ConnectTimeout |
| CellNetAnalyzer | https://www2.mpi-magdeburg.mpg.de/projects/cna/cna.html | SSLError |
| ZincBind | https://zincbind.bioinf.org.uk/ | ConnectTimeout |
