"""build.primary_identifier() - which paper is *this* tool's paper.

Getting this wrong is what made the original dissertation table's citation
column meaningless: bio.tools attaches a suite's paper to each of its members,
so summing every linked publication hands each EMBOSS command the whole suite's
count. This function picks exactly one identifier, and prefers a peer-reviewed
one over a preprint.
"""
from build import PREPRINT_PREFIXES, norm_name, primary_identifier


def pub(doi=None, pmid=None, primary=False):
    p = {"type": ["Primary"] if primary else []}
    if doi:
        p["doi"] = doi
    if pmid:
        p["pmid"] = pmid
    return p


# ---------------------------------------------------------------------------
def test_no_publications_yields_empty():
    assert primary_identifier({}) == ""
    assert primary_identifier({"publication": []}) == ""


def test_primary_marked_publication_wins_over_order():
    ident = primary_identifier({"publication": [
        pub(pmid="111"),
        pub(pmid="222", primary=True),
    ]})
    assert ident == "pmid:222"


def test_pmid_is_preferred_over_doi_on_the_same_record():
    assert primary_identifier({"publication": [pub(doi="10.1/x", pmid="999")]}) == "pmid:999"


def test_doi_url_prefix_is_stripped():
    ident = primary_identifier({"publication": [pub(doi="https://doi.org/10.1093/nar/gkx1126")]})
    assert ident == "doi:10.1093/nar/gkx1126"


def test_placeholder_pmids_are_ignored():
    """bio.tools stores the string "None" in this field often enough to matter."""
    ident = primary_identifier({"publication": [pub(doi="10.1/real", pmid="None")]})
    assert ident == "doi:10.1/real"


# ---------------------------------------------------------------------------
# preprints
# ---------------------------------------------------------------------------
def test_published_version_beats_a_preprint_listed_first():
    """TOBIAS, a real case.

    Linking a reader to the 2019 bioRxiv preprint when the Nature
    Communications paper exists is a worse citation, not merely an older one -
    even though bio.tools lists the preprint first.
    """
    ident = primary_identifier({"publication": [
        pub(doi="10.1101/2019.12.10.871707"),
        pub(doi="10.1038/s41467-020-18035-1"),
    ]})
    assert ident == "doi:10.1038/s41467-020-18035-1"


def test_a_preprint_is_still_returned_when_it_is_all_there_is():
    ident = primary_identifier({"publication": [pub(doi="10.1101/2020.11.17.384578")]})
    assert ident == "doi:10.1101/2020.11.17.384578"


def test_crossref_upgrade_is_applied():
    """resolve_pubs.py maps preprint DOI -> published DOI; build applies it."""
    ident = primary_identifier(
        {"publication": [pub(doi="10.1101/preprint")]},
        pubmap={"10.1101/preprint": "10.1038/published"})
    assert ident == "doi:10.1038/published"


def test_every_known_preprint_prefix_is_recognised():
    for prefix in PREPRINT_PREFIXES:
        ident = primary_identifier({"publication": [
            pub(doi=prefix + "something"),
            pub(doi="10.1093/nar/journal"),
        ]})
        assert ident == "doi:10.1093/nar/journal", f"{prefix} not treated as a preprint"


# ---------------------------------------------------------------------------
# the dedup key that stops a seed duplicating a bio.tools record
# ---------------------------------------------------------------------------
def test_norm_name_collapses_registry_spelling_variants():
    assert norm_name("Cluster Buster") == norm_name("Cluster-Buster")
    assert norm_name("ChIP-Atlas") == "chipatlas"


def test_norm_name_keeps_genuinely_different_names_apart():
    assert norm_name("MEME") != norm_name("MEMEsuite")
    assert norm_name("ReMap") != norm_name("remap2")


def test_a_successor_named_with_a_plus_is_not_merged_into_its_parent():
    """SCENIC+ is a different tool from SCENIC, not a spelling of it.

    Stripping `+` normalised "SCENIC+" to "scenic", so the hand-written SCENIC+
    seed was skipped as a duplicate of the unrelated SCENIC record. Spelling
    the symbol out fixes both halves: it separates the successor from its
    parent, and it merges the successor with bio.tools' own `scenicplus`.
    """
    assert norm_name("SCENIC+") != norm_name("SCENIC")
    assert norm_name("SCENIC+") == norm_name("scenicplus")


def test_the_plus_convention_holds_for_the_other_known_cases():
    for parent, successor in [("YEASTRACT", "Yeastract+"),
                              ("DeltaNeTS", "DeltaNeTS+"),
                              ("MOST", "MOST+")]:
        assert norm_name(parent) != norm_name(successor), (
            f"{successor} must not collapse into {parent}")


# ---------------------------------------------------------------------------
# monorepos are not a tool's repository
# ---------------------------------------------------------------------------
def test_a_monorepo_is_not_a_tools_repository():
    """bio.tools points hgv_pass at github.com/galaxyproject/galaxy.

    Accepting that made a small Galaxy wrapper the most-starred entry in the
    catalog at 1,818 stars, ahead of MACS. nucleosome_prediction picked up 123
    stars from bgruening/galaxytools the same way.
    """
    from build import is_monorepo
    assert is_monorepo("https://github.com/galaxyproject/galaxy")
    assert is_monorepo("https://github.com/galaxyproject/galaxy/tree/dev/tools")
    assert is_monorepo("https://www.github.com/bgruening/galaxytools/")
    assert is_monorepo("https://github.com/bioconda/bioconda-recipes")


def test_a_real_project_repository_is_kept():
    from build import is_monorepo
    for url in ["https://github.com/taoliu/MACS",
                "https://github.com/aertslab/pySCENIC",
                "https://github.com/FelixKrueger/Bismark",
                "https://bitbucket.org/CBGR/unibind_enrichment/",
                ""]:
        assert not is_monorepo(url), url


def test_the_monorepo_list_is_lowercase():
    """is_monorepo() lowercases the slug before comparing, so an entry with a
    capital in it would silently never match."""
    from config import MONOREPOS
    assert all(m == m.lower() for m in MONOREPOS)
