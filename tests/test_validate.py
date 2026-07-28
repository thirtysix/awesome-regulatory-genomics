"""resolve_repos.validate() - is this really the tool's repository?

The governing rule is that **a matching name is necessary but never
sufficient**. Tool names in this field are short and collide across all of
software, so every loosening of this function has produced wrong links that
look perfectly plausible. Each case below is one of those.
"""
import pytest

import resolve_repos
from resolve_repos import STOP, tokens, validate


def tool(name, description):
    return {"name": name, "description": description}


def gh(description="", topics=(), readme=""):
    return {"description": description, "topics": list(topics), "readme": readme}


# ---------------------------------------------------------------------------
# name matching
# ---------------------------------------------------------------------------
def test_exact_name_with_agreement_is_accepted():
    ok, why = validate(
        tool("TOBIAS", "Differential ATAC-seq footprinting between conditions"),
        "loosolab/TOBIAS",
        gh("ATAC-seq footprinting analysis across conditions"))
    assert ok, why


def test_prefix_collision_is_rejected():
    """`cudameme` is a prefix of `cudamemeticalgorithm`.

    Substring matching gave CUDA-MEME a particle-swarm GRN repository, and
    STREME a web frontend (`streme` in `stremefrontend`). A few extra
    characters are tolerated; a different word is not.
    """
    ok, why = validate(
        tool("CUDA-MEME", "GPU-accelerated motif discovery for DNA sequences"),
        "someone/cudamemeticalgorithm",
        gh("Particle swarm memetic algorithm implementation"))
    assert not ok, why


def test_short_suffix_is_still_a_name_match():
    """`weblogo` vs `weblogo3` must match, or the correct answer is rejected."""
    ok, why = validate(
        tool("WebLogo", "Generate sequence logos from aligned sequences"),
        "gecrooks/weblogo3",
        gh("WebLogo: sequence logo generator for aligned DNA sequences"))
    assert ok, why


def test_same_name_different_tool_is_rejected():
    """bioconda has a `medusa` recipe for a genome scaffolder.

    This catalog's MEDUSA learns motif models of TF binding sites. Two real
    bioinformatics tools, one name; a domain-scoped registry does not rescue
    matching on the name alone.
    """
    ok, why = validate(
        tool("MEDUSA", "Learns motif models of transcription factor binding sites"),
        "combogenomics/DUCT",
        gh("MEDUSA: a draft genome scaffolder using multiple reference genomes"))
    assert not ok, why


# ---------------------------------------------------------------------------
# evidence thresholds
# ---------------------------------------------------------------------------
def test_repo_without_any_description_cannot_be_verified():
    ok, why = validate(tool("SomeTool", "Calls peaks from ChIP-seq data"),
                       "user/sometool", gh())
    assert not ok
    assert "cannot verify" in why


def test_github_search_needs_more_agreement_than_a_registry():
    """GitHub search returns the most *popular* similarly named repository.

    For a short bioinformatics name that is usually somebody else's project, so
    the same evidence that suffices from bioconda is not enough from search.
    """
    t = tool("Genrich", "Peak caller with replicate handling and an ATAC mode")
    meta = gh("Peak caller for sequencing data")   # exactly two shared terms
    ok_registry, why_registry = validate(t, "jsh58/Genrich", meta, source="bioconda")
    ok_search, why_search = validate(t, "jsh58/Genrich", meta, source="github-search")
    assert ok_registry, why_registry
    assert not ok_search, why_search


def test_strong_textual_agreement_carries_a_name_mismatch():
    """A repository can be right while being named differently.

    Four shared content words is enough on its own; this is what recovers tools
    whose repository is named after the lab or the paper.
    """
    ok, why = validate(
        tool("SomeScanner",
             "Scans genomic sequences for transcription factor binding motifs "
             "using position weight matrices"),
        "lab/entirely-different-name",
        gh("Scans genomic sequences for transcription factor binding motifs "
           "with position weight matrices"))
    assert ok, why


# ---------------------------------------------------------------------------
# the stopword invariant
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("word", ["sequence", "genome", "motif", "binding",
                                  "chromatin", "regulatory", "transcription"])
def test_domain_words_are_not_stopwords(word):
    """Adding these to STOP rejected the correct WebLogo repository.

    STOP exists to drop generic software words ("tool", "python", "fast").
    Domain words are the entire signal that separates a sequence-logo generator
    from a meme generator, so they must survive tokenisation.
    """
    assert word not in STOP
    assert word in tokens(f"A tool for {word} analysis")


def test_stop_still_removes_generic_software_words():
    assert tokens("A fast simple python tool library framework") == set()
