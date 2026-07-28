"""resolve_installs.py - reading install routes off a repository README.

A badge on a project's own repository is the project stating where it ships,
which is better evidence than finding a package that merely shares its name.
The risk is the opposite one: a README also mentions everybody else's packages.
"""
import pytest

from resolve_installs import belongs_to, routes_in, slug_of


# ---------------------------------------------------------------------------
# what counts as a route
# ---------------------------------------------------------------------------
def test_badges_are_read():
    found = routes_in(
        "[![PyPI](https://img.shields.io/pypi/v/macs3)](https://pypi.org/project/MACS3/)\n"
        "[![Anaconda](https://anaconda.org/bioconda/macs3/badges/version.svg)]()")
    assert "macs3" in [p.lower() for p in found["pypi"]]
    assert "macs3" in [p.lower() for p in found["conda"]]


def test_install_commands_are_read():
    found = routes_in("Install with `pip install pyscenic` or "
                      "`conda install -c bioconda pyscenic`.")
    assert found["pypi"] == ["pyscenic"]
    assert found["conda"] == ["pyscenic"]


def test_r_install_idioms_are_read():
    found = routes_in('BiocManager::install("chromVAR") or install.packages("BoolNet")')
    assert found["bioconductor"] == ["chromVAR"]
    assert found["cran"] == ["BoolNet"]


# ---------------------------------------------------------------------------
# the things a README says that are NOT the tool
# ---------------------------------------------------------------------------
def test_pip_flags_are_not_package_names():
    """`pip install -r requirements.txt` and `pip install --editable .`

    DNABERT's README produced ['--editable', '-r', '-v'] before this guard.
    """
    found = routes_in("pip install -r requirements.txt\npip install --editable .\n"
                      "pip install -v deepbind")
    assert found.get("pypi") == ["deepbind"]


def test_a_registry_qualified_image_is_not_on_docker_hub():
    """Bismark ships via ghcr.io.

    Formatting that as hub.docker.com/r/ghcr.io/... fabricates a URL that 404s,
    which is worse than recording no route at all.
    """
    found = routes_in("docker pull ghcr.io/felixkrueger/bismark\n"
                      "docker pull quay.io/biocontainers/x")
    assert "docker" not in found
    assert routes_in("docker pull lzamparo/basset")["docker"] == ["lzamparo/basset"]


def test_build_tooling_is_never_the_tool():
    assert "pypi" not in routes_in("pip install planemo")
    assert "pypi" not in routes_in("pip install numpy pandas")


# ---------------------------------------------------------------------------
# ownership: is this package the tool, or somebody else's?
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("pkg,name,slug", [
    ("MACS3", "MACS", "macs3-project/MACS"),
    ("pyscenic", "pySCENIC", "aertslab/pySCENIC"),
    ("cooltools", "cooltools", "open2c/cooltools"),
    ("pyDNase", "Wellington / pyDNase", "jpiper/pyDNase"),
    ("lzamparo/basset", "Basset", "davek44/Basset"),
])
def test_the_project_own_package_is_accepted(pkg, name, slug):
    assert belongs_to(pkg, name, slug)


@pytest.mark.parametrize("pkg,name,slug", [
    ("planemo", "ChIP-seq workflows", "bgruening/galaxytools"),
    ("deeplift", "DeepSTARR", "bernardo-de-almeida/DeepSTARR"),
    ("docopt", "Sei", "FunctionLab/sei-framework"),
])
def test_somebody_elses_package_is_rejected(pkg, name, slug):
    """These are dependencies or harnesses, not the tool.

    Galaxy tool repositories are the systematic case: every one of them says
    `pip install planemo`, which is the Galaxy development harness.
    """
    assert not belongs_to(pkg, name, slug)


def test_ownership_tolerates_a_small_suffix():
    """The same tolerance resolve_repos.validate() uses for weblogo/weblogo3."""
    assert belongs_to("weblogo3", "WebLogo", "gecrooks/weblogo")
    assert not belongs_to("cudamemeticalgorithm", "CUDA-MEME", "x/cudameme")


# ---------------------------------------------------------------------------
def test_slug_parsing():
    assert slug_of("https://github.com/aertslab/pySCENIC") == "aertslab/pySCENIC"
    assert slug_of("https://www.github.com/a/b.git") == "a/b"
    assert slug_of("https://bitbucket.org/a/b") == ""
    assert slug_of("") == ""
