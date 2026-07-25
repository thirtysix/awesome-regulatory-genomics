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
import time

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
                    help="comma-separated: categorise,describe,adjudicate")
    ap.add_argument("--model", default=BULK_MODEL)
    ap.add_argument("--escalate-model", default=QUALITY_MODEL,
                    help="retry model for invalid or low-confidence bulk output")
    ap.add_argument("--no-escalate", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--refresh", action="store_true",
                    help="ignore cached results for the selected jobs")
    args = ap.parse_args()

    api_key = os.environ.get("DEEPINFRA_API_KEY") or os.environ.get("DEEPINFRA_TOKEN")
    if not api_key:
        sys.exit("DEEPINFRA_API_KEY is not set. This stage is optional; the rest of "
                 "the pipeline runs without it.")

    jobs = {j.strip() for j in args.jobs.split(",") if j.strip()}
    unknown = jobs - {"categorise", "describe", "adjudicate"}
    if unknown:
        sys.exit(f"unknown job(s): {', '.join(sorted(unknown))}")

    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    proposals = yaml.safe_load(PROPOSALS.read_text()) if PROPOSALS.exists() else {}
    proposals = proposals or {}
    catalog = json.loads(CATALOG.read_text())["tools"]

    spend, escalations, invalid = 0.0, 0, 0
    valid_keys = set(CATEGORY_KEYS)

    def cached_call(job: str, key_parts: tuple[str, ...], system: str, user: str,
                    validate) -> dict | None:
        """Call with cache, then escalate to the quality model if the result is unusable.

        The bulk model is documented to blank enum fields on a small fraction of
        calls; an unvalidated empty enum silently becomes a permanent
        mis-classification, so an invalid result must escalate rather than be
        stored.
        """
        nonlocal spend, escalations, invalid
        cache_key = f"{job}:{args.model}:{digest(*key_parts)}"
        if cache_key in cache and not args.refresh:
            return cache[cache_key]

        text, cost, _ = call(args.model, system, user, api_key)
        spend += cost
        result = parse_json(text)
        if not (result and validate(result)):
            invalid += 1
            if args.no_escalate:
                return None
            escalations += 1
            saved_model, args.model = args.model, args.escalate_model
            try:
                text, cost, _ = call(args.model, system, user, api_key)
                spend += cost
                result = parse_json(text)
            finally:
                args.model = saved_model
            if not (result and validate(result)):
                return None
        cache[cache_key] = result
        return result

    # --- categorise ---------------------------------------------------------
    if "categorise" in jobs:
        tools = [t for t in catalog if t["source"] == "bio.tools"]
        tools = tools[: args.limit] if args.limit else tools
        out = {}
        print(f"categorise: {len(tools)} tools via {args.model}")
        for i, t in enumerate(tools, 1):
            res = cached_call(
                "categorise", (t["name"], t.get("description") or "",
                               ",".join(t.get("_operations") or [])),
                CATEGORISE_SYSTEM, tool_prompt(t),
                lambda r: isinstance(r.get("categories"), list)
                and all(c in valid_keys for c in r["categories"])
                and isinstance(r.get("in_scope"), bool))
            if not res:
                continue
            derived = set(t["categories"])
            proposed = [c for c in CATEGORY_KEYS if c in set(res["categories"])]
            if set(proposed) != derived or not res["in_scope"]:
                out[t["id"]] = {"categories": proposed,
                                "was": t["categories"],
                                "in_scope": res["in_scope"],
                                "confidence": res.get("confidence", "medium")}
            if i % 50 == 0:
                print(f"  {i}/{len(tools)}  ${spend:.3f}", flush=True)
                CACHE.write_text(json.dumps(cache))
        proposals["categories"] = out
        print(f"  {len(out)} differ from the rule-derived categories")

    # --- describe -----------------------------------------------------------
    if "describe" in jobs:
        tools = [t for t in catalog if t["source"] == "bio.tools" and t.get("description")]
        tools = tools[: args.limit] if args.limit else tools
        out = {}
        print(f"describe: {len(tools)} tools via {args.model}")
        for i, t in enumerate(tools, 1):
            res = cached_call(
                "describe", (t["name"], t["description"]),
                DESCRIBE_SYSTEM, tool_prompt(t),
                lambda r: isinstance(r.get("description"), str)
                and 4 <= len(r["description"].split()) <= 40)
            if res:
                out[t["id"]] = {"description": res["description"].rstrip("."),
                                "was": t["description"]}
            if i % 50 == 0:
                print(f"  {i}/{len(tools)}  ${spend:.3f}", flush=True)
                CACHE.write_text(json.dumps(cache))
        proposals["descriptions"] = out
        print(f"  {len(out)} rewritten")

    # --- adjudicate ---------------------------------------------------------
    if "adjudicate" in jobs:
        rejects = json.loads(REJECTED.read_text())["list"]
        rejects = rejects[: args.limit] if args.limit else rejects
        out = {}
        print(f"adjudicate: {len(rejects)} rejected records via {args.model}")
        for i, t in enumerate(rejects, 1):
            user = (f"Name: {t['name']}\nDescription: {t.get('description') or '(none)'}\n"
                    f"EDAM operations: {', '.join(t.get('operations') or []) or 'none'}\n"
                    f"Filter's reason for exclusion: {t.get('reason', '')}")
            res = cached_call(
                "adjudicate", (t["name"], t.get("description") or ""),
                ADJUDICATE_SYSTEM, user,
                lambda r: isinstance(r.get("should_include"), bool))
            if res and res["should_include"]:
                out[t["biotoolsID"]] = {"name": t["name"],
                                        "reason": res.get("reason", ""),
                                        "filter_said": t.get("reason", "")}
            if i % 50 == 0:
                print(f"  {i}/{len(rejects)}  ${spend:.3f}", flush=True)
                CACHE.write_text(json.dumps(cache))
        proposals["false_negatives"] = out
        print(f"  {len(out)} flagged as wrongly excluded")

    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cache))
    PROPOSALS.write_text(
        "# GENERATED by pipeline/llm_assist.py - proposals, not decisions.\n"
        "# build.py merges this BELOW curation/overlay.yaml, so any hand-written\n"
        "# correction always wins. Review before trusting; promote what you agree\n"
        "# with into overlay.yaml, which is never overwritten.\n"
        f"# model: {args.model}  jobs: {','.join(sorted(jobs))}\n\n"
        + yaml.safe_dump(proposals, sort_keys=True, width=100, allow_unicode=True))

    print(f"\nspend ${spend:.3f} | escalations {escalations} | unusable after retry {invalid - escalations}")
    print(f"-> {PROPOSALS}")


if __name__ == "__main__":
    main()
