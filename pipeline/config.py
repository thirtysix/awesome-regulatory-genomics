"""Shared configuration: harvest vocabulary, category taxonomy, paths.

Everything that defines *what the catalog is* lives here, so the scope of the
resource can be audited and changed in one place.
"""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW = DATA / "raw"
CACHE = DATA / "cache"
CURATION = ROOT / "curation"
DOCS = ROOT / "docs"

BIOTOOLS_API = "https://bio.tools/api/tool/"
OPENALEX_API = "https://api.openalex.org/works"
GITHUB_API = "https://api.github.com"

# ---------------------------------------------------------------------------
# Contact address for the API "polite pools"
# ---------------------------------------------------------------------------
# OpenAlex and Crossref give faster, more reliable service to clients that
# identify themselves, and ask for a contact address to do it. It is not a
# credential, but it is a personal detail, so it is configured rather than
# hard-coded: set CONTACT_EMAIL in the environment or in a local .env file.
#
# Unset is fine. Every caller omits the mailto parameter entirely rather than
# sending a placeholder, since a fake address in the polite pool is worse than
# no address at all.


def _load_dotenv() -> None:
    """Read a local .env if present. Deliberately no python-dotenv dependency."""
    path = ROOT / ".env"
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


_load_dotenv()
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "").strip()


def user_agent(tool: str = "awesome-regulatory-genomics/1.0") -> str:
    """User-Agent string, with a contact address only if one is configured."""
    base = f"{tool} (+https://github.com/thirtysix/awesome-regulatory-genomics"
    return f"{base}; mailto:{CONTACT_EMAIL})" if CONTACT_EMAIL else f"{base})"


def polite_params(params: dict | None = None) -> dict:
    """Add OpenAlex/Crossref `mailto` when configured, and nothing when not."""
    out = dict(params or {})
    if CONTACT_EMAIL:
        out["mailto"] = CONTACT_EMAIL
    return out

# ---------------------------------------------------------------------------
# Harvest vocabulary
# ---------------------------------------------------------------------------
# bio.tools' ``operation=`` search is a fuzzy text match, not an ontology
# lookup: querying "Enhancer prediction" returns tools annotated with
# "Exonic splicing enhancer prediction". So we query broadly and then filter on
# the operation terms a record actually carries (KEEP_OPERATIONS below). Query
# recall and result precision are deliberately separate steps.

QUERY_OPERATIONS = [
    # motif
    "Sequence motif recognition",
    "Sequence motif discovery",
    "Sequence motif comparison",
    "Sequence motif analysis",
    # transcription-factor binding and regulatory elements
    "Transcription factor binding site prediction",
    "Transcriptional regulatory element prediction",
    "cis-regulatory element prediction",
    "trans-regulatory element prediction",
    "Regulatory element prediction",
    "Promoter prediction",
    "DNA binding site prediction",
    "Phylogenetic footprinting",
    # chromatin
    "Peak calling",
    "Differential binding analysis",
    "Nucleosome position prediction",
    # networks
    "Gene regulatory network analysis",
    "Gene regulatory network prediction",
    # methylation, 3D genome and QTL, added with the 2026-07-28 scope widening
    "Methylation calling",
    "Methylation analysis",
    "Gene methylation analysis",
    "Bisulfite mapping",
    "Loop modelling",
    "Gene expression QTL analysis",
]

# Operation terms that look in-domain but are NOT queried and never admit
# anything, because bio.tools applies them to a different field entirely:
#   "Peak detection"                        -> mass spectrometry / chromatography.
#                                              Of the 204 records carrying it,
#                                              roughly three in four are
#                                              proteomics, metabolomics or NMR.
#   "DNA-binding protein prediction"        -> protein-function prediction, not TFBS
#   "Nucleic acids-binding site prediction" -> protein structure annotation
#   "Protein-nucleic acid binding prediction"      -> likewise
#   "Protein-nucleic acid binding site analysis"   -> likewise
#
# This list is documentation, not control flow: nothing imports it. The
# exclusion is enforced by these terms being absent from STRONG_OPERATIONS,
# WEAK_OPERATIONS and QUERY_OPERATIONS. Keep it in sync with those three, since
# it is the record of *why* they are absent - which is what keeps someone from
# helpfully adding "Peak detection" and absorbing 200 metabolomics tools.
REJECTED_OPERATIONS = [
    "Peak detection",
    "DNA-binding protein prediction",
    "Nucleic acids-binding site prediction",
    "Protein-nucleic acid binding prediction",
    "Protein-nucleic acid binding site analysis",
]

# Topic queries. Operations describe what a tool *does* and are frequently
# wrong; topics describe what it is *about* and are applied more reliably. This
# pass is what reaches HOCOMOCO ("Data handling"), SICER ("Sequence
# contamination filtering") and ChIP-Atlas ("Genome assembly") - records no
# operation query can see. Only tight domain topics are listed: "Gene
# expression" and "RNA-Seq" match thousands of off-domain tools and hit the
# API's result cap.
QUERY_TOPICS = [
    "Transcription factors and regulatory sites",
    "DNA binding sites",
    "Gene regulation",
    "ChIP-seq",
    "Epigenomics",
    "Chromosome conformation capture",
    "Methylated DNA immunoprecipitation",
]

# bio.tools records that are unambiguously in scope but that no operation,
# topic or free-text query reaches - their annotations place them somewhere
# else entirely (MAST under "Transcriptomics", ARACNe under "Systems biology",
# HaploReg under "Pathology"). Fetched directly by ID and admitted without
# passing the selection filter, since each has been checked by hand.
# Prefer this over duplicating a tool in seeds.yaml: the metadata, publication
# and citation count still come from upstream and stay fresh.
SEED_BIOTOOLS_IDS = [
    "aracne",         # network inference
    "atsnp",          # variant effect on TF binding
    "HaploReg",       # regulatory annotation of variants
    "uniprobe",       # PBM-derived DNA-binding specificities

    # Surfaced by the harder benchmark tier (2026-07-28). Each record was
    # opened and read before being added: probing bio.tools by NAME offered
    # eight, and three were different tools wearing the same name. `Thor` is a
    # spatial-transcriptomics package, not the RGT differential peak caller;
    # `inps` and `maestro` are protein-stability predictors, not the nucleosome
    # and single-cell tools. Those three are absent from bio.tools and belong
    # in seeds.yaml instead. These five are the genuine articles.
    "danpos",         # nucleosome position dynamics
    "dbsuper",        # super-enhancer database
    "ggseqlogo",      # sequence logos in ggplot2
    "logolas",        # enrichment/depletion logo plots
    "rgreat",         # GREAT region-enrichment from R

    # Reviewed individually after the adjudication pass over the reject pile.
    # Each is in scope but phrased so idiosyncratically that no pattern reaches
    # it without dragging in a neighbouring field ("Genomic loci annotation and
    # enrichment tool", "Quantitative analysis of the genomic overlaps",
    # "A tool for exploring patterns in ChIP profiling data"). Listing them by
    # ID is honest about that: a human decided, and the metadata still comes
    # from upstream and stays fresh.
    "4d-nucleome-data-portal",
    "ChiCMaxima",
    "GLANET",
    "RSAT_-_Retrieve_Sequence",
    "abs",
    "bisa",
    "catch",
    "chrogps",
    "chrokit",
    "chromegcn",
    "citrus",
    "cobind",
    "conquer",
    "couger",
    "decorate",
    "deepfun",
    "deeptools",
    "driverpower",
    "echolocator",
    "enhort",
    "episegmix",
    "ermer",
    "es-arcnn",
    "evoaug_tf",
    "filer",
    "filtercontrol",
    "funcisnp",
    "funsip",
    "genomesidekick",
    "greap",
    "grenits",
    "infima",
    "ipro-gan",
    "jaspar2018",
    "lolaweb",
    "lpnet",
    "makestatschipseq",
    "meme",
    "mira_single-cell",
    "motifbreakr",
    "niacs",
    "ntw",
    "owas",
    "p53mutagene",
    "racipe",
    "readout",
    "remm",
    "remus-disease",
    "rispice",
    "rsat-retrieve-ensembl-seq",
    "simsearch",
    "snapshot",
    "sparkinferno",
    "suldex",
    "swissregulon",
    "tadeus2",
    "targetgene",
    "varadb",
    "w-chipeaks",
    "svmil2",

    # Dual-purpose or boilerplate-burdened records confirmed by a second
    # adjudication pass against the tightened rules.
    "x2k",            # upstream TF networks from ChIP-seq + PWMs; also does
                      # kinase enrichment, which the hard exclusions catch.
                      # Its sibling record x2k_web is admitted on text, so
                      # excluding this one made the catalog self-inconsistent.
]

# Free-text queries, for tools whose EDAM annotation is wrong or absent.
# bio.tools' ``q=`` searches name + description, so this recovers records that
# no operation query can reach: peak callers like gcapc, Q, CCAT and MixChIP
# carry no usable operation at all.
QUERY_FREETEXT = [
    "transcription factor binding site",
    "TFBS",
    "position weight matrix",
    "sequence motif",
    "motif enrichment",
    "regulatory element",
    "cis-regulatory",
    "enhancer prediction",
    "promoter analysis",
    "DNase footprinting",
    "ATAC-seq footprint",
    "ChIP-seq peak",
    "CUT&RUN",
    "gene regulatory network",
    "transcription factor database",
    "chromatin accessibility",
]

# Selection is tiered, because EDAM terms differ wildly in how reliably
# bio.tools applies them.
#
# STRONG - the term is specific enough that carrying it is sufficient.
# Deliberately excluded as over-broad: "Binding site prediction" (parent term,
# also covers ligand and metal sites), "Protein binding site prediction",
# "RNA binding site prediction", "Network analysis", "Pathway or network
# prediction", and all methylation operations.
STRONG_OPERATIONS = {
    "Transcription factor binding site prediction",
    "Transcriptional regulatory element prediction",
    "cis-regulatory element prediction",
    "trans-regulatory element prediction",
    "Regulatory element prediction",
    "Promoter prediction",
    "DNA binding site prediction",
    "Sequence motif discovery",
    "Motif discovery",
    "Sequence motif comparison",
    "Peak calling",
    "Differential binding analysis",
    "Nucleosome position prediction",
    "Nucleosome formation or exclusion sequence prediction",
    "Gene regulatory network analysis",
    "Gene regulatory network prediction",
    "Gene co-expression network analysis",
    # Added 2026-07-28 with the scope widening. Only these two survived the
    # first run: they name the DNA assay itself and nothing else uses them.
    "Methylation calling",
    "Gene methylation analysis",
}

# WEAK - genuinely in-domain terms that bio.tools also applies to protein
# motifs, RNA structural motifs and nanopore methylation. Carrying one admits a
# record only alongside a supporting topic or text signal.
WEAK_OPERATIONS = {
    "Sequence motif recognition",
    "Sequence motif analysis",
    "Structural motif discovery",
    # bio.tools attaches these to orthology and phylogenetics tools
    # (OrtholugeDB, SwiftOrtho, Broccoli, PhyloPars) far more often than to
    # actual comparative regulatory analysis.
    "Phylogenetic footprinting",
    "Phylogenetic footprinting / shadowing",
    # "Methylation analysis" is applied to RNA m6A and protein PTM work as well
    # as to DNA, so it needs a corroborating topic or text signal.
    "Methylation analysis",
    # These three were tried in STRONG on 2026-07-28 and demoted the same hour,
    # because the first run showed what bio.tools actually attaches them to:
    #
    #   "Loop modelling"              -> RNA secondary-structure loops
    #                                    (CRISPRtracrRNA) and protein
    #                                    conformational landscapes (Rascore),
    #                                    not only chromatin loops.
    #   "Gene expression QTL analysis" -> expression atlases and model-organism
    #                                    databases (ZFIN, Mouse Atlas of Gene
    #                                    Expression, SAGE), not QTL methods.
    #   "Bisulfite mapping"           -> general-purpose commercial suites that
    #                                    list every assay they support (CLC
    #                                    Main Workbench, Genedata Expressionist).
    #
    # A domain topic turned out to be too weak a corroboration for these:
    # bio.tools applies "Transcription factors and regulatory sites" and
    # "Epigenomics" liberally, so topic-corroboration alone still admitted ZFIN,
    # the Mouse Atlas of Gene Expression, CLC Main Workbench and a RAS protein
    # conformation tool. They are therefore not admitted by operation at all;
    # the STRONG text patterns (bisulfite, methylome, Hi-C, eQTL) reach every
    # genuine case on their own, which was verified by removing these and
    # checking that nothing real was lost.
}

KEEP_OPERATIONS = STRONG_OPERATIONS | WEAK_OPERATIONS

# EDAM topics that corroborate a weak operation or a text-only match.
DOMAIN_TOPICS = {
    "Transcription factors and regulatory sites",
    "Gene regulation",
    "Gene transcription",
    "Gene transcripts",
    "Gene expression",
    "ChIP-seq",
    "Epigenetics",
    "Epigenomics",
    "Chromatin architecture",
    "Sequence sites, features and motifs",
    "Functional, regulatory and non-coding RNA",
    "DNA binding sites",
    "ChIP-on-chip",
    "Chromosome conformation capture",
    "Methylated DNA immunoprecipitation",
    "DNA methylation",
}

# STRONG text patterns: phrases so specific to this field that a match settles
# the question on its own. These admit a record with no topic corroboration,
# and they also OVERRIDE the hard exclusions below - a transcription-factor
# database that happens to mention phylogenetic trees, or a multi-omics
# regulatory resource that mentions proteomics, is still in scope.
# Ordering matters: exclusions still beat a STRONG EDAM *operation* (bio.tools
# assigns those wrongly), but they lose to a STRONG text match (which describes
# what the tool actually does).
STRONG_TEXT_PATTERNS = [
    r"\btranscription[- ]factor",
    r"\bTFBS\b|\bTF binding\b",
    r"\bcis-regulatory|\bregulatory element|\bcis-element",
    r"\bgene regulatory network|\bregulatory network|\bregulon\b",
    r"\bpromoter\b|\benhancer\b|\bsuper-?enhancer",
    r"\bposition (weight|frequency|specific scoring) matri|\bPWM\b|\bPFM\b|\bPSSM\b",
    r"\bsequence logo|\bsequence motifs?\b|\bmotifs? in DNA|\bDNA (sequence )?motif",
    r"\bmotif (discovery|enrichment|scan|search|find|analysis)|\bdiscriminative .{0,12}motif",
    r"\bChIP[- ]?(seq|chip|exo|nexus)\b|\bCUT&(RUN|Tag)\b",
    r"\bpeak[- ]call(er|ing)?\b|\bcalls? peaks\b",
    r"\bfootprint",
    r"\bchromatin (accessibilit|state|loop|interaction|organi[sz]ation)|\bopen[- ]chromatin",
    r"\bsc(ATAC|-ATAC)|\bsingle[- ](cell|nucleus) ATAC|\bsingle[- ]cell (epigenom|regulom)",
    r"\bmassively parallel reporter|\bMPRA\b|\bSTARR-?seq",
    r"\btranscription start site|\bCAGE\b",
    r"\bHiChIP\b|\bChIA-?PET\b|\bCapture-?C\b|\btopologically associat|\bCTCF\b",
    r"\b(non-?coding|regulatory) (variant|mutation|SNP)",
    r"\bDNA[- ]binding (site|preference|specificit|profile|domain)",
    r"\bnucleosome",
    r"\bepigenom(e|ic)s?\b",
    # Added 2026-07-28. DNA methylation: every term here is DNA-specific.
    # Deliberately NOT bare "methylation", which protein PTM and RNA m6A work
    # use just as freely; those are soft-excluded below and lose to these.
    r"\bbisulfite\b|\bWGBS\b|\bRRBS\b|\bmethylome\b|\bmethyl-?seq\b|\bB[iS]S?-?seq\b",
    r"\bDNA methylation|\bdifferentially methylated|\bDMRs?\b|\bDMPs?\b",
    r"\bCpG (island|site|methylation|dinucleotide)|\bmethylation (calling|caller)",
    # 3D genome. NOT bare "Hi-C": the assay is used just as heavily to scaffold
    # genome assemblies, and putting it here admitted "A high-quality genome
    # sequence of alkaligrass". Hi-C stays in KEEP_TEXT_PATTERNS, where a
    # domain topic has to corroborate it; "Chromosome conformation capture" is
    # a domain topic, so the real 3D tools still arrive. What is listed here is
    # only vocabulary that genome-assembly papers do not use.
    r"\bmicro-?C\b|\bchromosome conformation capture\b|\b[3-5]C-seq\b",
    r"\bchromatin (loop|contact|interaction)|\bA/B compartment|\bloop calling",
    r"\bloop extrusion|\b(molecular|omics) QTL",
    # Molecular QTL.
    r"\b[a-z]{1,3}QTLs?\b|\bexpression quantitative trait|\bquantitative trait loc",
    # Histone marks. The mark nomenclature (H3K27ac) is decisive; bare
    # "histone methylation" is not, because that is also a protein PTM task.
    r"\bH[1-4](K|R)\d+(me|ac|ub|ph)\d*\b|\bhistone (mark|modification|variant|acetylation)",
]

# Records that fail the operation filter are still kept if their name or
# description matches one of these AND they carry a domain topic. This is the
# escape hatch for bio.tools' annotation gaps, and it is what recovers tools
# like gcapc, Q and CCAT that no ontology query can reach.
KEEP_TEXT_PATTERNS = [
    r"\btranscription factor binding site",
    r"\bTFBS\b",
    r"\bposition (weight|frequency|specific scoring) matri",
    r"\bPWM\b|\bPFM\b|\bPSSM\b",
    r"\bsequence motif",
    r"\bmotif (discovery|enrichment|scan|search|find)",
    r"\bcis-regulatory\b",
    r"\bregulatory element",
    r"\benhancer (prediction|identification|activity)",
    r"\bpromoter (prediction|analysis|identification)",
    r"\b(DNase|ATAC)[- ]?(seq )?footprint",
    r"\bChIP[- ]?(seq|exo|nexus)\b.*\bpeak",
    r"\bpeak call",
    r"\bCUT&(RUN|Tag)\b",
    r"\bgene regulatory network",
    r"\bregulon\b",
    r"\bchromatin accessibilit",
    r"\b(TF|transcription[- ]factor|DNA|protein-DNA)[- ]binding site",
    r"\bsequence logo",
    r"\bChIP[- ]?(seq|exo|nexus|on-chip)\b",
    r"\b(ChIP )?peak annotat",
    r"\bChIP peak",
    r"\btranscription(al)? regulat",
    r"\bhistone modification",
    r"\benriched (domain|region)s?\b",
    r"\bDNA[- ]binding (preference|specificit|profile)",

    # --- gaps found by the adjudication pass over the reject pile -----------
    # Each of these classes was systematically missed: the tools are squarely
    # in scope but were phrased in vocabulary no earlier pattern covered.

    # chromatin state, segmentation and epigenome annotation (ChromHMM, STAN,
    # Segtools, EpiSegMix, ChAsE)
    r"\bchromatin state|\bgenome segmentation|\bgenomic segmentation",
    r"\bepigenom(e|ic)s?\b",
    r"\bheterochromatin|\bnucleosome (position|stability)",

    # single-cell regulatory genomics (SCALE, SnapATAC, epiScanpy, APEC, MIRA)
    r"\bsc(ATAC|-ATAC)|\bsingle[- ](cell|nucleus) ATAC",
    r"\bsingle[- ]cell (epigenom|regulom|open[- ]chromatin|chromatin)",
    r"\bopen[- ]chromatin",

    # reporter assays (MPRA, STARR-seq)
    r"\bmassively parallel reporter|\bMPRA\b|\bSTARR-?seq",

    # transcription start sites (TSRexploreR, TSSr, EPD, TE-TSS)
    r"\btranscription start site|\bTSS\b|\bCAGE\b",

    # transcription factors as objects of study, not only their binding sites
    # (TFcheckpoint, TF-Marker, PlantTFDB, CoryneRegNet, ChEA3)
    r"\btranscription[- ]factor|\btranscription factors\b",
    r"\btranscriptional regulat|\bco-?factors? .{0,20}(bound|binding|genomic)",

    # promoters and enhancers named plainly
    r"\bpromoter\b|\benhancer\b|\bsuper-?enhancer|\bcis-element",

    # regulatory variant interpretation (TURF, TVAR, ReMM, VannoPortal)
    r"\b(non-?coding|regulatory) (variant|mutation|SNP|element)",
    r"\bvariant (annotation|prioriti[sz]ation).{0,30}(regulat|epigenom|chromatin)",
    r"\ballele-?specific binding",

    # 3D genome, where the interaction IS the regulatory link (HiChIP, Capture-C,
    # promoter-distal loops, CTCF loops, TADs)
    r"\bchromatin (loop|interaction|organi[sz]ation|contact)",
    r"\bHi-?C\b|\bChIA-?PET\b|\bHiChIP\b|\bCapture-?C\b",
    r"\btopologically associat|\bTADs?\b|\bCTCF\b",
    r"\benhancer[- ](promoter|target|gene) (interaction|link)",

    # peak calling phrased without the word "peak call"
    r"\bpeak[- ]call(er|ing)?\b|\benriched (genomic )?regions?\b",
]

# HARD exclusions: the phrase names another field's core object, so it wins even
# against a STRONG text match. "protein sequence motifs" contains "sequence
# motifs" and would otherwise admit protein-motif viewers like 3Matrix.
HARD_EXCLUDE_PATTERNS = [
    r"\bprotein (sequence )?motif|\bmotifs? (with)?in proteins|\bstructural motif",
    # Protein and peptide work uses the same vocabulary as DNA motif analysis:
    # "position weight matrix", "sequence logo" and "motif discovery" are as
    # common in one as the other. Without these, the strong-text tier admits
    # SLiMFinder, PeSA, GibbsCluster, pftools and the antimicrobial-peptide
    # classifiers, all of which a scope reviewer flagged.
    r"\bshort linear motif|\bSLiMs?\b",
    r"\bpeptides?\b",
    r"\bcatalytic site|\bactive site\b",
    r"\bamino[- ]acid (motif|pattern|sequence|composition)",
    r"\bprotein (profile|family|residue|disorder)s?\b",
    r"\bleucine[- ]rich repeat|\bLRR\b",
    r"\bantibacterial|\bantimicrobial|\bantifungal",
    r"\bRNA[- ]binding protein|\bRBPs?\b",
    r"\bcircular RNA|\bcircRNA",
    r"\bRNA (sequence and structure|structure|secondary structure) motif",
    r"\bRNA[- ]binding data",
    # Protein-side residue prediction: DNA tools speak of binding *sites*,
    # protein-structure tools of binding *residues*.
    r"\bbinding residues?\b",
    r"\bRNA (tertiary|structural|secondary) motif",
    r"\bmass spectrometr|\bLC-MS\b|\bMS/MS\b|\bmetabolomic|\bglycomic",
    r"\bchromatograph|\bflow injection analysis",
    r"\brestriction enzyme",
    r"\briboswitch|\bribosome profiling",
    r"\bPROSITE\b|\bHAMAP\b|\bPfam\b|\bInterPro\b",
    r"\bphosphorylat|\bkinase substrate",
    r"\bprotein (crystall|folding|structure prediction)",
    r"\bdocking\b|\bmolecular dynamics",
    r"\bMHC (class )?(I|II)\b|\bepitope\b",
    r"\bG-?quadruplex|\bQGRS\b",
    r"\bexosom|\bmicrobiome",
    r"\bretroposon|\bretrotransposon",
    r"\bviral taxonom",
    r"\bortholog(y|ue|s)? (inference|prediction|assignment|classifier)",
    # Protein methylation is a post-translational-modification task and shares
    # every word with DNA methylation. MethK ("identifying methylated lysines
    # on histones and non-histone proteins") is the case that matters: it would
    # otherwise ride in on the histone pattern.
    r"\bmethylated lysine|\blysine (methylation|acetylation) site|\bPTM site",
    # Genome-announcement papers, which are not tools at all. They reach the
    # sweep because chromosome conformation capture is now routinely used to
    # scaffold an assembly, so "A high-quality genome sequence of alkaligrass"
    # matched a 3D-genome phrase. The give-away is in the opening clause.
    r"\bhigh[- ]quality .{0,25}genome (sequence|assembly)",
    r"\bchromosome[- ]?(level|scale) .{0,15}(genome )?(assembly|sequence)",
]

# SOFT exclusions: the phrase merely suggests another field and can legitimately
# co-occur with in-scope work, so a STRONG text match overrides it. A
# transcription-factor database is not disqualified by mentioning a
# phylogenetic tree, nor a regulatory multi-omics resource by listing
# proteomics among its data types.
EXCLUDE_TEXT_PATTERNS = [
    r"\bRNA (secondary |tertiary )?structure",
    r"\bstructural variant|\bcopy[- ]number variant call",
    r"\bphylogenetic tree|\bspecies tree|\bmultiple sequence alignment tool",
    r"\bdocking\b|\bmolecular dynamics",
    # protein/RNA motif work shares the word "motif" but is a different field
    r"\bPROSITE\b|\bHAMAP\b|\bPfam\b|\bInterPro\b",
    r"\bHMM profile|\bprofile HMM|\bhidden Markov model.{0,20}protein",
    r"\bamino acid (motif|pattern)|\bprotein (motif|pattern|domain) (search|discovery|database)",
    r"\bunaligned protein sequence",
    # other vocabulary collisions
    r"\brestriction enzyme",
    r"\bretroposon|\bretrotransposon|\btransposable element",
    r"\bflow injection analysis",
    r"\bmetabolic pathway (map|database)",
    r"\bMHC (class )?(I|II)\b|\bepitope\b|\bimmunogenic",
    r"\bG-?quadruplex|\bQGRS\b",
    r"\bmiRNA[- ]target|\bmicroRNA target",
    r"\bexosom",
    r"\bCRISPR (screen|guide|repeat|array)|\bsgRNA design",
    r"\ballele[- ]specific copy number|\bASCN\b",
    r"\bpathway (map|enrichment) database|\bKyoto Encyclopedia",
    r"\bgeneral[- ]purpose (sequence|genomic) analysis (suite|platform)",
    r"\bprotein (sequence )?motif|\bmotifs? (with)?in proteins",
    r"\bphosphorylat|\bkinase substrate",
    r"\bortholog(y|ue|s)? (inference|prediction|assignment|classifier)|\bortholog(y|ue) predictions",
    r"\bRNA (tertiary|structural|secondary) motif",
    r"\bviral taxonom|\btelomeric motif|\bmicrobiome",
    r"\blow complexity protein",
    # RNA modification is a neighbouring field using the same word. Soft
    # rather than hard on purpose: bacterial 6mA is a DNA modification, so a
    # tool calling both (nanodisco) must still be admitted by the DNA-specific
    # strong patterns above, which beat this.
    r"\bepitranscriptom|\bRNA methylation|\bm6A\b|\bm5C\b|\bpseudouridin",
]

# ---------------------------------------------------------------------------
# Category taxonomy
# ---------------------------------------------------------------------------
# Each category is (key, label, description). A tool may hold several.
# Assignment order matters only for choosing the *primary* category (first hit).
CATEGORIES = [
    ("motif-discovery", "Motif discovery",
     "De novo discovery of sequence motifs from sets of sequences or peaks."),
    ("motif-scanning", "Motif scanning & enrichment",
     "Scanning sequences with known matrices; motif enrichment and over-representation."),
    ("motif-comparison", "Motif comparison & visualisation",
     "Comparing, clustering, aligning and drawing motifs and logos."),
    ("motif-databases", "Motif & TF databases",
     "Curated collections of binding profiles, TF families and TF-target relationships."),
    ("tfbs-prediction", "TFBS prediction",
     "Predicting transcription-factor binding sites, including sequence-based ML models."),
    ("regulatory-elements", "Promoter & enhancer prediction",
     "Prediction and annotation of promoters, enhancers and other cis-regulatory elements."),
    ("reporter-assays", "Reporter assays",
     "MPRA, STARR-seq and other massively parallel tests of regulatory activity."),
    ("footprinting", "Footprinting",
     "DNase/ATAC digital footprinting and phylogenetic footprinting."),
    ("peak-calling", "Peak calling",
     "Calling enriched regions from ChIP-seq, ATAC-seq, CUT&RUN and related assays."),
    ("peak-annotation", "Peak annotation & differential binding",
     "Annotating peaks to genes/features and testing differential occupancy."),
    ("chip-resources", "ChIP/ATAC data resources",
     "Portals and databases of processed binding and accessibility experiments."),
    ("grn-inference", "Gene regulatory networks",
     "Inferring and analysing TF-target networks and regulons."),
    ("regulatory-variants", "Regulatory variant effect",
     "Assessing the impact of sequence variants on binding and regulatory activity."),
    ("molecular-qtl", "Molecular QTL",
     "eQTL, caQTL and related mapping of variants to regulatory phenotypes."),
    ("nucleosome-chromatin", "Nucleosome & chromatin state",
     "Nucleosome positioning, chromatin accessibility and chromatin-state segmentation."),
    ("histone-marks", "Histone modifications",
     "Histone marks, super-enhancers and chromatin-state segmentation from histone data."),
    ("chromatin-3d", "3D genome & chromatin interactions",
     "Hi-C, HiChIP and ChIA-PET; loops, TADs, compartments and enhancer-promoter contacts."),
    ("dna-methylation", "DNA methylation",
     "Methylation calling, differential methylation and methylome resources."),
    ("single-cell", "Single-cell regulatory genomics",
     "Single-cell ATAC/multiome and single-cell regulatory network methods."),
    ("comparative", "Comparative & evolutionary",
     "Cross-species conservation and evolution of regulatory sequence."),
]
CATEGORY_KEYS = [c[0] for c in CATEGORIES]
CATEGORY_LABEL = {c[0]: c[1] for c in CATEGORIES}
CATEGORY_DESC = {c[0]: c[2] for c in CATEGORIES}

# EDAM operation -> categories
OP_CATEGORY = {
    "Sequence motif discovery": ["motif-discovery"],
    "Motif discovery": ["motif-discovery"],
    "Structural motif discovery": ["motif-discovery"],
    "Sequence motif recognition": ["motif-scanning"],
    "Sequence motif analysis": ["motif-scanning"],
    "Sequence motif comparison": ["motif-comparison"],
    "Transcription factor binding site prediction": ["tfbs-prediction"],
    "DNA binding site prediction": ["tfbs-prediction"],
    "Nucleic acids-binding site prediction": ["tfbs-prediction"],
    "Protein-nucleic acid binding prediction": ["tfbs-prediction"],
    "Protein-nucleic acid binding site analysis": ["tfbs-prediction"],
    "DNA-binding protein prediction": ["tfbs-prediction"],
    "Transcriptional regulatory element prediction": ["regulatory-elements"],
    "cis-regulatory element prediction": ["regulatory-elements"],
    "trans-regulatory element prediction": ["regulatory-elements"],
    "Regulatory element prediction": ["regulatory-elements"],
    "Promoter prediction": ["regulatory-elements"],
    "Phylogenetic footprinting": ["footprinting", "comparative"],
    "Phylogenetic footprinting / shadowing": ["footprinting", "comparative"],
    "Peak calling": ["peak-calling"],
    "Peak detection": ["peak-calling"],
    "Differential binding analysis": ["peak-annotation"],
    "Nucleosome position prediction": ["nucleosome-chromatin"],
    "Nucleosome formation or exclusion sequence prediction": ["nucleosome-chromatin"],
    "Gene regulatory network analysis": ["grn-inference"],
    "Gene regulatory network prediction": ["grn-inference"],
    "Gene co-expression network analysis": ["grn-inference"],
    "Methylation calling": ["dna-methylation"],
    "Methylation analysis": ["dna-methylation"],
    "Gene methylation analysis": ["dna-methylation"],
    "Bisulfite mapping": ["dna-methylation"],
    "Loop modelling": ["chromatin-3d"],
    "Gene expression QTL analysis": ["molecular-qtl"],
}

# Regex applied to "name. description" -> extra categories.
TEXT_CATEGORY = {
    "motif-discovery": [r"\bde novo motif", r"\bmotif (discovery|finding|finder)", r"\bdiscover(s|y of)? motifs"],
    "motif-scanning": [r"\bmotif (scan|search|match)", r"\bscan(s|ning)? .{0,30}(motif|matri|PWM)",
                       r"\bmotif enrichment", r"\bover-?represent\w+ .{0,20}motif"],
    "motif-comparison": [r"\bmotif (comparison|similarity|clustering|alignment)", r"\bsequence logo",
                         r"\blogo (plot|generat)"],
    "motif-databases": [r"\b(database|collection|repository|catalog(ue)?) of .{0,40}"
                        r"(motif|binding (profile|site)|transcription factor)",
                        r"\b(PWM|PFM|PSSM|binding profile)s? (database|collection|library)"],
    "tfbs-prediction": [r"\btranscription factor binding site", r"\bTFBS\b", r"\bTF binding\b",
                        r"\bbinding (site|affinity) predict"],
    "regulatory-elements": [r"\b(promoter|enhancer|silencer|insulator) (prediction|identification|discovery)",
                            r"\bcis-regulatory (module|element)", r"\bCRM\b", r"\bregulatory element"],
    "footprinting": [r"\b(digital |DNase |ATAC[- ]?)footprint", r"\bfootprinting\b"],
    "peak-calling": [r"\bpeak call", r"\bcalls? peaks\b", r"\benriched regions?\b"],
    "peak-annotation": [r"\bpeak annotat", r"\bdifferential (binding|occupancy|peak)",
                        r"\bannotat\w+ .{0,20}peaks", r"\bnearest (gene|TSS)"],
    "chip-resources": [r"\b(database|atlas|portal|compendium|resource) of .{0,40}(ChIP|ATAC|DNase)",
                       r"\bChIP-seq (data)?(base|sets? collection|atlas)"],
    "grn-inference": [r"\bgene regulatory network", r"\bregulatory network (infer|reconstruct|predict)",
                      r"\bregulon\b", r"\bGRN\b"],
    "regulatory-variants": [r"\b(SNP|SNV|variant|mutation)s? .{0,40}(binding|motif|regulatory)",
                            r"\bmotif.?break", r"\bregulatory variant", r"\bnon-?coding variant"],
    "nucleosome-chromatin": [r"\bnucleosome", r"\bchromatin (accessibilit|state|segmentation)",
                             r"\bopen chromatin"],
    "histone-marks": [r"\bH[1-4](K|R)\d+(me|ac|ub|ph)\d*\b",
                      r"\bhistone (mark|modification|variant|acetylation|methylation)",
                      r"\bsuper-?enhancer", r"\bchromatin[- ]state segmentation", r"\bChromHMM\b"],
    "chromatin-3d": [r"\bloop extrusion", r"\bHi-?C\b", r"\bmicro-?C\b", r"\bHiChIP\b", r"\bChIA-?PET\b",
                     r"\bcapture[- ]?C\b", r"\b[3-5]C-seq\b", r"\bchromosome conformation",
                     r"\btopologically associat|\bTADs?\b", r"\bchromatin (loop|contact|interaction)",
                     r"\bA/B compartment", r"\benhancer-?promoter (loop|contact|interaction)"],
    "dna-methylation": [r"\bDNA methylation", r"\bbisulfite\b|\bB[iS]S?-?seq\b", r"\bWGBS\b|\bRRBS\b",
                        r"\bmethylome\b", r"\bdifferentially methylated|\bDMRs?\b",
                        r"\bCpG (island|site|methylation)", r"\bmethylation (call|profil|array)"],
    "molecular-qtl": [r"\b[a-z]{1,3}QTLs?\b", r"\b(molecular|omics) QTL", r"\bexpression quantitative trait",
                      r"\bquantitative trait loc"],
    "reporter-assays": [r"\bMPRA\b", r"\bSTARR-?seq", r"\bmassively parallel reporter",
                        r"\breporter assay", r"\blentiMPRA\b"],
    "single-cell": [r"\bsingle[- ]cell", r"\bscATAC", r"\bsnATAC", r"\bscRNA.{0,20}regulat", r"\bmultiome"],
    "comparative": [r"\b(cross|inter)[- ]species", r"\bcomparative genomic", r"\bconservation of .{0,30}regulat",
                    r"\bevolution(ary)? .{0,30}(regulat|motif|binding)"],
}

# Topic-derived categories (EDAM topic term -> category)
TOPIC_CATEGORY = {
    "ChIP-seq": ["peak-calling"],
    "Epigenomics": ["nucleosome-chromatin"],
    "Epigenetics": ["nucleosome-chromatin"],
    "Transcription factors and regulatory sites": ["tfbs-prediction"],
    "Gene regulatory networks": ["grn-inference"],
    "Molecular interactions, pathways and networks": [],
    "Chromosome conformation capture": ["chromatin-3d"],
    "Methylated DNA immunoprecipitation": ["dna-methylation"],
    "DNA methylation": ["dna-methylation"],
}

# Database-ish tool types promote a tool into the *-databases/resources buckets.
DB_TOOLTYPES = {"Database portal", "Bioinformatics portal", "Web API"}

# ---------------------------------------------------------------------------
# Repo resolution
# ---------------------------------------------------------------------------
CODE_HOSTS = {
    "github.com": "github",
    "gitlab.com": "gitlab",
    "bitbucket.org": "bitbucket",
    "sourceforge.net": "sourceforge",
    "codeberg.org": "codeberg",
    "r-forge.r-project.org": "r-forge",
    "git.bioconductor.org": "bioconductor",
}
# Shared repositories that hold hundreds of unrelated tools. A member of one of
# these does NOT have its own repository, and treating the monorepo as its
# source hands the tool the whole project's stars, activity, licence and
# language. bio.tools points hgv_pass at github.com/galaxyproject/galaxy, which
# made a small Galaxy wrapper the most-starred entry in this catalog at 1,818
# stars; nucleosome_prediction picked up 123 stars from bgruening/galaxytools
# the same way.
#
# The tool may still be real and in scope. It simply has no repository of its
# own, and saying so is more honest than crediting it with someone else's.
MONOREPOS = {
    "galaxyproject/galaxy",
    "galaxyproject/tools-iuc",
    "bgruening/galaxytools",
    "bioconda/bioconda-recipes",
    "biocontainers/containers",
    "nf-core/modules",
    "snakemake/snakemake-wrappers",
    "broadinstitute/gatk",
    "ncbi/sra-tools",
}

# The publication equivalent of MONOREPOS: platform and suite papers that are
# never one tool's own, however few catalog members happen to link them.
#
# build.py already blanks a publication claimed as primary by three or more
# tools, but that counter keys on the IDENTIFIER, and the same paper is reachable
# as both a PMID and a DOI. Bioconductor is `pmid:25633503` for 23 records and
# `doi:10.1038/nmeth.3252` for TransView, so the DOI-flavoured copy tallied 1,
# slid under the threshold, and gave TransView the Bioconductor paper's 4,023
# citations and 12th place in the catalog. Galaxy splits the same way
# (`pmid:27137889` for 13 records, `doi:10.1093/nar/gkw343` for two), which put
# two Galaxy wrappers at 2,343 apiece.
#
# List every identifier a paper is reachable by, not just the common one.
SUITE_PUBLICATIONS = {
    # Bioconductor
    "pmid:25633503", "doi:10.1038/nmeth.3252",
    # Galaxy
    "pmid:27137889", "doi:10.1093/nar/gkw343",
    # a Galaxy/workflow F1000Research poster carried by 16 records
    "doi:10.7490/f1000research.1114334.1",
    # EMBOSS, plus its administrator and developer guides
    "doi:10.1016/S0168-9525(00)02024-2",
    "doi:10.1017/CBO9781139151399", "doi:10.1017/CBO9781139151405",
    # nf-core
    "pmid:32055031",
}

REGISTRY_HOSTS = {
    "bioconductor.org": "bioconductor",
    "pypi.org": "pypi",
    "cran.r-project.org": "cran",
    "anaconda.org": "conda",
    "hub.docker.com": "docker",
    "galaxyproject.org": "galaxy",
}
