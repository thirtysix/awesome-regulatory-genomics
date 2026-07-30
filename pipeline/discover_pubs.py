#!/usr/bin/env python3
"""Stage 2g - find the paper for a tool that bio.tools records none for.

90 catalog entries carry no publication at all, so they show no citation count.
Some of them plainly have papers: HOMER is a featured tool and one of the most
cited in the field.

**The obvious method is the one this catalog has been burned by.** Searching the
literature for a tool's name finds the wrong paper often enough to matter: the
name `Match` resolved to a text-matching library, `SEA` to an RPC framework, and
a DOI that resolves perfectly can still be someone else's work (ChromBPNet once
pointed at "The maize cis-regulatory landscape"). So this stage never searches by
name. It asks each tool's own authoritative source what to cite:

  1. Bioconductor's citation page, which is what the maintainer declared.
  2. `CITATION.cff` in the repository, which is machine-readable and explicit.
  3. `codemeta.json`.
  4. A DOI in the README, which is weakest and always held for review.

Two outcomes are easy to confuse and are kept apart:

* **No article exists.** A Bioconductor page declaring only
  `10.18129/B9.bioc.<pkg>` is the package citing itself. 31 of these packages
  have never had a paper, so "cite the package" is the permanent, correct answer,
  not a failed lookup.
* **An article exists but describes the wrapped method, not the tool.** `rmspc`
  declares the MSPC paper it wraps. That is what its maintainer wants cited, but
  it is not the R package's own work, so it must not be presented as such.

Nothing here is applied automatically. Rows land in docs/publication-discovery.md
for promotion into `overlay.yaml: publications` (bio.tools records) or into
`seeds.yaml` (curated entries).

    python pipeline/discover_pubs.py [--limit N] [--refresh]
"""
from __future__ import annotations

import argparse
import json
import re
import time

import requests
import yaml

from config import CACHE, CURATION, DATA, DOCS, user_agent
from mdutil import cell
from resolve_repos import norm, tokens

CATALOG = DATA / "catalog.json"
PUB_CACHE = CACHE / "pub_discovery.json"
REPORT = DOCS / "publication-discovery.md"

# A DOI contains dots, so a lazy match that stops at the first one truncates it.
# That truncation is not cosmetic: it turned every `10.18129/B9.bioc.MotifDb`
# into `10.18129/B9`, which then no longer matched the self-citation test and was
# reported as a recovered article for 31 packages that have no paper at all.
DOI_RE = re.compile(r"\b10\.\d{4,9}/\S+")

# Identifiers that are a deposited artefact rather than a paper: a Bioconductor
# package citing itself, or a Zenodo/figshare/OSF upload. Attune's README yields
# a figshare DOI for its model weights, which is not a publication.
SELF_DOI = re.compile(r"10\.18129/B9\.bioc\b|10\.5281/zenodo\b"
                      r"|10\.6084/m9\.figshare\b|10\.17605/OSF\b", re.I)

# A README carries other people's DOIs too - a dependency, a benchmark, a "see
# also". Only a DOI in a citation-flavoured context is worth even reviewing.
CITE_CONTEXT = re.compile(r"(cite|citation|citing|reference|published|paper|doi)", re.I)


def http() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": user_agent(), "Accept": "*/*"})
    return s


def get(session: requests.Session, url: str, timeout: int = 30) -> str | None:
    try:
        r = session.get(url, timeout=timeout)
        return r.text if r.status_code == 200 else None
    except requests.RequestException:
        return None


def dois_in(text: str) -> list[str]:
    """DOIs in a blob, trimmed of trailing prose and of anything absurdly long.

    A README can run a DOI straight into a file path, so `\\S+` keeps going past
    the end of the identifier. Real DOIs in this catalog are under 60 characters;
    anything longer is a path or a URL fragment that swallowed one, and passing it
    to Crossref just returns nothing while looking like a real candidate.
    """
    out, seen = [], set()
    for raw in DOI_RE.findall(text or ""):
        # Cut at characters that cannot occur inside a DOI. Markdown is why:
        # `[10.1002/ijc.34666](https://doi.org/10.1002/ijc.34666)` otherwise
        # yields the whole link as one "DOI".
        d = re.split(r"[<>|\\\[\]`\"'*]", raw)[0].rstrip(".,;:}")
        # Parentheses cannot simply be cut: legacy Elsevier DOIs contain them
        # (10.1016/S0168-1702(00)00210-0), and mangling one is what produced a
        # cache key that could never resolve. Drop only unbalanced trailing ones.
        while d.endswith(")") and d.count("(") < d.count(")"):
            d = d[:-1].rstrip(".,;:}")
        if not d or len(d) > 60 or d.lower() in seen:
            continue
        seen.add(d.lower())
        out.append(d)
    return out


def strip_tags(html: str) -> str:
    txt = re.sub(r"<[^>]+>", " ", html)
    for a, b in (("&ldquo;", '"'), ("&rdquo;", '"'), ("&ndash;", "-"),
                 ("&amp;", "&"), ("&nbsp;", " "), ("&lt;", "<"), ("&gt;", ">")):
        txt = txt.replace(a, b)
    return re.sub(r"\s+", " ", txt).strip()


def biocpkg(tool: dict) -> str | None:
    for url in [(tool.get("_registries") or {}).get("bioconductor", ""),
                tool.get("homepage") or ""]:
        if "bioconductor" not in url:
            continue
        m = re.search(r"/(?:release/(?:bioc|data/\w+)/html/)?([A-Za-z0-9._]+?)(?:\.html)?/?$", url)
        if m:
            return m.group(1)
    return None


def slug_of(tool: dict) -> str | None:
    m = re.search(r"github\.com/([^/]+/[^/#?]+)", tool.get("repo_url") or tool.get("homepage") or "")
    return m.group(1).removesuffix(".git") if m else None


# ---------------------------------------------------------------------------
BIOC_TITLE = re.compile(r'"([^"]{15,200})"')


def crossref_by_title(session, title: str) -> str | None:
    """Resolve a title to a DOI, accepting only a near-exact match.

    Some Bioconductor pages state the article in prose with no DOI at all
    ("nucleR: a package for non-parametric nucleosome positioning. Bioinformatics,
    27, 2149-2150"), which otherwise reads as "no article found". A bibliographic
    query recovers it, but a Crossref search ALWAYS returns something, so the top
    hit is only taken when its title matches the one we asked for. Trusting the
    first result is how a catalog ends up citing a plausible stranger.
    """
    try:
        r = session.get("https://api.crossref.org/works",
                        params={"query.bibliographic": title, "rows": 3}, timeout=30)
        items = r.json()["message"]["items"] if r.status_code == 200 else []
    except (requests.RequestException, ValueError, KeyError):
        return None
    want = norm(title)
    for it in items:
        got = norm((it.get("title") or [""])[0])
        if got and (got == want or got.startswith(want[:60]) or want.startswith(got[:60])):
            return it.get("DOI")
    return None


def crossref_by_reference(session, ref: str) -> str | None:
    """Resolve a full reference string ("Heinz S, Benner C, ... Mol Cell 2010").

    Crossref always returns something, so the top hit is accepted only when most
    of its title words already appear in the reference we asked about. Without
    that test this becomes exactly the name-search that put a text-matching
    library in this catalog under the name `Match`.
    """
    try:
        r = session.get("https://api.crossref.org/works",
                        params={"query.bibliographic": ref[:400], "rows": 3}, timeout=30)
        items = r.json()["message"]["items"] if r.status_code == 200 else []
    except (requests.RequestException, ValueError, KeyError):
        return None
    ref_words = set(re.findall(r"[a-z]{4,}", ref.lower()))
    for it in items:
        title = (it.get("title") or [""])[0]
        words = set(re.findall(r"[a-z]{4,}", title.lower()))
        if len(words) >= 4 and len(words & ref_words) / len(words) >= 0.8:
            return it.get("DOI")
    return None


def from_bioconductor(session, tool) -> dict | None:
    pkg = biocpkg(tool)
    if not pkg:
        return None
    for kind in ("bioc", "data/experiment", "data/annotation"):
        html = get(session, f"https://bioconductor.org/packages/release/{kind}"
                            f"/citations/{pkg}/citation.html")
        if not html:
            continue
        txt = strip_tags(html)
        found = [d for d in dois_in(txt) if not SELF_DOI.match(d)]
        if found:
            return {"doi": found[0], "via": "bioconductor citation", "context": txt[:260]}
        if SELF_DOI.search(txt):
            return {"doi": None, "via": "bioconductor citation", "context": txt[:260],
                    "no_article": True}
        # An article stated in prose. The quoted span is the title.
        for quoted in BIOC_TITLE.findall(txt):
            doi = crossref_by_title(session, quoted)
            if doi:
                return {"doi": doi, "via": "bioconductor citation (title lookup)",
                        "context": txt[:260]}
        return {"doi": None, "via": "bioconductor citation", "context": txt[:260]}
    return None


def from_citation_cff(session, tool) -> dict | None:
    slug = slug_of(tool)
    if not slug:
        return None
    for branch in ("HEAD",):
        for name in ("CITATION.cff", "citation.cff"):
            raw = get(session, f"https://raw.githubusercontent.com/{slug}/{branch}/{name}")
            if not raw:
                continue
            # preferred-citation wins: the top-level doi is often the software
            # archive (a Zenodo concept DOI), not the paper.
            block = raw.split("preferred-citation", 1)
            target = block[1] if len(block) > 1 else raw
            found = [d for d in dois_in(target) if not SELF_DOI.match(d)]
            if found:
                return {"doi": found[0], "via": "CITATION.cff", "context": target[:260]}
            return {"doi": None, "via": "CITATION.cff", "context": raw[:260]}
    return None


def from_codemeta(session, tool) -> dict | None:
    slug = slug_of(tool)
    if not slug:
        return None
    raw = get(session, f"https://raw.githubusercontent.com/{slug}/HEAD/codemeta.json")
    if not raw:
        return None
    found = [d for d in dois_in(raw) if not SELF_DOI.match(d)]
    return {"doi": found[0], "via": "codemeta.json", "context": raw[:260]} if found else None


def from_readme(session, tool) -> dict | None:
    slug = slug_of(tool)
    if not slug:
        return None
    for name in ("README.md", "README.rst", "readme.md", "README.txt"):
        raw = get(session, f"https://raw.githubusercontent.com/{slug}/HEAD/{name}")
        if not raw:
            continue
        for line in raw.splitlines():
            found = [d for d in dois_in(line) if not SELF_DOI.match(d)]
            if found and CITE_CONTEXT.search(line):
                return {"doi": found[0], "via": "README (weak)", "context": line.strip()[:260]}
        # a DOI anywhere in a Citation section, even on its own line
        m = re.search(r"(?is)#+\s*(?:how to )?cit\w+.{0,600}", raw)
        if m:
            found = [d for d in dois_in(m.group(0)) if not SELF_DOI.match(d)]
            if found:
                return {"doi": found[0], "via": "README (weak)",
                        "context": strip_tags(m.group(0))[:260]}
        return None
    return None


def from_homepage(session, tool) -> dict | None:
    """A DOI stated on the tool's own page, in a citation context.

    Many of these tools are not on GitHub at all: they are lab pages that say
    outright what to cite. HOMER is the case that matters most, being a featured
    tool and among the most cited in the field, and its paper title contains no
    hint of the name ("Simple combinations of lineage-determining transcription
    factors ..."), so nothing name-based would ever find it.

    Weakest source in the set: a lab page also lists the group's other papers, so
    every hit here is held for review no matter how clean it looks.
    """
    url = tool.get("homepage") or ""
    if not url.startswith("http") or "github.com" in url or "bioconductor.org" in url:
        return None
    # The catalogued URL is often a subpage. HOMER's citation sits on
    # homer.ucsd.edu/homer/ while the record points at .../homer/motif/, so walk
    # up one or two levels before giving up.
    candidates = [url]
    trimmed = url.rstrip("/")
    for _ in range(2):
        trimmed = trimmed.rsplit("/", 1)[0]
        if trimmed.count("/") >= 2:
            candidates.append(trimmed + "/")
    for page in dict.fromkeys(candidates):
        html = get(session, page, timeout=25)
        if not html:
            continue
        txt = strip_tags(html)
        # Not [^.]{0,500}: a reference string is full of periods, and stopping at
        # the first one truncated HOMER's citation at "Bertolino E et al." -
        # exactly before the title, leaving a query with authors and no title.
        for m in re.finditer(r"(?:cite|citation|citing|reference)\w*.{0,420}", txt, re.I):
            span = m.group(0)
            found = [d for d in dois_in(span) if not SELF_DOI.match(d)]
            if found:
                return {"doi": found[0], "via": "homepage (weak)", "context": span.strip()[:260]}
            pm = re.search(r"(?:PMID|pubmed[^0-9]{0,15})(\d{7,9})", span, re.I)
            if pm:
                return {"pmid": pm.group(1), "via": "homepage (weak)",
                        "context": span.strip()[:260]}
            # Prose with no identifier at all, which is how HOMER states its
            # citation. Hand the whole reference string to Crossref, which is
            # what query.bibliographic is for, and keep it only if the returned
            # title is largely made of words from the reference we asked about.
            ref = re.sub(r"^(?:cite|citation|citing|reference)\w*\b[:\s]*", "", span,
                         flags=re.I).strip()
            if len(ref) > 60:
                hit = crossref_by_reference(session, ref)
                if hit:
                    return {"doi": hit, "via": "homepage prose (weak)",
                            "context": ref[:260]}
    return None


SOURCES = (from_bioconductor, from_citation_cff, from_codemeta, from_readme, from_homepage)


# ---------------------------------------------------------------------------
def crossref_title(session, doi: str) -> tuple[str, str, str]:
    """Title, container and year for a DOI, so the claim can be checked."""
    try:
        r = session.get(f"https://api.crossref.org/works/{doi}", timeout=30)
        if r.status_code != 200:
            return "", "", ""
        msg = r.json()["message"]
        year = str((msg.get("issued", {}).get("date-parts") or [[""]])[0][0] or "")
        return ((msg.get("title") or [""])[0],
                (msg.get("container-title") or [""])[0], year)
    except (requests.RequestException, ValueError, KeyError, IndexError):
        return "", "", ""


def pubmed_title(session, pmid: str) -> tuple[str, str, str]:
    try:
        r = session.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                        params={"db": "pubmed", "retmode": "json", "id": pmid}, timeout=30)
        rec = (r.json().get("result") or {}).get(pmid) or {} if r.status_code == 200 else {}
        return (rec.get("title", "").rstrip("."), rec.get("source", ""),
                (rec.get("pubdate") or "")[:4])
    except (requests.RequestException, ValueError, KeyError):
        return "", "", ""


def grade(tool: dict, title: str) -> tuple[str, str]:
    """Does this paper actually look like this tool's own?

    Name in title is the strong signal, exactly as resolve_pubs.verify_curated
    uses it. Where the name is absent the paper may still be right (MAST's paper
    is "Combining evidence using p-values"), so it is held for review rather than
    rejected: the cost of a wrong citation here is a reader misled about impact.
    """
    if not title:
        return "review", "no title from Crossref to check against"
    stem = norm(tool["name"].split()[0])
    if len(stem) >= 3 and stem in norm(title):
        return "accept", "tool name appears in the title"
    shared = tokens(tool.get("description", "")) & tokens(title)
    if len(shared) >= 3:
        return "review", "name absent; description overlap " + ", ".join(sorted(shared)[:4])
    return "review", "name absent from the title and little description overlap"


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--refresh", action="store_true", help="ignore the cache")
    args = ap.parse_args()

    tools = json.loads(CATALOG.read_text())["tools"]
    # Anything recorded under `no_article` in the overlay is settled: either the
    # software has no paper, or its one candidate was read and rejected. Asking
    # again would rediscover the same wrong answer every run.
    settled = set((yaml.safe_load((CURATION / "overlay.yaml").read_text()) or {})
                  .get("no_article") or {})
    targets = [t for t in tools
               if t.get("citations") is None and t["id"] not in settled
               and not t.get("publication")]
    if args.limit:
        targets = targets[: args.limit]
    print(f"{len(targets)} catalog entries have no publication recorded")

    cache = json.loads(PUB_CACHE.read_text()) if PUB_CACHE.exists() and not args.refresh else {}
    session = http()

    for i, tool in enumerate(targets, 1):
        if tool["id"] in cache:
            continue
        hit = None
        for source in SOURCES:
            hit = source(session, tool)
            if hit and (hit.get("doi") or hit.get("pmid") or hit.get("no_article")):
                break
            time.sleep(0.2)
        rec = {"name": tool["name"], "source": tool["source"],
               "homepage": tool.get("homepage", ""), "repo": tool.get("repo_url", ""),
               "description": tool.get("description", "")}
        rec.update(hit or {"doi": None, "via": "", "context": ""})
        if rec.get("doi") or rec.get("pmid"):
            if rec.get("doi"):
                title, venue, year = crossref_title(session, rec["doi"])
            else:
                title, venue, year = pubmed_title(session, rec["pmid"])
            rec["title"], rec["venue"], rec["year"] = title, venue, year
            rec["verdict"], rec["why"] = grade(tool, title)
            # A homepage or README hit is the group saying what to cite, which is
            # useful evidence and not proof: hold it even when the name matches.
            if rec["verdict"] == "accept" and "weak" in rec.get("via", ""):
                rec["verdict"] = "review"
                rec["why"] += " (from a weak source, so read it)"
        elif rec.get("no_article"):
            rec["verdict"], rec["why"] = "no-article", "the declared citation is the software itself"
        else:
            rec["verdict"], rec["why"] = "not-found", "no authoritative citation source carried a DOI"
        cache[tool["id"]] = rec
        if i % 10 == 0:
            print(f"  {i}/{len(targets)}", flush=True)
            PUB_CACHE.write_text(json.dumps(cache, indent=1, sort_keys=True))
        time.sleep(0.3)

    PUB_CACHE.write_text(json.dumps(cache, indent=1, sort_keys=True))
    rows = [dict(r, id=k) for k, r in cache.items() if k in {t["id"] for t in targets}]

    def by(verdict):
        return sorted((r for r in rows if r["verdict"] == verdict), key=lambda r: r["name"].lower())

    accept, review, none_, missing = by("accept"), by("review"), by("no-article"), by("not-found")
    out = [
        "# Publications for tools that bio.tools records none for",
        "",
        "Generated by `pipeline/discover_pubs.py`. Nothing here is applied.",
        "Promote a row into `curation/overlay.yaml` under `publications:` for a",
        "bio.tools record, or add `doi:`/`pmid:` to the entry in `curation/seeds.yaml`",
        "for a curated one.",
        "",
        "Candidates come from the tool's own declared citation, never from a",
        "literature search by name. Read the title before promoting a row: a DOI",
        "that resolves can still be the wrong paper.",
        "",
        f"- **{len(accept)}** carry the tool's name in the title and are ready to promote",
        f"- **{len(review)}** need a human to read the title first",
        f"- **{len(none_)}** have no article at all; the declared citation is the software",
        f"- **{len(missing)}** yielded nothing from any authoritative source",
        "",
    ]

    def table(rs, heading, blurb):
        out.extend([f"## {heading}", "", blurb, "",
                    "| Tool | DOI | Title | Venue | Year | Source | Note |",
                    "| --- | --- | --- | --- | --- | --- | --- |"])
        for r in rs:
            out.append("| {} | `{}` | {} | {} | {} | {} | {} |".format(
                cell(r["name"]), cell(r.get("doi") or ""), cell(r.get("title", ""), 90),
                cell(r.get("venue", ""), 34), cell(r.get("year", "")),
                cell(r.get("via", "")), cell(r.get("why", ""), 60)))
        out.append("")

    if accept:
        table(accept, "Ready to promote",
              "The tool's name appears in the paper's title, so the pairing is self-evidencing.")
    if review:
        table(review, "Needs a human",
              "The name is absent from the title. That is not disqualifying (MAST's paper is "
              "\"Combining evidence using p-values\"), but it has to be read rather than assumed. "
              "Watch for a paper describing a wrapped method rather than this tool: `rmspc` "
              "declares the MSPC paper it wraps.")
    if none_:
        out.extend(["## No article exists", "",
                    "Bioconductor reports the package citing itself, so there is nothing to",
                    "find. This is a permanent answer: record it rather than re-investigating,",
                    "and let the catalog say \"cite the package\" instead of showing a blank.",
                    "",
                    "| Tool | Declared citation |", "| --- | --- |"])
        for r in none_:
            out.append(f"| {cell(r['name'])} | {cell(r.get('context', ''), 110)} |")
        out.append("")
    if missing:
        out.extend(["## Nothing found", "",
                    "No Bioconductor citation page, `CITATION.cff`, `codemeta.json` or README",
                    "DOI. Several are well-known tools whose papers exist and simply are not",
                    "declared anywhere machine-readable, so they need a hand lookup.",
                    "",
                    "| Tool | Homepage | Repository |", "| --- | --- | --- |"])
        for r in missing:
            out.append(f"| {cell(r['name'])} | {cell(r.get('homepage', ''), 60)} "
                       f"| {cell(r.get('repo', ''), 50)} |")
        out.append("")

    REPORT.write_text("\n".join(out))
    print(f"\naccept {len(accept)} | review {len(review)} | "
          f"no article {len(none_)} | nothing found {len(missing)}")
    print(f"-> {REPORT.relative_to(DOCS.parent)}")


if __name__ == "__main__":
    main()
