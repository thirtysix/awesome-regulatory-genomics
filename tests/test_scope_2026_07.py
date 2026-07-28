"""The 2026-07-28 scope widening: methylation, 3D genome, histone, MPRA, QTL.

Widening a boundary is where a catalog quietly becomes a different catalog, so
each new area is pinned from both sides: a real in-scope record that must be
admitted, and the neighbouring field that shares its vocabulary and must not be.

Every rejection case below is a record that was actually admitted during
development and had to be excluded afterwards.
"""
import pytest

from config import (CATEGORY_KEYS, STRONG_OPERATIONS, TEXT_CATEGORY,
                    WEAK_OPERATIONS)
from select_domain import classify


def rec(name="X", description="", operations=(), topics=()):
    return {"name": name, "description": description,
            "function": [{"operation": [{"term": t} for t in operations]}],
            "topic": [{"term": t} for t in topics]}


def admitted(**kw):
    return classify(rec(**kw))[0] is not None


# ---------------------------------------------------------------------------
# the five new categories exist and are assignable
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("key", ["dna-methylation", "chromatin-3d", "histone-marks",
                                 "reporter-assays", "molecular-qtl"])
def test_new_category_is_defined_and_has_text_rules(key):
    assert key in CATEGORY_KEYS
    assert TEXT_CATEGORY.get(key), f"{key} has no text rule, so nothing lands in it"


# ---------------------------------------------------------------------------
# DNA methylation, and the two fields that share the word
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("desc", [
    "Analysing differentially methylated regions from WGBS data",
    "Context-aware alignment of bisulfite sequencing reads",
    "A reference methylome database for different organisms",
    "Discovery of regulatory regions from Bis-seq data",          # MethylSeekR
])
def test_dna_methylation_is_admitted(desc):
    assert admitted(description=desc), desc


def test_rna_modification_is_excluded():
    """m6A/m5C work is epitranscriptomics, a different field.

    Twelve such records were in the catalog before this pass and left with it.
    """
    for desc in ["TRESS is a tool for detecting m6A methylation regions from MeRIP-seq",
                 "A novel method for predicting m5C sites of RNA",
                 "Prediction of RNA pseudouridine sites"]:
        assert not admitted(description=desc), desc


def test_protein_methylation_is_excluded():
    """MethK: "identifying methylated lysines on histones and non-histone proteins".

    It mentions histones, so without the hard exclusion it rides in on the
    histone pattern. It is a post-translational-modification predictor.
    """
    assert not admitted(
        name="MethK",
        description="Web server for identifying methylated lysines on histones "
                    "and non-histone proteins")


def test_a_dna_modification_that_mentions_6mA_still_gets_in():
    """Bacterial 6mA is a DNA modification, not an RNA one.

    This is why the RNA exclusion is SOFT: a strong DNA-methylation phrase has
    to be able to override it, or nanodisco is lost.
    """
    assert admitted(
        name="nanodisco",
        description="A toolbox for de novo discovery of all three types of DNA "
                    "methylation (6mA, 5mC, 4mC) and bacterial methylome analysis")


# ---------------------------------------------------------------------------
# 3D genome
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("desc", [
    "Stochastic modeling of molecular contacts from DNA loop extrusion",   # MoDLE
    "Identification of topologically associating domains",
    "Calls chromatin loops and A/B compartments",
])
def test_unambiguous_3d_vocabulary_admits_on_its_own(desc):
    """Phrases a genome-assembly paper would never use."""
    assert admitted(description=desc), desc


@pytest.mark.parametrize("desc", [
    "Resolution enhancement of Hi-C data with a deep convolutional network",  # HiCNN
    "Coverage based normalization of Hi-C and capture Hi-C data",             # covNorm
])
def test_bare_hi_c_needs_a_corroborating_topic(desc):
    """Hi-C is a technology, not a field, and assembly uses it heavily.

    Putting bare "Hi-C" in the strong tier admitted "A high-quality genome
    sequence of alkaligrass", a genome-announcement paper that used Hi-C to
    scaffold. The real 3D tools all carry a domain topic, so nothing was lost
    by demoting it.
    """
    assert not admitted(description=desc), f"should need a topic: {desc}"
    assert admitted(description=desc, topics=["Chromosome conformation capture"])


@pytest.mark.parametrize("desc", [
    "A high-quality genome sequence of alkaligrass provides insights into "
    "halophyte stress tolerance, assembled with chromosome conformation capture",
    "A chromosome-level genome assembly of the Atlantic salmon",
])
def test_genome_announcement_papers_are_excluded(desc):
    """These are not tools. They reach the sweep because scaffolding an
    assembly now routinely uses chromosome conformation capture."""
    assert not admitted(description=desc), desc


# ---------------------------------------------------------------------------
# molecular QTL
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("desc", [
    "eQTL mediation analysis with efficient permutation testing",
    "An integrative resource for quantitative trait loci across human molecular traits",
    "Discovering eQTLs with single-cell RNA-seq data",
    "Integration of multiple GWAS and omics QTL summary statistics",       # Primo
])
def test_molecular_qtl_is_admitted(desc):
    assert admitted(description=desc), desc


# ---------------------------------------------------------------------------
# the operation terms that were tried and withdrawn
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("term", ["Loop modelling", "Gene expression QTL analysis",
                                  "Bisulfite mapping"])
def test_the_withdrawn_operations_never_admit_on_their_own(term):
    """Tried in STRONG, then in WEAK, and removed from both.

    bio.tools attaches `Loop modelling` to RNA secondary structure and protein
    conformation, `Gene expression QTL analysis` to expression atlases, and
    `Bisulfite mapping` to general-purpose commercial suites. Even topic
    corroboration was not enough, because the domain topics are applied
    liberally. Admission for these areas comes from text.
    """
    assert term not in STRONG_OPERATIONS
    assert term not in WEAK_OPERATIONS
    assert not admitted(description="A general analysis platform.",
                        operations=[term],
                        topics=["Transcription factors and regulatory sites"])


@pytest.mark.parametrize("name,desc", [
    ("Rascore", "Defining an expanded RAS conformational landscape based on structures"),
    ("ZFIN", "Central repository and web-based resource for zebrafish genetic data"),
    ("CLC Main Workbench", "De novo and reference assembly, SNP and small indel detection"),
])
def test_the_records_those_operations_dragged_in_stay_out(name, desc):
    assert not admitted(name=name, description=desc,
                        operations=["Loop modelling", "Bisulfite mapping",
                                    "Gene expression QTL analysis"],
                        topics=["Transcription factors and regulatory sites"])


# ---------------------------------------------------------------------------
# already-in-scope areas that only gained a category
# ---------------------------------------------------------------------------
def test_reporter_assays_were_already_in_scope():
    """MPRA and STARR-seq were strong patterns before this pass.

    Nothing was rejected for them, so this change is a category and not a
    widening. The test exists so a later tidy-up of the patterns does not
    silently drop them.
    """
    assert admitted(description="Massively parallel reporter assay analysis")
    assert admitted(description="starrpeaker calls peaks from STARR-seq data")


def test_histone_marks_admit_on_the_mark_nomenclature():
    assert admitted(description="Predicts condition-specific enhancers from H3K27ac ChIP-seq")
    assert admitted(description="Chromatin state segmentation from histone modification data")
