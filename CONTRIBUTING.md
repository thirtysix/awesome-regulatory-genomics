# Contributing

Corrections and additions are welcome. Two rules keep this maintainable:

1. **Never edit `README.md`, `data/catalog.json`, `data/catalog.tsv`, or
   `docs/catalog.js`.** All four are generated. Edits are silently overwritten
   on the next build.
2. **Edit the curation files instead**, then run `make curate`.

## Adding a tool

First check whether it is already in [bio.tools](https://bio.tools). If it is
and it is missing here, the selection filter is at fault. Please open an issue
with the bio.tools ID so the rule can be fixed rather than the symptom patched.

If it is genuinely absent from bio.tools, add it to
[`curation/seeds.yaml`](curation/seeds.yaml):

```yaml
  - name: MyTool
    url: https://example.org/mytool
    repo: owner/mytool                 # optional, GitHub owner/name
    description: One sentence, no trailing full stop
    categories: [motif-discovery, tfbs-prediction]
    tags: [deep-learning]              # optional
    doi: 10.1093/nar/gkxxxx            # or pmid:
```

Valid `categories` keys are listed in `CATEGORIES` in
[`pipeline/config.py`](pipeline/config.py). A tool can hold several, and most do.

Adding it to bio.tools as well is more valuable than adding it here, since
every downstream consumer of that registry benefits.

## Fixing a category or description

Add an entry under `corrections` in
[`curation/overlay.yaml`](curation/overlay.yaml), keyed by bio.tools ID:

```yaml
corrections:
  mytool:
    note: why this override exists
    categories: [motif-scanning]       # replaces the derived list
    add_categories: [peak-annotation]  # or extends it
```

## Proposing a featured tool

`featured` in `overlay.yaml` controls what appears in the README. The bar is
deliberately not "well cited":

- it is the tool a newcomer to this sub-problem should try first, **or**
- it is a de-facto standard the literature assumes you know, **or**
- it is the only maintained option in its niche.

The value is the one-line description shown in the README. Write it as a
reason, not a restatement of the name.

## Removing something out of scope

Add it under `exclude` in `overlay.yaml` with a reason. Please also check
[`data/raw/rejected.json`](data/raw/rejected.json) first: if a whole class of
tools is wrongly admitted, the fix belongs in `pipeline/config.py`
(`STRONG_OPERATIONS`, `WEAK_OPERATIONS`, `EXCLUDE_TEXT_PATTERNS`), not in a
long exclusion list.

## Running the pipeline

```bash
pip install requests pyyaml

make curate     # rebuild from cached data after editing curation/*.yaml
make all        # re-select, re-enrich, rebuild  (needs network)
make refresh    # also re-sweep bio.tools        (~10 min)
make serve      # preview the site at localhost:8000
make check      # sanity-check the built catalog
```

Enrichment uses the GitHub API. It works unauthenticated at 60 requests/hour,
but set `GITHUB_TOKEN` (or run `gh auth login`) for 5,000/hour. Both the GitHub
and OpenAlex responses are cached under `data/cache/`, so repeat runs are cheap
and mostly offline.

## Scope

In scope: transcription-factor binding and motifs, promoters and enhancers,
footprinting, ChIP/ATAC peak calling and annotation, chromatin accessibility and
nucleosomes, gene-regulatory networks, regulatory variant effect, and the
databases serving those.

Out of scope: general sequence alignment and assembly, RNA structure, protein
structure and docking, mass spectrometry, and generic differential-expression
tooling, even when they share vocabulary like "motif" or "peak".
