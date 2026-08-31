#!/usr/bin/env python3
"""Stage 1e - turn literature candidates into seeds.yaml entries.

The literature route finds tools the registries do not index, but promoting one
has been entirely manual: read docs/literature-discovery.md, decide, retype the
entry. This stage does the checkable parts and leaves the judgement.

Three layers, cheapest first, each independently useful:

  1. VALIDATE THE REPOSITORY (deterministic, no key, no model). The paper's own
     abstract names a code url, so unlike the registry route there is nothing to
     guess - but a stated url still has to be the tool's own. Reuses
     resolve_repos.validate(), whose rule is that a matching name is necessary
     and never sufficient: the repo must share content words with the paper.
  2. CATEGORISE (model). `categories` is required by build.py and is the one
     field a human currently has to supply.
  3. MIRROR CHECK (a second opinion). Whether the tool is in scope at all. A
     rule cannot do this: CellCall is "ligand-receptor and transcription factor
     activity for cell-cell communication", which classify() admits on the
     phrase "transcription factor" while a reader sees a cell-communication
     tool. Reviewed by hand, it was the one rejection in the first 14.

Layers 2 and 3 decide nothing on their own: disagreement goes to a human, in
keeping with verify_additions.py - the bar for adding stays lower than the bar
for removing, because a wrongly included tool is visible and reportable while a
wrongly excluded one is invisible.

    python pipeline/promote_literature.py --layer1 [--only NAME] [--limit N]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path

import requests

from config import CACHE, DATA, DOCS, RAW, user_agent
from jsonio import read_json, write_json
from resolve_repos import clean_slug, github_meta, norm, validate
from enrich import github_token

CANDIDATES = RAW / "literature_candidates.json"
VERDICTS = RAW / "literature_promote.json"
SCOPE_VERDICTS = RAW / "literature_scope.json"
SCOPE_CACHE = CACHE / "literature_scope_cache.json"
FULLTEXT_VERDICTS = RAW / "literature_fulltext_urls.json"
FULLTEXT_CACHE = CACHE / "fulltext_urls.json"
CAT_VERDICTS = RAW / "literature_categories.json"
CAT_CACHE = CACHE / "literature_category_cache.json"
REPOMAP = CACHE / "repo_map.json"


def load_candidates(only: str | None, limit: int, require_repo: bool = False) -> list[dict]:
    """Every candidate not already in the catalog.

    A code url is how a candidate gets NOTICED - it sorts the queue and hands
    layer 1 something to validate - but it was never a condition of promotion,
    and requiring one costs real recall. Measured 2026-08-30 on 20 candidates
    with no stated repo: 18 were in scope, among them TRACE, DeepTACT, MCAST,
    HiCORE and CATAD. Those are ordinary regulatory-genomics tools whose
    abstracts simply predate or skip the convention of printing a url.
    """
    blob = read_json(CANDIDATES)
    rows = blob["list"] if isinstance(blob, dict) and "list" in blob else blob
    rows = [r for r in rows if not r.get("known")]
    if require_repo:
        rows = [r for r in rows if r.get("repo")]
    if only:
        rows = [r for r in rows if r["name"].lower() == only.lower()]
    rows.sort(key=lambda r: -(r.get("citations") or 0))
    return rows[:limit] if limit else rows


def layer1(rows: list[dict]) -> list[dict]:
    """Validate each stated repository against the paper's own description."""
    http = requests.Session()
    http.headers.update({"User-Agent": user_agent()})
    token = github_token()
    cache = json.loads(REPOMAP.read_text()) if REPOMAP.exists() else {}
    gh_cache = cache.setdefault("_gh_meta", {})

    out = []
    for r in rows:
        slug = clean_slug(r["repo"])
        rec = {"name": r["name"], "repo": r["repo"], "slug": slug,
               "citations": r.get("citations"), "year": r.get("year"),
               "doi": r.get("doi"), "pmid": r.get("pmid"),
               "description": r.get("description")}
        if not slug:
            # Bioconductor and CRAN urls are landing pages, not repositories.
            # Bioconductor and CRAN urls identify a package, not a repository,
            # so there is nothing here to validate against. Printed rather than
            # dropped silently: an invisible skip reads as a candidate that was
            # never seen.
            rec |= {"layer1": "skip", "why": "package landing page, not a repository"}
            out.append(rec)
            print(f"  skip  {r['name'][:22]:24s} {rec['why']}", flush=True)
            continue
        meta = github_meta(http, slug, token, gh_cache)
        if meta is None:
            rec |= {"layer1": "fail", "why": "repository not reachable (404 or private)"}
        else:
            ok, why = validate(r, slug, meta, source="abstract")
            # validate() is tuned for a repo we GUESSED, from a name search or a
            # registry, where the link is a hypothesis. Here the paper's own
            # abstract states the url, which is the author asserting it. With a
            # name match that is two independent confirmations, and demanding
            # shared vocabulary on top of it rejects correct repos whose
            # description is merely terse: epiGBS reads "Code for working with
            # epiGBS data", STARE "TF analysis from epigenetic and Hi-C data".
            # No name match is a different matter and still held: QuASAR-MPRA
            # points into github.com/piquelab/QuASAR/tree/master/mpra, a
            # subdirectory of a larger repo, which a human should see.
            if not ok and meta.get("description"):
                tn, rn = norm(r["name"]), norm(slug.split("/")[-1])
                if tn == rn or (tn in rn and len(rn) <= len(tn) + 3):
                    ok, why = True, f"author-stated url + name match ({why})"
            rec |= {"layer1": "pass" if ok else "hold", "why": why,
                    "stars": meta.get("stars"), "archived": meta.get("archived"),
                    "repo_description": meta.get("description")}
            if "/tree/" in r["repo"] or "/blob/" in r["repo"]:
                rec["note"] = "url points inside a larger repository, not at its root"
        out.append(rec)
        print(f"  {rec['layer1']:5s} {r['name'][:22]:24s} {rec.get('why','')[:64]}", flush=True)
    REPOMAP.write_text(json.dumps(cache, indent=1))
    return out


# ---------------------------------------------------------------------------
# Layers 2 and 3 - the model calls
# ---------------------------------------------------------------------------
def taxonomy_block() -> str:
    from config import CATEGORIES
    return "\n".join(f"  {k} - {label}: {desc}" for k, label, desc in CATEGORIES)


# Scope IS the taxonomy, using config.CATEGORIES' own definitions rather than a
# hand-written paraphrase. Before this the scope call - the harder judgement - got
# bare domain names while the categorise call got full definitions, so the two could
# disagree about what a domain meant and a new category did not widen scope.
# Scope is defined POSITIVELY here. llm_assist.CATEGORISE_SYSTEM, which produced
# the 130 scope drops this catalog applies, defines in_scope only by exclusion
# and never names the 3D genome, methylation, QTL, reporter assays or histone
# marks - all live categories. That omission is why 34 Hi-C tools were dropped
# while chromatin-3d held 153 records. Cell-cell communication is named out
# explicitly because CellCall is the case a rule cannot reach: classify() admits
# it on the phrase "transcription factor" and a reader sees a signalling tool.
SCOPE_SYSTEM = f"""You decide whether a software tool belongs in a catalog of REGULATORY \
GENOMICS tools. You are given the tool's name, its paper's title, and its abstract.

IN scope is exactly the catalog's own taxonomy, with the definitions the catalog uses. A
tool belongs if it does any of these, or is a database serving one:

{taxonomy_block()}

OUT of scope: general alignment and assembly; RNA secondary structure; protein structure, \
folding, docking and ligand binding; mass spectrometry; proteomics; metabolomics; \
phylogenetics; generic differential-expression tooling; RNA modification (m6A, m5C, \
pseudouridine); protein post-translational modification; cell-cell communication and \
ligand-receptor inference; and genome-announcement papers. This holds even when the tool \
shares vocabulary like "motif", "peak", "binding", "regulatory" or "transcription factor".

Judge what the tool DOES, not what it mentions. A tool that USES transcription-factor \
activity as a feature for some other purpose is out of scope; a tool that STUDIES \
transcriptional regulation is in scope.

Supporting software for the assays above IS in scope, decided 2026-08-30: aligners and \
read mappers specific to a regulatory assay (bisulfite, ATAC, ChIP), file formats and \
compression for regulatory signal, GPU ports, simulators, and power or sample-size \
calculators. The test is whether the software exists to serve regulatory genomics, not \
whether it makes a biological inference itself. A GENERAL-purpose aligner or format that \
happens to be usable on regulatory data is still out.

Also decide: is this software at all, or is it a wet-lab assay, a database of results, or \
a review? Assays are out.

Ask what the paper ANNOUNCES. If its contribution is the bench procedure itself, is_software \
is false even when analysis code ships alongside it - nextPBM introduces a nuclear-extract \
protein-binding microarray, ChIP-Rx a spike-in ChIP protocol, GAM a contact-mapping method. \
Nearly every assay paper now releases code, so accompanying software is not the test. A \
program that ANALYSES data produced by such an assay is software and is in scope: bisulfite \
aligners, MPRA statistics packages, ATAC quality-control tools.

Reply with JSON only:
{{"in_scope": true|false, "is_software": true|false, "confidence": "high|medium|low", \
"reason": "one short clause"}}"""


def categorise_system() -> str:
    return f"""Assign categories from this fixed taxonomy to a regulatory-genomics tool. \
You are given its name, paper title, and abstract.

{taxonomy_block()}

Rules:
- Assign every category that genuinely applies. Most tools take 1-3.
- Judge what the tool DOES, not its topic area. A database of ChIP-seq experiments is
  chip-resources, not peak-calling.
- Use these exact keys. Never invent one.
- confidence "high" only when the abstract states the function plainly.

Reply with JSON only:
{{"categories": ["key", ...], "confidence": "high|medium|low"}}"""


def api_key() -> str | None:
    key = os.environ.get("DEEPINFRA_API_KEY")
    if key:
        return key
    env = DATA.parent / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if line.startswith("DEEPINFRA_API_KEY="):
                return line.split("=", 1)[1].strip().strip("'\"")
    return None


# Abstracts are sent whole. The earlier 2,600-character cut was arbitrary and,
# although it fired on only 2 of 630 records, it was a TAIL cut on text whose
# payload is in the tail: the "Availability: ... github.com/x/y" sentence sits at
# median position 0.97 of the abstract, and 177 of 185 code urls fall in its final
# quarter. One of the two truncated records lost its only url. There is no context
# pressure to justify it either - the longest abstract here is ~700 tokens against
# a 1M window, and the whole pass costs about $0.03 in input tokens.
#
# The cap that remains is a guard against a pathological record, not a budget, and
# it keeps the END rather than the beginning for the reason above.
ABSTRACT_CAP = 20000


def clip(text: str, cap: int = ABSTRACT_CAP) -> str:
    """Whole abstract, unless it is absurd - then keep the opening and the tail."""
    if len(text) <= cap:
        return text
    head, tail = text[: cap // 2], text[-(cap // 2):]
    return f"{head}\n[...]\n{tail}"


def ask(model: str, system: str, user: str, key: str) -> tuple[dict | None, str, float]:
    """One json_object call. Returns (parsed, raw, cost).

    Thinking is sent off: GLM-5.3-Flash accepts it (no 400, so controllable not
    forced) and is cheaper and tidier without the reasoning_content channel.
    The raw text is returned alongside the parse because a harness that only
    reports the parse turns its own assumptions into "the model failed".
    """
    body = {"model": model, "max_tokens": 400, "temperature": 0.3, "top_p": 0.9,
            "response_format": {"type": "json_object"},
            "chat_template_kwargs": {"enable_thinking": False},
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}]}
    r = requests.post("https://api.deepinfra.com/v1/openai/chat/completions",
                      headers={"Authorization": f"Bearer {key}"}, json=body, timeout=90)
    d = r.json()
    if "error" in d:
        return None, str(d["error"])[:200], 0.0
    served = d.get("model")
    if served and served != model:
        print(f"    ALIAS: {model} -> {served}", flush=True)
    raw = (d["choices"][0]["message"].get("content") or "")
    cost = (d.get("usage") or {}).get("estimated_cost") or 0.0
    try:
        return json.loads(raw), raw, cost
    except ValueError:
        return None, raw, cost


def abstracts() -> dict:
    """pmid/doi -> abstractText, from the cached Europe PMC result sets."""
    out = {}
    for f in (CACHE / "literature").glob("*.json"):
        for p in json.loads(f.read_text()):
            a = p.get("abstractText")
            if not a:
                continue
            for k in (p.get("pmid"), p.get("doi")):
                if k:
                    out[str(k)] = a
    return out


def layer3(rows: list[dict]) -> list[dict]:
    """Scope check every candidate. Cached by doi/pmid so a re-run is free."""
    key = api_key()
    if not key:
        raise SystemExit("DEEPINFRA_API_KEY not set (env or .env)")
    cache = json.loads(SCOPE_CACHE.read_text()) if SCOPE_CACHE.exists() else {}
    ab = abstracts()
    model = "zai-org/GLM-5.3-Flash"
    prompt_sha = hashlib.sha256(SCOPE_SYSTEM.encode()).hexdigest()[:12]
    spend, n_new, out = 0.0, 0, []
    for i, r in enumerate(rows, 1):
        # The prompt is part of the question, so it is part of the key. Without it a
        # cached verdict silently answers whichever prompt happened to be live when
        # it was written - and this one changed twice on 2026-08-30, first to define
        # scope positively and then to admit supporting software.
        ck = f"{model}:{prompt_sha}:{r.get('doi') or r.get('pmid') or r['name']}"
        if ck in cache:
            j = cache[ck]
        else:
            a = ab.get(str(r.get("pmid") or "")) or ab.get(str(r.get("doi") or "")) or ""
            user = (f"Tool name: {r['name']}\nPaper title: {r.get('description','')}\n\n"
                    f"Abstract:\n{clip(a)}" if a else
                    f"Tool name: {r['name']}\nPaper title: {r.get('description','')}\n"
                    f"(no abstract available)")
            j, raw, cost = ask(model, SCOPE_SYSTEM, user, key)
            spend += cost
            n_new += 1
            if j is None:
                j = {"in_scope": None, "reason": f"unparsed: {raw[:120]}"}
            cache[ck] = j
            if n_new % 25 == 0:
                SCOPE_CACHE.write_text(json.dumps(cache))
                print(f"  {i}/{len(rows)}  ${spend:.4f}", flush=True)
        out.append({**{k: r.get(k) for k in
                       ("name", "repo", "citations", "year", "doi", "pmid", "description")},
                    **{k: j.get(k) for k in
                       ("in_scope", "is_software", "confidence", "reason")},
                    "model": model, "prompt_sha": prompt_sha})
    SCOPE_CACHE.write_text(json.dumps(cache))
    print(f"  {n_new} new calls, ${spend:.4f}")
    return out

def layer2(rows: list[dict]) -> list[dict]:
    """Assign taxonomy categories to the candidates that cleared layer 3.

    A cheaper model than the scope check on purpose: categorisation was
    benchmarked on this very taxonomy over ~1,700 tools with hand labels, where
    DeepSeek-V4-Flash scored 0.83 F1 against GLM-5's 0.85 at a quarter of the
    cost. Scope is the judgement worth paying for and wants a different family;
    assigning a key from a fixed list of 20 does not.
    """
    from config import CATEGORY_KEYS
    key = api_key()
    if not key:
        raise SystemExit("DEEPINFRA_API_KEY not set (env or .env)")
    system = categorise_system()
    model = "deepseek-ai/DeepSeek-V4-Flash"
    prompt_sha = hashlib.sha256(system.encode()).hexdigest()[:12]
    cache = json.loads(CAT_CACHE.read_text()) if CAT_CACHE.exists() else {}
    ab = abstracts()
    valid = set(CATEGORY_KEYS)
    spend, n_new, out = 0.0, 0, []
    for i, r in enumerate(rows, 1):
        ck = f"{model}:{prompt_sha}:{r.get('doi') or r.get('pmid') or r['name']}"
        if ck in cache:
            j = cache[ck]
        else:
            a = ab.get(str(r.get("pmid") or "")) or ab.get(str(r.get("doi") or "")) or ""
            user = (f"Tool name: {r['name']}\nPaper title: {r.get('description','')}\n\n"
                    f"Abstract:\n{clip(a)}" if a else
                    f"Tool name: {r['name']}\nPaper title: {r.get('description','')}\n"
                    f"(no abstract available)")
            j, raw, cost = ask(model, system, user, key)
            spend += cost
            n_new += 1
            if j is None:
                j = {"categories": [], "confidence": "low",
                     "note": f"unparsed: {raw[:120]}"}
            cache[ck] = j
            if n_new % 50 == 0:
                CAT_CACHE.write_text(json.dumps(cache))
                print(f"  {i}/{len(rows)}  ${spend:.4f}", flush=True)
        cats = [c for c in (j.get("categories") or []) if c in valid]
        out.append({**{k: r.get(k) for k in
                       ("name", "repo", "citations", "year", "doi", "pmid", "description")},
                    "categories": cats,
                    "invented": [c for c in (j.get("categories") or []) if c not in valid],
                    "cat_confidence": j.get("confidence"),
                    "cat_model": model, "cat_prompt_sha": prompt_sha})
    CAT_CACHE.write_text(json.dumps(cache))
    print(f"  {n_new} new calls, ${spend:.4f}")
    return out

def fulltext_urls(rows: list[dict]) -> list[dict]:
    """Recover a software url from full text for candidates whose abstract had none.

    Journals put the link in an Availability section, which is body text, so an
    abstract-only reader misses it: 377 promotable candidates state no url and 270
    of them have full text in Europe PMC.

    The url must be NAMED for the tool. A paper links every tool it benchmarks
    against, so the first non-boilerplate url is usually somebody else's: before
    the guard, BiSearch resolved to perlprimer.sourceforge.net and Xenbase to an
    unrelated CSBB repo. With it, precision on a 12-record probe went from about
    half to all twelve, at the cost of 2 fewer hits. A wrong link is worse than
    none.
    """
    import glob
    from discover_literature import FULLTEXT, software_urls
    epmc = {}
    for f in glob.glob(str(CACHE / "literature" / "*.json")):
        for rec in json.loads(Path(f).read_text()):
            k = rec.get("pmid") or rec.get("doi")
            if k:
                epmc[str(k)] = rec
    cache = json.loads(FULLTEXT_CACHE.read_text()) if FULLTEXT_CACHE.exists() else {}
    http = requests.Session()
    http.headers.update({"User-Agent": user_agent()})
    out, n_new = [], 0
    for i, r in enumerate(rows, 1):
        meta = epmc.get(str(r.get("pmid") or "")) or epmc.get(str(r.get("doi") or "")) or {}
        pmcid = meta.get("pmcid")
        rec = {"name": r["name"], "pmcid": pmcid, "doi": r.get("doi"), "pmid": r.get("pmid")}
        if not pmcid or meta.get("inEPMC") != "Y":
            rec |= {"status": "no full text", "url": "", "code": []}
            out.append(rec)
            continue
        if pmcid in cache:
            hit = cache[pmcid]
        else:
            try:
                resp = http.get(FULLTEXT.format(pmcid=pmcid), timeout=60)
                code, other = (software_urls(resp.text, r["name"])
                               if resp.status_code == 200 else ([], []))
                hit = {"code": code[:3], "other": other[:3]}
            except requests.RequestException as exc:
                hit = {"error": str(exc)[:80], "code": [], "other": []}
            cache[pmcid] = hit
            n_new += 1
            if n_new % 25 == 0:
                FULLTEXT_CACHE.write_text(json.dumps(cache))
                print(f"  {i}/{len(rows)}", flush=True)
            time.sleep(0.25)
        code, other = hit.get("code") or [], hit.get("other") or []
        best = code[0] if code else (other[0] if other else "")
        rec |= {"status": "code host" if code else ("named url" if other else "none"),
                "url": best, "code": code}
        out.append(rec)
    FULLTEXT_CACHE.write_text(json.dumps(cache))
    print(f"  {n_new} documents fetched")
    return out

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--layer1", action="store_true",
                    help="validate stated repositories (only candidates that name one)")
    ap.add_argument("--fulltext", action="store_true",
                    help="recover software urls from full text, for candidates with none")
    ap.add_argument("--layer2", action="store_true",
                    help="categorise the candidates that cleared layer 3")
    ap.add_argument("--layer3", action="store_true",
                    help="scope check every candidate, repo or not")
    ap.add_argument("--only", help="a single candidate, by name")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    rows = load_candidates(args.only, args.limit, require_repo=args.layer1)
    print(f"{len(rows)} candidates"
          + (" with a stated code url" if args.layer1 else " not yet in the catalog"))
    if args.fulltext:
        scoped = read_json(SCOPE_VERDICTS)["list"]
        need = {x["name"] for x in scoped
                if x.get("in_scope") and x.get("is_software") and not x.get("repo")}
        rows = [r for r in rows if r["name"] in need]
        print(f"  {len(rows)} promotable candidates with no url in their abstract")
        verdicts = fulltext_urls(rows)
    elif args.layer2:
        scoped = read_json(SCOPE_VERDICTS)["list"]
        ok = {x["name"] for x in scoped if x.get("in_scope") and x.get("is_software")}
        rows = [r for r in rows if r["name"] in ok]
        print(f"  {len(rows)} cleared layer 3 (in scope and software)")
        verdicts = layer2(rows)
    elif args.layer3:
        verdicts = layer3(rows)
    elif args.layer1:
        verdicts = layer1(rows)
    else:
        print("nothing to do: pass --layer1 or --layer3")
        return
    out = FULLTEXT_VERDICTS if args.fulltext else CAT_VERDICTS if args.layer2 else (SCOPE_VERDICTS if args.layer3 else VERDICTS)
    write_json(out, {"count": len(verdicts), "list": verdicts})
    field = "status" if args.fulltext else "cat_confidence" if args.layer2 else ("in_scope" if args.layer3 else "layer1")
    tally = {}
    for v in verdicts:
        tally[str(v.get(field))] = tally.get(str(v.get(field)), 0) + 1
    print("\n" + "  ".join(f"{k}={v}" for k, v in sorted(tally.items())))
    print(f"-> {out}")


if __name__ == "__main__":
    main()
