"""select_domain.classify() - what is in scope.

This function decides the boundary of the entire resource, and every case below
is a bug that actually shipped. The ordering of its rules is load-bearing and
not obvious, so each ordering decision gets its own test: reversing any of them
either readmits a neighbouring field wholesale or rejects a flagship tool.
"""
import pytest

from select_domain import classify


def rec(name="ToolX", description="", operations=(), topics=()):
    """A bio.tools record, in the shape the API actually returns."""
    return {
        "name": name,
        "description": description,
        "function": [{"operation": [{"term": t} for t in operations]}],
        "topic": [{"term": t} for t in topics],
    }


# ---------------------------------------------------------------------------
# the tiers
# ---------------------------------------------------------------------------
def test_strong_operation_admits_alone():
    tier, reason = classify(rec(operations=["Transcription factor binding site prediction"]))
    assert tier == "core"
    assert reason.startswith("operation:")


def test_weak_operation_needs_corroboration():
    """A weak operation on its own is not enough.

    bio.tools applies `Sequence motif recognition` to protein and RNA motif
    tools as freely as to DNA ones, so admitting on it alone pulls in
    neighbouring fields.
    """
    tier, reason = classify(rec(description="Finds motifs.",
                                operations=["Sequence motif recognition"]))
    assert tier is None
    assert "no corroboration" in reason


def test_weak_operation_plus_domain_topic_admits():
    tier, reason = classify(rec(operations=["Sequence motif recognition"],
                                topics=["Transcription factors and regulatory sites"]))
    assert tier == "extended"
    assert reason == "weak-operation+topic"


# "transcriptional regulation" is a WEAK text pattern: real but not decisive,
# since it appears in plenty of expression and systems-biology tools. Contrast
# with "transcription factor", which is STRONG and admits on its own.
WEAK_TEXT = "Literature-based curation of transcriptional regulation in Escherichia coli."


def test_text_match_without_domain_topic_is_rejected():
    tier, reason = classify(rec(description=WEAK_TEXT))
    assert tier is None
    assert reason == "text match, no domain topic"


def test_text_match_with_domain_topic_admits():
    """The EcoCyc path: weak text plus a corroborating topic."""
    tier, reason = classify(rec(description=WEAK_TEXT, topics=["Gene regulation"]))
    assert tier == "extended"
    assert reason.startswith("text+topic:")


def test_unrelated_record_is_rejected():
    tier, reason = classify(rec(name="Widget", description="Aligns protein structures."))
    assert tier is None
    assert reason in ("no-match", "text match, no domain topic") or reason.startswith(
        ("excluded:", "hard-excluded:"))


# ---------------------------------------------------------------------------
# the ordering, which is where the bugs were
# ---------------------------------------------------------------------------
def test_hard_exclusion_beats_a_strong_operation():
    """bio.tools mis-assigns strong operations too.

    KEGG carries `Gene regulatory network analysis` and Geneious `Sequence
    motif discovery`. Trusting the ontology ahead of the hard exclusions
    readmits whole neighbouring fields, so the exclusion has to win.
    """
    tier, reason = classify(rec(
        name="MassSpecSuite",
        description="Mass spectrometry proteomics platform for peptide identification.",
        operations=["Gene regulatory network analysis"]))
    assert tier is None
    assert reason.startswith("hard-excluded:")


def test_strong_text_beats_a_soft_exclusion():
    """Soft exclusions name neighbouring *fields*, not disqualifying words.

    A tool that plainly says it predicts transcription-factor binding sites is
    not out of scope because it also mentions a phylogenetic tree.
    """
    tier, _ = classify(rec(
        description="Predicts transcription factor binding sites, "
                    "with results mapped onto a phylogenetic tree."))
    assert tier == "core"


def test_hard_exclusion_reads_only_the_leading_description():
    """SEProm, a real regression.

    bio.tools entries often append their host lab's boilerplate. SEProm is a
    prokaryotic promoter predictor whose record carries "We are the Providers
    of ... Protein structure prediction ... Drug design software" from the lab
    web page footer. Matching hard exclusions against the whole record excluded
    a plainly in-scope tool on the strength of its footer.
    """
    # The record verbatim, newlines and all: the separator matters, because the
    # sentence splitter is what pushes the footer out of the window.
    real = (
        "A novel method SEProm for prokaryotic promoter prediction based on DNA "
        "structure and energetics.\n\n"
        "Supercomputing Facility for Bioinformatics & Computational Biology, IIT Delhi.\n\n"
        "We are the Providers of Genome Analysis Software , Protein structure "
        "prediction tool, In-sillico Drug design software, drug discovery, "
        "Bioinformatics, algorithms for Genome analysis, active site directed "
        "Drug Design, gene to drug."
    )
    tier, reason = classify(rec(name="SEProm", description=real))
    assert tier is not None, (
        f"lab boilerplate beyond the lead must not exclude an in-scope tool ({reason})")

    # ...and the guard is the *window*, not luck: the same boilerplate in the
    # opening sentence must still exclude, or the hard rules would be dead code.
    inverted = ("Protein structure prediction tool and in-silico drug design "
                "software for molecular docking.\n\nAlso predicts promoters.")
    assert classify(rec(name="SEProm", description=inverted))[0] is None


# ---------------------------------------------------------------------------
# real records that motivated the design
# ---------------------------------------------------------------------------
def test_hocomoco_is_reachable_despite_a_useless_operation():
    """HOCOMOCO is filed under `Data handling`, which no query would target.

    It is admitted by topic plus text instead. This is the escape hatch working
    as intended; if it stops working the catalog loses a flagship database.
    """
    tier, _ = classify(rec(
        name="HOCOMOCO",
        description="Collection of transcription factor binding sites models "
                    "derived from ChIP-seq data.",
        operations=["Data handling"],
        topics=["DNA binding sites", "ChIP-seq"]))
    assert tier is not None


def test_fimo_the_genotyping_tool_is_not_admitted():
    """The name-collision guard.

    bio.tools ID `fimo` is FiMO, a clonal-phylogeny tool, not the MEME Suite
    scanner. It has never been harvested, but nothing would stop a future query
    reaching it, so the filter is the backstop.
    """
    tier, reason = classify(rec(
        name="FiMO",
        description="Inferring the Temporal Order of Mutations on Clonal "
                    "Phylogeny under Finite-sites Models.",
        operations=["Genotyping", "Standardisation and normalisation", "Quantification"],
        topics=["Genetic variation", "Phylogeny", "Oncology"]))
    assert tier is None, f"FiMO must not enter the catalog (got {reason})"


@pytest.mark.parametrize("description", [
    "Identifies peaks in mass spectra for metabolomite quantification.",
    "Predicts protein secondary structure motifs from sequence.",
    "Predicts RNA secondary structure and folding energy.",
])
def test_neighbouring_fields_sharing_vocabulary_are_excluded(description):
    """`peak`, `motif` and `binding` are shared with fields that are out of scope."""
    tier, _ = classify(rec(description=description, topics=["Epigenomics"]))
    assert tier is None, f"should not admit: {description}"
