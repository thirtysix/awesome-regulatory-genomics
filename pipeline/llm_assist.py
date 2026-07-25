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

ENDPOINT = "https://api.deepinfra.com/v1/openai/chat/completions"
CATALOG = DATA / "catalog.json"
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

Rules:
- One sentence, 8-22 words, no trailing full stop.
- Start with a verb or a noun phrase. Never start with the tool's own name, and never write \
"A tool that" or "This package".
- State what it does and on what data. Keep the distinguishing detail; drop marketing, version \
numbers, funding and citations.
- Use only information present in the input. Never invent capabilities.
- British or American spelling as given; do not "correct" the tool's own name.

Reply with JSON only:
{"description": "..."}"""

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


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--jobs", default="categorise",
                    help="comma-separated: categorise,describe,adjudicate,verify-scope")
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
    unknown = jobs - {"categorise", "describe", "adjudicate", "verify-scope"}
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
        tools = [t for t in catalog if t["source"] == "bio.tools" and t.get("description")]
        tools = tools[: args.limit] if args.limit else tools
        print(f"describe: {len(tools)} tools via {args.model} "
              f"({args.workers} workers)")

        def do_describe(t):
            res = cached_call(
                "describe", (t["name"], t["description"]),
                DESCRIBE_SYSTEM, tool_prompt(t),
                lambda r: isinstance(r.get("description"), str)
                and 4 <= len(r["description"].split()) <= 40)
            if not res:
                return None
            return {t["id"]: {"description": res["description"].rstrip("."),
                              "was": t["description"]}}

        out = run_batch(tools, do_describe, "describe")
        proposals["descriptions"] = out
        print(f"  {len(out)} rewritten")

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
