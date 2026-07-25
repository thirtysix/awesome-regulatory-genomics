"""Shared configuration: harvest vocabulary, category taxonomy, paths.

Everything that defines *what the catalog is* lives here, so the scope of the
resource can be audited and changed in one place.
"""
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
]

# Queried but deliberately NOT used to admit records, because bio.tools applies
# them to a different field entirely:
#   "Peak detection"                     -> mass spectrometry / chromatography
#   "DNA-binding protein prediction"     -> protein-function prediction, not TFBS
#   "Nucleic acids-binding site prediction" -> protein structure annotation
#   "Protein-nucleic acid binding prediction"
# Auditing these is what keeps the catalog from silently absorbing 200
# metabolomics tools.
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
]

# bio.tools records that are unambiguously in scope but that no operation,
# topic or free-text query reaches - their annotations place them somewhere
# else entirely (MAST under "Transcriptomics", ARACNe under "Systems biology",
# HaploReg under "Pathology"). Fetched directly by ID and admitted without
# passing the selection filter, since each has been checked by hand.
# Prefer this over duplicating a tool in seeds.yaml: the metadata, publication
# and citation count still come from upstream and stay fresh.
SEED_BIOTOOLS_IDS = [
    "mast",           # MEME Suite motif scanner
    "aracne",         # network inference
    "atsnp",          # variant effect on TF binding
    "HaploReg",       # regulatory annotation of variants
    "uniprobe",       # PBM-derived DNA-binding specificities
]

# Free-text queries, for tools whose EDAM annotation is wrong or absent.
# bio.tools' ``q=`` searches name + description, so this recovers records like
# FIMO (annotated "Genotyping") that no operation query can reach.
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
}

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
]

# Hard exclusions applied after every other rule. These catch neighbouring
# fields that share vocabulary ("motif", "peak", "binding") but are not
# regulatory genomics.
EXCLUDE_TEXT_PATTERNS = [
    r"\bmass spectrometr|\bLC-MS\b|\bMS/MS\b|\bmetabolomic|\bglycomic|\bproteomic workflow",
    r"\bchromatograph",
    r"\bprotein (crystall|folding|structure prediction)",
    r"\bRNA (secondary |tertiary )?structure",
    r"\briboswitch|\bribosome profiling",
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
    ("nucleosome-chromatin", "Nucleosome & chromatin state",
     "Nucleosome positioning, chromatin accessibility and chromatin-state segmentation."),
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
                             r"\bopen chromatin", r"\bhistone modification"],
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
REGISTRY_HOSTS = {
    "bioconductor.org": "bioconductor",
    "pypi.org": "pypi",
    "cran.r-project.org": "cran",
    "anaconda.org": "conda",
    "hub.docker.com": "docker",
    "galaxyproject.org": "galaxy",
}
