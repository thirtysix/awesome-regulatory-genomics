#!/usr/bin/env python3
"""Optional stage - LLM proposals for the judgements rules handle badly.

Three jobs, each independently enable-able:

  ``categorise``  assign taxonomy keys from name + description + EDAM terms.
                  Rules get the obvious cases and degrade at the margins; a
                  model reading the actual sentence does better.
  ``describe``    rewrite bio.tools descriptions into a uniform one-liner.
  ``adjudicate``  re-read the rejected records and flag likely false negatives.

Three properties are preserved deliberately, because losing them would cost
more than the accuracy gained:

  * **Proposals, not decisions.** Output goes to curation/llm_proposals.yaml,
    which build.py merges *below* the hand-written overlay. A human promotes
    changes in a reviewable diff; nothing is silently applied.
  * **Cached by content hash.** Re-runs are free and deterministic. Only records
    whose input text actually changed are re-sent. The cache is committed, so
    CI needs no API key.
  * **Fully optional.** With no key and no cache, the pipeline still runs
    end-to-end on the deterministic path.

    export DEEPINFRA_API_KEY=...
    python pipeline/llm_assist.py --jobs categorise,describe --limit 50
    python pipeline/llm_assist.py --jobs adjudicate
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import yaml

from config import CATEGORIES, CATEGORY_DESC, CATEGORY_KEYS, CURATION, DATA, RAW
from enrich import abstract_text, ident_key, read_openalex_work
from jsonio import read_json

ENDPOINT = "https://api.deepinfra.com/v1/openai/chat/completions"
CATALOG = DATA / "catalog.json"
ENRICHED = RAW / "enriched.json.gz"
REJECTED = RAW / "rejected.json"
PROPOSALS = CURATION / "llm_proposals.yaml"
CACHE = DATA / "cache" / "llm.json"
REGISTRY = "~/.claude/skills/deepinfra-models/models.yaml"

# Verified call settings, mirroring the deepinfra-models registry. Sending
# enable_thinking:false to a forced-thinking model breaks it, and letting a
# thinking model think breaks json_object - so this is per-model, never global.
MODEL_PARAMS = {
    "deepseek-ai/DeepSeek-V4-Flash":
        {"temperature": 0.3, "top_p": 0.9, "enable_thinking": False},
    "deepseek-ai/DeepSeek-V3.1-Terminus":
        {"temperature": 0.3, "top_p": 0.9, "enable_thinking": False},
    "deepseek-ai/DeepSeek-V3.2":
        {"temperature": 0.3, "top_p": 0.9, "enable_thinking": False},
    "zai-org/GLM-5":
        {"temperature": 0.3, "top_p": 0.9, "enable_thinking": False},
    "zai-org/GLM-5.2":
        {"temperature": 0.3, "top_p": 0.9, "enable_thinking": False},
    "Qwen/Qwen3-Coder-480B-A35B-Instruct-Turbo":
        {"temperature": 0.3, "top_p": 0.9},
}
BULK_MODEL = "deepseek-ai/DeepSeek-V4-Flash"
QUALITY_MODEL = "deepseek-ai/DeepSeek-V3.1-Terminus"


def load_params(model: str) -> dict:
    """Prefer the shared registry if it is installed; fall back to the table above."""
    path = os.path.expanduser(REGISTRY)
    if os.path.exists(path):
        try:
            reg = yaml.safe_load(open(path))
            for entry in reg.get("models") or []:
                if entry["id"] == model:
                    return dict(entry.get("call") or reg.get("defaults") or {})
        except (OSError, ValueError, KeyError):
            pass
    return MODEL_PARAMS.get(model, {"temperature": 0.3, "top_p": 0.9})


# ---------------------------------------------------------------------------
def call(model: str, system: str, user: str, api_key: str,
         max_tokens: int = 900) -> tuple[str, float, float]:
    """One streaming json_object call. Returns (text, cost, seconds).

    Streaming avoids single-read timeouts, and the usage chunk carries the
    cost. Content is collected from `delta.content` only - thinking models
    stream reasoning on a separate `reasoning_content` channel, and mixing the
    two is the classic "the model returned empty" bug.
    """
    params = load_params(model)
    body = {
        "model": model, "max_tokens": max_tokens, "stream": True,
        "stream_options": {"include_usage": True},
        "response_format": {"type": "json_object"},
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "temperature": params.get("temperature", 0.3),
        "top_p": params.get("top_p", 0.9),
    }
    if params.get("enable_thinking") is False:
        body["chat_template_kwargs"] = {"enable_thinking": False}

    started = time.time()
    r = requests.post(ENDPOINT, json=body, timeout=(20, 180), stream=True,
                      headers={"Authorization": f"Bearer {api_key}",
                               "Accept": "text/event-stream"})
    r.raise_for_status()
    chunks, cost = [], 0.0
    for line in r.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data:"):
            continue
        payload = line[5:].strip()
        if payload == "[DONE]":
            break
        try:
            j = json.loads(payload)
        except ValueError:
            continue
        choices = j.get("choices") or []
        if choices and (choices[0].get("delta") or {}).get("content"):
            chunks.append(choices[0]["delta"]["content"])
        cost = (j.get("usage") or {}).get("estimated_cost", cost) or cost
    return "".join(chunks), cost, time.time() - started


def parse_json(text: str) -> dict | None:
    """Parse a model response, unwrapping the fenced-code and envelope variants."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1].removeprefix("json").strip()
    try:
        return json.loads(text)
    except ValueError:
        start, end = text.find("{"), text.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except ValueError:
                return None
    return None


# ---------------------------------------------------------------------------
TAXONOMY = "\n".join(f"  {k}: {CATEGORY_DESC[k]}" for k, _, _ in CATEGORIES)

CATEGORISE_SYSTEM = f"""You classify bioinformatics software into a fixed taxonomy for a \
catalog of regulatory-genomics tools.

Categories (use these exact keys, never invent one):
{TAXONOMY}

Rules:
- Assign every category that genuinely applies. Most tools take 1-3; a suite may take more.
- Judge what the tool DOES, not what its topic area is. A database of ChIP-seq experiments is \
chip-resources, not peak-calling, even though peaks are involved.
- If it analyses protein or RNA motifs rather than DNA regulatory motifs, return an empty list.
- in_scope is false when the tool is not a regulatory-genomics tool at all (mass spectrometry, \
protein structure, RNA folding, generic sequence alignment, variant calling).
- confidence: "high" only when the description states the function plainly.

Reply with JSON only:
{{"categories": ["key", ...], "in_scope": true, "confidence": "high|medium|low"}}"""

DESCRIBE_SYSTEM = """You rewrite bioinformatics tool descriptions into one uniform line for a \
catalog.

You are given the registry description and, usually, the tool's own paper (title and abstract). \
The registry description is the primary source; the paper is there to supply the function when \
the registry text is too thin to state it.

Rules:
- One sentence, 10-25 words, no trailing full stop.
- Start with a verb or a noun phrase. Never start with the tool's own name, and never write \
"A tool that" or "This package".
- State what it does and on what data. Keep the distinguishing detail; drop marketing, version \
numbers, funding and citations.
- Prefer the specific over the generic. "Calls peaks" is weaker than "Calls peaks from ChIP-seq \
data using a model-based background"; spend the words on what separates this tool from the next \
one doing the same job. Do not pad to length with generic wording.
- Use only information present in the input. Never invent capabilities.
- Describe the TOOL, not the biology. An abstract's findings, organisms studied and results are \
context, not features. "Footprinting unravels binding kinetics" is a result; the tool does \
footprinting.
- EDAM operations are automated registry annotations and are often WRONG. Treat them as a weak \
hint only. Never state a capability that rests on an EDAM term alone, and never name an EDAM \
operation that the description or abstract does not support.
- If the inputs do not actually say what the tool does, reply {"description": null}. Guessing \
from the name or from EDAM terms is worse than leaving it.
- British or American spelling as given; do not "correct" the tool's own name.

Also judge whether the paper is plausibly THIS tool's paper. Set paper_matches to false only \
when the subject matter is unrelated to the tool - a physics paper against a genomics tool, a \
clinical review against a software package. A paper whose title never names the tool is normal \
and is NOT a mismatch: method papers routinely have descriptive titles. When paper_matches is \
false, ignore the paper and describe the tool from the registry text alone.

Reply with JSON only:
{"description": "...", "paper_matches": true, "mismatch_reason": ""}
or {"description": null, "paper_matches": true, "mismatch_reason": ""}"""

SCOPE_AUDIT_SYSTEM = """You review tools that an automated filter ADMITTED into a catalog of \
regulatory-genomics tools, and identify the ones admitted wrongly.

Each of these was admitted on a single EDAM operation annotation with nothing corroborating it. \
Those annotations are frequently wrong: a cytochrome-P450 inhibition predictor was admitted as \
"Promoter prediction", a protein beta-strand predictor likewise. So judge the tool by what its \
description and paper say it DOES, and treat the EDAM operation as unreliable.

IN scope: transcription-factor binding and motifs; promoters, enhancers and cis-regulatory \
elements; DNase/ATAC footprinting; ChIP-seq/ATAC-seq peak calling and annotation; chromatin \
accessibility and nucleosomes; gene-regulatory networks; regulatory variant effect; DNA \
methylation; the 3D genome (Hi-C, HiChIP, loops, TADs); histone modifications; reporter assays \
(MPRA/STARR-seq); molecular QTL (eQTL, caQTL); and databases serving any of those.

OUT of scope: general alignment and assembly; RNA secondary structure; protein structure, \
folding, docking and ligand or small-molecule binding sites; mass spectrometry; proteomics; \
metabolomics; phylogenetics; generic differential-expression tooling; RNA modification \
(m6A, m5C, m6Am, pseudouridine); protein post-translational modification including protein \
methylation and acetylation; and genome-announcement papers. This holds even when the tool \
shares vocabulary like "motif", "peak", "binding" or "regulatory".

A DNA-binding protein predictor IS in scope. A protein-ligand binding site predictor is NOT. \
A tool for RNA modification sites is NOT, even though it says "modification site prediction".

Reply with JSON only:
{"in_scope": true, "confidence": "high|medium|low", "reason": "one short clause"}"""

ADJUDICATE_SYSTEM = """You review bioinformatics tools that an automated filter EXCLUDED from a \
catalog of regulatory-genomics tools, and identify the ones excluded wrongly.

In scope: transcription-factor binding and motifs; promoters, enhancers and cis-regulatory \
elements; DNase/ATAC footprinting; ChIP-seq/ATAC-seq peak calling and annotation; chromatin \
accessibility and nucleosomes; gene-regulatory networks; regulatory variant effect; and databases \
serving those.

Out of scope: general alignment and assembly, RNA structure, protein structure and docking, mass \
spectrometry, proteomics, metabolomics, phylogenetics, and generic differential-expression \
tooling - even when they share vocabulary like "motif", "peak" or "binding".

Be strict. The filter is usually right; only flag a clear mistake.

Reply with JSON only:
{"should_include": false, "reason": "one short clause"}"""


def digest(*parts: str) -> str:
    return hashlib.sha256("\x1f".join(parts).encode()).hexdigest()[:16]


def tool_prompt(t: dict) -> str:
    ops = ", ".join(t.get("_operations") or []) or "none"
    topics = ", ".join((t.get("topics") or [])[:6]) or "none"
    types = ", ".join(t.get("tool_type") or []) or "unknown"
    return (f"Name: {t['name']}\nDescription: {t.get('description') or '(none)'}\n"
            f"EDAM operations: {ops}\nEDAM topics: {topics}\nTool type: {types}")


def source_descriptions() -> dict[str, str]:
    """bio.tools description as HARVESTED, keyed by biotools id.

    The describe stage must not read data/catalog.json for this. build.py has
    already merged the previous run's rewrite into that file, so reading it back
    feeds the model its own output: the run of 2026-07-27 rewrote a rewrite for
    1,407 of 1,563 records, and `was:` recorded the first rewrite rather than the
    original. It is the same shape as the verify_additions.py convergence trap.
    """
    out: dict[str, str] = {}
    for rec in read_json(ENRICHED).get("list") or []:
        key = rec.get("biotoolsID")
        if key and rec.get("description"):
            out[key] = rec["description"].strip()
    return out


def describe_prompt(t: dict, source: str, paper: dict) -> str:
    """The describe input: registry text first, the tool's own paper as backup."""
    ops = ", ".join(t.get("_operations") or []) or "none"
    topics = ", ".join((t.get("topics") or [])[:6]) or "none"
    types = ", ".join(t.get("tool_type") or []) or "unknown"
    lines = [f"Name: {t['name']}",
             f"Registry description: {source or '(none)'}",
             f"EDAM operations (unreliable): {ops}",
             f"EDAM topics: {topics}",
             f"Tool type: {types}"]
    if paper.get("title"):
        lines.append(f"Paper title: {paper['title']}")
    if paper.get("abstract"):
        lines.append(f"Paper abstract: {paper['abstract'][:1800]}")
    return "\n".join(lines)


def paper_context(t: dict) -> dict:
    """Title and abstract of the tool's primary publication, from the OpenAlex cache.

    Read-only: whatever `enrich.py --backfill-works` has stored. A tool with no
    stored response simply gets no paper, which is the pre-existing behaviour.

    `_identifiers` alone is not enough. It holds what the HARVEST mentioned, so a
    publication recovered by discover_pubs.py or set in the overlay is missing
    from it: HOMER, featured and the second most-cited entry, carries
    `doi:10.1016/j.molcel.2010.05.004` in `publication` and an empty
    `_identifiers`, so it drew on no paper at all. Try the displayed publication
    too, and prefer it, since that is the paper the catalog actually claims.
    """
    idents = []
    pub = t.get("publication")
    if isinstance(pub, str) and pub.strip():
        idents.append(pub.strip())
    idents += t.get("_identifiers") or []
    for ident in dict.fromkeys(idents):
        work = read_openalex_work(ident_key(ident))
        if not work:
            continue
        title = work.get("title") or work.get("display_name") or ""
        abstract = abstract_text(work)
        if title or abstract:
            return {"title": title, "abstract": abstract}
    return {}


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--jobs", default="categorise",
                    help="comma-separated: categorise,describe,adjudicate,audit-scope,verify-scope")
    ap.add_argument("--model", default=BULK_MODEL)
    ap.add_argument("--escalate-model", default=QUALITY_MODEL,
                    help="retry model for invalid or low-confidence bulk output")
    ap.add_argument("--no-escalate", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=8,
                    help="concurrent API calls")
    ap.add_argument("--refresh", action="store_true",
                    help="ignore cached results for the selected jobs")
    args = ap.parse_args()

    api_key = os.environ.get("DEEPINFRA_API_KEY") or os.environ.get("DEEPINFRA_TOKEN")
    if not api_key:
        sys.exit("DEEPINFRA_API_KEY is not set. This stage is optional; the rest of "
                 "the pipeline runs without it.")

    jobs = {j.strip() for j in args.jobs.split(",") if j.strip()}
    unknown = jobs - {"categorise", "describe", "adjudicate", "audit-scope", "verify-scope"}
    if unknown:
        sys.exit(f"unknown job(s): {', '.join(sorted(unknown))}")

    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    proposals = yaml.safe_load(PROPOSALS.read_text()) if PROPOSALS.exists() else {}
    proposals = proposals or {}
    catalog = json.loads(CATALOG.read_text())["tools"]

    stats = {"spend": 0.0, "escalations": 0, "invalid": 0, "done": 0}
    lock = threading.Lock()
    valid_keys = set(CATEGORY_KEYS)

    def cached_call(job: str, key_parts: tuple[str, ...], system: str, user: str,
                    validate) -> dict | None:
        """Call with cache, then escalate to the quality model if unusable.

        The bulk model is documented to blank enum fields on a fraction of
        calls. An unvalidated empty enum silently becomes a permanent
        mis-classification, so an invalid result escalates rather than being
        stored. Thread-safe: the model is passed explicitly rather than held on
        shared state, and every counter update takes the lock.
        """
        cache_key = f"{job}:{args.model}:{digest(*key_parts)}"
        with lock:
            if cache_key in cache and not args.refresh:
                return cache[cache_key]

        def attempt(model: str) -> dict | None:
            text, cost, _ = call(model, system, user, api_key)
            with lock:
                stats["spend"] += cost
            parsed = parse_json(text)
            return parsed if (parsed and validate(parsed)) else None

        try:
            result = attempt(args.model)
        except Exception:                                   # noqa: BLE001
            result = None
        if result is None:
            with lock:
                stats["invalid"] += 1
            if args.no_escalate:
                return None
            with lock:
                stats["escalations"] += 1
            try:
                result = attempt(args.escalate_model)
            except Exception:                               # noqa: BLE001
                result = None
            if result is None:
                return None
        with lock:
            cache[cache_key] = result
        return result

    def run_batch(items, work, label):
        """Fan out over a thread pool, checkpointing the cache periodically."""
        out = {}
        stats["done"] = 0
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(work, item): item for item in items}
            for fut in as_completed(futures):
                try:
                    got = fut.result()
                except Exception as exc:                    # noqa: BLE001
                    print(f"    ! {type(exc).__name__}: {exc}", file=sys.stderr)
                    got = None
                if got:
                    out.update(got)
                with lock:
                    stats["done"] += 1
                    n = stats["done"]
                    if n % 100 == 0:
                        print(f"  {label} {n}/{len(items)}  ${stats['spend']:.3f}", flush=True)
                        CACHE.parent.mkdir(parents=True, exist_ok=True)
                        CACHE.write_text(json.dumps(cache))
        return out

    # --- categorise ---------------------------------------------------------
    if "categorise" in jobs:
        tools = [t for t in catalog if t["source"] == "bio.tools"]
        tools = tools[: args.limit] if args.limit else tools
        print(f"categorise: {len(tools)} tools via {args.model} "
              f"({args.workers} workers)")

        def do_categorise(t):
            res = cached_call(
                "categorise", (t["name"], t.get("description") or "",
                               ",".join(t.get("_operations") or [])),
                CATEGORISE_SYSTEM, tool_prompt(t),
                lambda r: isinstance(r.get("categories"), list)
                and all(c in valid_keys for c in r["categories"])
                and isinstance(r.get("in_scope"), bool))
            if not res:
                return None
            proposed = [c for c in CATEGORY_KEYS if c in set(res["categories"])]
            if set(proposed) == set(t["categories"]) and res["in_scope"]:
                return None
            return {t["id"]: {"categories": proposed, "was": t["categories"],
                              "in_scope": res["in_scope"],
                              "confidence": res.get("confidence", "medium")}}

        out = run_batch(tools, do_categorise, "categorise")
        proposals["categories"] = out
        print(f"  {len(out)} differ from the rule-derived categories")

    # --- describe -----------------------------------------------------------
    if "describe" in jobs:
        sources = source_descriptions()
        tools = [t for t in catalog
                 if t["source"] == "bio.tools" and sources.get(t.get("biotools_id"))]
        tools = tools[: args.limit] if args.limit else tools
        n_paper = 0
        mismatches: dict[str, dict] = {}
        print(f"describe: {len(tools)} tools via {args.model} "
              f"({args.workers} workers)")

        def do_describe(t):
            nonlocal n_paper
            source = sources[t["biotools_id"]]
            paper = paper_context(t)
            if paper:
                n_paper += 1
            res = cached_call(
                # The cache key must carry every input, or a prompt that now
                # includes the paper would return the pre-paper answer. Bump the
                # version whenever DESCRIBE_SYSTEM changes: the key covers the
                # inputs, not the instructions, so a prompt edit is invisible to
                # it. v3 added the paper_matches check.
                "describe-v3", (t["name"], source, paper.get("title", ""),
                                paper.get("abstract", "")[:1800]),
                DESCRIBE_SYSTEM, describe_prompt(t, source, paper),
                lambda r: r.get("description") is None
                or (isinstance(r.get("description"), str)
                    and 6 <= len(r["description"].split()) <= 30))
            # A free second opinion on whether the paper belongs to the tool.
            # The model is reading both anyway, and a linked paper about
            # something else entirely is how NOBAI's transposed PMID surfaced.
            # Recorded, never acted on: build.py does not read this key.
            if res and res.get("paper_matches") is False and paper.get("title"):
                with lock:
                    mismatches[t["id"]] = {
                        "name": t["name"],
                        "paper": paper.get("title", ""),
                        "publication": t.get("publication") or "",
                        "reason": (res.get("mismatch_reason") or "").strip(),
                    }
            # An explicit null is the model declining to guess. Keep the
            # harvested text rather than recording a rewrite that never happened.
            if not res or res.get("description") is None:
                return None
            return {t["id"]: {"description": res["description"].rstrip("."),
                              "was": source}}

        out = run_batch(tools, do_describe, "describe")
        proposals["descriptions"] = out
        proposals["paper_mismatch"] = mismatches
        print(f"  {len(out)} rewritten; {n_paper} had a paper to draw on, "
              f"{len(tools) - len(out)} left as harvested")
        if mismatches:
            print(f"  {len(mismatches)} linked papers look unrelated to their tool "
                  f"(see paper_mismatch in the proposals file)")

    # --- adjudicate ---------------------------------------------------------
    if "adjudicate" in jobs:
        rejects = json.loads(REJECTED.read_text())["list"]
        rejects = rejects[: args.limit] if args.limit else rejects
        print(f"adjudicate: {len(rejects)} rejected records via {args.model} "
              f"({args.workers} workers)")

        def do_adjudicate(t):
            user = (f"Name: {t['name']}\nDescription: {t.get('description') or '(none)'}\n"
                    f"EDAM operations: {', '.join(t.get('operations') or []) or 'none'}\n"
                    f"Filter's reason for exclusion: {t.get('reason', '')}")
            res = cached_call(
                "adjudicate", (t["name"], t.get("description") or ""),
                ADJUDICATE_SYSTEM, user,
                lambda r: isinstance(r.get("should_include"), bool))
            if not (res and res["should_include"]):
                return None
            return {t["biotoolsID"]: {"name": t["name"],
                                      "reason": res.get("reason", ""),
                                      "filter_said": t.get("reason", "")}}

        out = run_batch(rejects, do_adjudicate, "adjudicate")
        proposals["false_negatives"] = out
        print(f"  {len(out)} flagged as wrongly excluded")

    # --- audit-scope --------------------------------------------------------
    # The inverse of adjudicate: that one re-reads REJECTIONS, this one re-reads
    # ADMISSIONS. Records admitted on a single EDAM operation have nothing
    # corroborating them, and EDAM is wrong often enough that this admitted a
    # cytochrome-P450 predictor on "Promoter prediction". Two models must agree
    # before anything is proposed for removal, and the verdict is a proposal in
    # a review file, never an edit to the catalog.
    if "audit-scope" in jobs:
        thin = [t for t in catalog
                if str(t.get("_select_reason") or "").startswith(("operation:", "weak-"))]
        thin = thin[: args.limit] if args.limit else thin
        second = args.escalate_model

        def scope_prompt(t):
            paper = paper_context(t)
            lines = [f"Name: {t['name']}",
                     f"Catalog description: {t.get('description') or '(none)'}",
                     f"EDAM operations (unreliable): "
                     f"{', '.join(t.get('_operations') or []) or 'none'}",
                     f"EDAM topics: {', '.join((t.get('topics') or [])[:6]) or 'none'}",
                     f"Admitted by rule: {t.get('_select_reason')}"]
            if paper.get("title"):
                lines.append(f"Paper title: {paper['title']}")
            if paper.get("abstract"):
                lines.append(f"Paper abstract: {paper['abstract'][:1500]}")
            return "\n".join(lines)

        def ask(model, t):
            key = f"audit-scope:{model}:{digest(t['name'], t.get('description') or '')}"
            with lock:
                if key in cache and not args.refresh:
                    return cache[key]
            try:
                text, cost, _ = call(model, SCOPE_AUDIT_SYSTEM, scope_prompt(t), api_key)
            except Exception:                               # noqa: BLE001
                return None
            with lock:
                stats["spend"] += cost
            res = parse_json(text)
            if not (res and isinstance(res.get("in_scope"), bool)):
                return None
            with lock:
                cache[key] = res
            return res

        # A sweep whose control case fails measures nothing. Two records that
        # must come back in scope and two that must come back out; if any of the
        # four is wrong the prompt or the model is not fit and the run aborts
        # rather than reporting a rate.
        by_id = {t["id"]: t for t in catalog}
        controls = [("macs", True), ("jaspar", True),
                    ("sitehound-web", False), ("m6ampred", False)]
        print("audit-scope: checking controls")
        for cid, want in controls:
            if cid not in by_id:
                sys.exit(f"  control {cid} is not in the catalog; cannot validate the sweep")
            got = ask(args.model, by_id[cid])
            if not got or got["in_scope"] is not want:
                sys.exit(f"  control {cid} expected in_scope={want}, got "
                         f"{got and got['in_scope']}. Aborting rather than reporting a rate.")
            print(f"  ok {cid}: in_scope={want}")

        print(f"audit-scope: {len(thin)} thinly-admitted records via {args.model}, "
              f"confirmed with {second} ({args.workers} workers)")

        def do_audit(t):
            first = ask(args.model, t)
            if not first or first["in_scope"]:
                return None
            confirm = ask(second, t)
            if not confirm or confirm["in_scope"]:
                return None                    # disagreement: keep it, the safe direction
            return {t["id"]: {"name": t["name"],
                              "description": t.get("description", ""),
                              "admitted_by": t.get("_select_reason"),
                              "citations": t.get("citations") or 0,
                              "reason": first.get("reason", ""),
                              "confidence": first.get("confidence", "medium"),
                              "agreed_by": [args.model, second]}}

        out = run_batch(thin, do_audit, "audit-scope")
        proposals["admitted_out_of_scope"] = out
        print(f"  {len(out)}/{len(thin)} flagged out of scope by BOTH models")

        # A reviewable file, in the shape overlay.yaml: exclude expects, so a
        # promotion is a copy-paste rather than a transcription.
        doc = DATA.parent / "docs" / "scope-audit.md"
        ranked = sorted(out.items(), key=lambda kv: -(kv[1].get("citations") or 0))
        lines = [
            "# Scope audit: records admitted on thin evidence",
            "",
            "GENERATED by `pipeline/llm_assist.py --jobs audit-scope`. Proposals, not",
            "decisions: nothing here is applied. Promote rows into",
            "`curation/overlay.yaml: exclude`, which is the hand-written layer.",
            "",
            f"{len(thin)} of the catalog's records were admitted by a single EDAM operation",
            "or a weak operation-plus-topic rule, with nothing corroborating them. Those",
            "annotations are unreliable often enough to matter: a cytochrome-P450 inhibition",
            "predictor was admitted as `Promoter prediction`. Each was re-read by two models",
            f"given its description and paper; **{len(out)} were called out of scope by both**.",
            "Disagreements are kept, which is the conservative direction.",
            "",
            "| tool | citations | admitted by | why it does not belong |",
            "| --- | ---: | --- | --- |",
        ]
        for tid, v in ranked:
            why = v.get("reason", "").replace("|", "/")
            lines.append(f"| `{tid}` {v['name']} | {v.get('citations') or 0} | "
                         f"`{v.get('admitted_by')}` | {why} |")
        lines += ["", "## Ready to paste into `overlay.yaml: exclude`", "", "```yaml"]
        for tid, v in ranked:
            why = v.get("reason", "").rstrip(".").replace(":", ";")
            lines.append(f"  {tid}: {why}")
        lines += ["```", ""]
        doc.parent.mkdir(parents=True, exist_ok=True)
        doc.write_text("\n".join(lines))
        print(f"  -> {doc}")

    # --- verify-scope -------------------------------------------------------
    # Dropping a record from the catalog is destructive, so one model's opinion
    # is not enough. Re-ask a DIFFERENT model about everything the first flagged
    # out of scope, and confirm only where the two agree. Disagreements stay in
    # the catalog - the conservative direction.
    if "verify-scope" in jobs:
        flagged = [k for k, v in (proposals.get("categories") or {}).items()
                   if not v.get("in_scope")]
        by_id = {t["id"]: t for t in catalog}
        items = [by_id[k] for k in flagged if k in by_id]
        second = args.escalate_model
        print(f"verify-scope: re-checking {len(items)} out-of-scope flags "
              f"with {second} ({args.workers} workers)")

        def do_verify(t):
            cache_key = f"verify-scope:{second}:{digest(t['name'], t.get('description') or '')}"
            with lock:
                if cache_key in cache and not args.refresh:
                    res = cache[cache_key]
                    return {t["id"]: res} if res.get("in_scope") is False else None
            try:
                text, cost, _ = call(second, CATEGORISE_SYSTEM, tool_prompt(t), api_key)
            except Exception:                               # noqa: BLE001
                return None
            with lock:
                stats["spend"] += cost
            res = parse_json(text)
            if not (res and isinstance(res.get("in_scope"), bool)):
                return None
            with lock:
                cache[cache_key] = res
            if res["in_scope"]:
                return None
            return {t["id"]: {"name": t["name"], "description": t.get("description", ""),
                              "agreed_by": [args.model, second]}}

        confirmed = run_batch(items, do_verify, "verify-scope")
        proposals["out_of_scope_confirmed"] = confirmed
        print(f"  {len(confirmed)}/{len(items)} confirmed out of scope by both models "
              f"({len(items) - len(confirmed)} disagreements kept in the catalog)")

    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache))
    PROPOSALS.write_text(
        "# GENERATED by pipeline/llm_assist.py - proposals, not decisions.\n"
        "# build.py merges this BELOW curation/overlay.yaml, so any hand-written\n"
        "# correction always wins. Review before trusting; promote what you agree\n"
        "# with into overlay.yaml, which is never overwritten.\n"
        f"# model: {args.model}  jobs: {','.join(sorted(jobs))}\n\n"
        + yaml.safe_dump(proposals, sort_keys=True, width=100, allow_unicode=True))

    print(f"\nspend ${stats['spend']:.3f} | escalations {stats['escalations']} "
          f"| unusable after retry {stats['invalid'] - stats['escalations']}")
    print(f"-> {PROPOSALS}")


if __name__ == "__main__":
    main()
