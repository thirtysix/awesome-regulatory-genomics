# The optional LLM stage

The pipeline's default path contains **no LLM calls at all**. Harvesting,
selection, enrichment, categorisation, rendering and the coverage audit are
deterministic: HTTP queries, set membership on EDAM terms, compiled regex, and
YAML merges. `make refresh` produces the same catalog from the same inputs, runs
in CI without an API key, and every rule is readable in
[`pipeline/config.py`](../pipeline/config.py).

That is worth keeping. But rules are weakest exactly where judgement is needed,
so there is an optional stage that adds it without giving up reproducibility.

## What it does

| Job | Why rules struggle |
| --- | --- |
| `categorise` | Categories come from EDAM lookups plus ~50 regex patterns. That handles the clear cases and degrades at the margins — a record described as "an integrated platform for ChIP-Seq data interpretation" gets whatever pattern happens to fire, and some land uncategorised. |
| `describe` | bio.tools descriptions are wildly inconsistent: some are one clean sentence, many open with "XYZ is a tool that…", some run to a paragraph with embedded citations. `first_sentence()` is a blunt instrument. |
| `adjudicate` | Around 1,700 records are rejected as out of scope. The boundary has been spot-checked, not read. This re-reads every rejection and flags likely false negatives. |

## The three properties that are preserved

**Proposals, not decisions.** Output goes to `curation/llm_proposals.yaml`.
`build.py` merges it *below* `curation/overlay.yaml`, so any hand-written
correction always wins. A human promotes changes in a reviewable diff; nothing
is silently applied. Only high- and medium-confidence, in-scope proposals are
merged at all — the rest stay in the file for inspection.

**Cached by content hash.** The cache key is a hash of the exact text sent
(name, description, EDAM operations). Re-runs cost nothing and return identical
results; only records whose text actually changed are re-sent. The cache is
committed, so continuous integration never needs a key.

**Fully optional.** With no key and no cache the pipeline still runs end to end.
`make build-strict` ignores the proposals file entirely.

## Choosing a model

Do not pick from a leaderboard. Two facts make measurement necessary:

1. A general intelligence index does not predict performance on a narrow
   structured-classification task. The
   [`deepinfra-models`](file:///home/harl/.claude/skills/deepinfra-models) registry
   records a case where the two highest-ranked open models agreed with a
   mid-ranked one 96–98% of the time on a narrow triage task, surfaced nothing
   it missed, and cost 2–3× more.
2. The cheapest candidate, DeepSeek-V4-Flash, is documented to **blank enum
   fields on roughly 9% of calls** while still filling the free-text ones. This
   task is enum-valued, so that quirk lands squarely on it. An unvalidated empty
   category list silently mis-files a tool forever.

So `pipeline/bench_models.py` measures, on a stratified sample from the built
catalog:

- `json_ok` — fraction of calls returning parseable JSON
- `enum_ok` — fraction returning *only* valid taxonomy keys (the failure mode above)
- `agreement` — Jaccard overlap with the rule-derived categories; a sanity signal, not ground truth, since beating the rules is the point
- `gold_F1` — F1 against hand-labelled tools (the curated seeds, whose categories were written by hand). **This is the number that matters.**
- cost and median latency, extrapolated per 100 tools

```bash
export DEEPINFRA_API_KEY=...
make bench          # writes docs/model-benchmark.md
```

## The cascade

`llm_assist.py` validates every response against the allowed taxonomy keys and
escalates failures to a stronger model rather than storing them:

```
bulk model  ──→ valid enum? ──yes──→ cache and use
                    │
                    no
                    ↓
            escalate to quality model ──→ valid? ──no──→ drop, leave to the rules
```

This is the shape the registry recommends: a cheap over-generous model reading
everything, with a stronger one re-reading only the tail. Defaults are
`--model deepseek-ai/DeepSeek-V4-Flash` and
`--escalate-model deepseek-ai/DeepSeek-V3.1-Terminus`; both are flags, and
per-model call settings (temperature, `top_p`, and critically whether to send
`enable_thinking:false`) are read from the shared registry when it is installed.
Getting that per-model setting wrong is the single most common cause of
"the model returned empty" — forced-thinking models break when told not to
think, and thinking models leak non-JSON when allowed to.

## Cost

At roughly 400 input and 120 output tokens per record over ~1,700 records, a
full categorisation pass costs on the order of **$0.11 with the bulk model** and
about **$0.38 with the quality tier**. Cost is not the deciding factor at this
volume; accuracy on the enum is. Run `make bench` and pick on `gold_F1` and
`enum_ok`.

## Reviewing proposals

```bash
make llm                       # writes curation/llm_proposals.yaml
git diff curation/             # read what changed
make build && make render      # rebuild with proposals merged
make build-strict              # or rebuild ignoring them entirely
```

Anything you agree with should be promoted into `curation/overlay.yaml`, which
is never overwritten. Treat `llm_proposals.yaml` as a machine-generated
suggestion box, not as data.
