"""The discovery stages, and the link-grading rules.

These stages exist to widen the catalog past bio.tools, which means they are
the most likely place for a bad entry to get in. The tests below pin the two
things that keep that from happening: candidates go through the *same* filter
the bio.tools records face, and links are compared by identity rather than by
name.
"""
import pytest

from check_homepages import classify as grade
from discover_literature import candidate_from, name_from_repo
from discover_registries import (BIOCVIEW_TOPIC, as_biotools_record, canon_url,
                                 collapse_wrappers, parse_dcf)
from render import site_url


# ---------------------------------------------------------------------------
# registry sweep
# ---------------------------------------------------------------------------
def test_dcf_parses_indented_continuations():
    """Bioconductor's VIEWS wraps long Descriptions onto indented lines."""
    recs = parse_dcf("Package: x\nTitle: One\n  continued here\n\nPackage: y\nTitle: Two\n")
    assert len(recs) == 2
    assert recs[0]["Title"] == "One continued here"
    assert recs[1]["Package"] == "y"


def test_biocview_map_excludes_the_broad_terms():
    """Only terms specific enough to corroborate on their own are mapped.

    `PeakDetection` is left out for the same reason it is left out of the EDAM
    query plan: in practice it is mass spectrometry's term. `SystemsBiology`
    and `NetworkInference` cover metabolic and signalling networks as readily
    as regulatory ones.
    """
    for broad in ("PeakDetection", "SystemsBiology", "NetworkInference"):
        assert broad not in BIOCVIEW_TOPIC
    assert BIOCVIEW_TOPIC["ChIPSeq"] == "ChIP-seq"


def test_registry_candidate_is_shaped_for_the_shared_filter():
    rec = as_biotools_record({"name": "x", "description": "d", "topics": ["ChIP-seq"]})
    assert rec["function"] == []          # registries carry no EDAM operations
    assert rec["topic"] == [{"term": "ChIP-seq"}]


@pytest.mark.parametrize("a,b", [
    ("https://github.com/Owner/Repo", "http://www.github.com/owner/repo/"),
    ("https://github.com/o/r/tree/master/sub", "https://github.com/o/r"),
])
def test_urls_compare_by_identity(a, b):
    assert canon_url(a) == canon_url(b)


def test_different_repos_do_not_collapse():
    assert canon_url("https://github.com/a/one") != canon_url("https://github.com/a/two")


def test_wrappers_sharing_a_homepage_are_merged():
    """The Galaxy ToolShed publishes one repository per wrapper.

    AlphaGenome arrived five times, once per exposed operation, all pointing at
    the same homepage. Grouping by link is safe because a shared link is
    evidence; grouping by name would not be.
    """
    entries = [
        {"name": "suite_alphagenome", "homepage": "https://github.com/x/alphagenome", "source": "galaxy"},
        {"name": "alphagenome_variant_scorer", "homepage": "https://github.com/x/alphagenome/", "source": "galaxy"},
        {"name": "alphagenome_ism_scanner", "homepage": "https://github.com/x/alphagenome", "source": "galaxy"},
    ]
    merged = collapse_wrappers(entries)
    assert len(merged) == 1
    assert merged[0]["name"] == "suite_alphagenome"     # shortest wins
    assert len(merged[0]["merged"]) == 2


def test_entries_without_a_link_are_never_merged():
    """No link is not evidence of sameness, so these must stay separate."""
    entries = [{"name": "a", "homepage": "", "source": "galaxy"},
               {"name": "b", "homepage": "", "source": "galaxy"}]
    assert len(collapse_wrappers(entries)) == 2


# ---------------------------------------------------------------------------
# literature sweep
# ---------------------------------------------------------------------------
def test_tool_paper_title_yields_name_and_evidence():
    c = candidate_from({"title": "TOBIAS: differential ATAC-seq footprinting.",
                        "doi": "10.1/x", "pmid": "1", "pubYear": "2020"})
    assert c["name"] == "TOBIAS"
    assert c["description"].startswith("differential ATAC-seq footprinting")


def test_a_title_without_a_colon_yields_nothing():
    """No name, no candidate. That is the right failure, not a fallback."""
    assert candidate_from({"title": "Chromatin accessibility in development"}) is None


@pytest.mark.parametrize("title", [
    "Correction: a method for peak calling",
    "RETRACTED: transcription factor binding in yeast",
    "Editorial: the future of regulatory genomics",
])
def test_editorial_prefixes_are_not_tool_names(title):
    assert candidate_from({"title": title}) is None


# ---------------------------------------------------------------------------
# link grading
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("status,expected", [
    (200, "ok"), (301, "ok"), (399, "ok"),
    (404, "dead"), (410, "dead"),
    (401, "blocked"), (403, "blocked"), (405, "blocked"),
    (429, "ratelimited"), (500, "ratelimited"), (503, "ratelimited"),
])
def test_only_404_and_410_count_as_dead(status, expected):
    """The rule the DOI checker learned expensively: a non-200 is not a death.

    That checker once reported 152 broken DOIs, of which 151 were rate
    limiting. 429 and 5xx mean the server is up and struggling; 401/403 mean
    the page is there and we are not welcome.
    """
    assert grade(status, "") == expected


def test_a_transport_failure_is_unreachable_not_dead():
    """Timeouts and DNS failures are often a slow institutional host."""
    assert grade(None, "ConnectTimeout") == "unreachable"
    assert grade(200, "ConnectionError") == "unreachable"


# ---------------------------------------------------------------------------
# the Site column rule
# ---------------------------------------------------------------------------
def test_site_is_empty_when_the_homepage_is_just_the_repository():
    assert site_url({"homepage": "https://github.com/a/b", "repo_url": "https://github.com/a/b"}) == ""
    assert site_url({"homepage": "https://github.com/a/b", "repo_url": ""}) == ""


def test_site_is_the_project_page_when_there_is_one():
    assert site_url({"homepage": "http://jaspar.genereg.net/",
                     "repo_url": "https://github.com/x/y"}) == "http://jaspar.genereg.net/"


def test_site_ignores_trailing_slash_and_www_when_comparing():
    assert site_url({"homepage": "http://www.example.org/tool/",
                     "repo_url": "http://example.org/tool"}) == ""


# ---------------------------------------------------------------------------
# a repository url names the tool by its repository, not by its tail
# ---------------------------------------------------------------------------
def test_name_comes_from_the_repository_not_the_branch():
    """A deep github url must not name the candidate after a path segment.

    .../lisaber/OVAAnno/tree/master put a tool called "master" in the queue.
    It cleared the appears-in-the-text guard because that guard strips word
    boundaries before matching, so a short common word finds itself inside
    some longer run of letters.
    """
    title = ("Detecting novel cell type in single-cell chromatin accessibility "
             "data via open-set domain adaptation with OVAAnno")
    assert name_from_repo("https://github.com/lisaber/OVAAnno/tree/master", title, "") == "OVAAnno"
    assert name_from_repo("https://bitbucket.org/team/toolx/src/main",
                          "we present toolx here", "") == "toolx"


def test_the_appears_in_the_text_guard_still_holds():
    assert name_from_repo("https://github.com/someone/paper-figures", "Unrelated title", "") is None
    assert name_from_repo("https://github.com/MoonLord0525", "A person", "") is None


# ---------------------------------------------------------------------------
# folding a hand review back into the curation files
# ---------------------------------------------------------------------------
def test_yaml_scalars_survive_the_round_trip():
    """seeds.yaml is appended as text, so every scalar must re-read as itself.

    yaml 1.1 resolves bare "no", "yes" and "null" to non-strings, which would
    turn a tool honestly named No into False the next time the file is loaded.
    """
    import yaml as _yaml
    from ingest_review import _yaml_str
    for s in ["Tool: a thing", "it's a 'quoted' name", "no", "yes", "null", "~",
              "On", "TRUE", "3.14", "0755", "- leading dash", "a # hash",
              "[bracket]", "%pct", "@handle", "ChIP-seq peak caller (v2)"]:
        assert str(_yaml.safe_load("k: " + _yaml_str(s))["k"]) == s.rstrip("."), s


def test_the_queue_is_the_join_of_in_scope_and_is_software():
    """Both conditions are load-bearing and neither implies the other."""
    from promotion_queue import absolute
    assert absolute("owner/name") == "https://github.com/owner/name"
    assert absolute("https://github.com/owner/name") == "https://github.com/owner/name"
    assert absolute("http://example.org/tool") == "http://example.org/tool"
    assert absolute("") == ""
