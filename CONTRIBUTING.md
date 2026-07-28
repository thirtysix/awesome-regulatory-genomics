# Contributing

Corrections and additions are welcome. Two rules keep this maintainable:

1. **Never edit `README.md`, `data/catalog.json`, `data/catalog.tsv`, or
   `docs/catalog.js`.** All four are generated. Edits are silently overwritten
   on the next build.
2. **Edit the curation files instead**, then run `make curate`.

## If you maintain a tool listed here

Repository links come from three places, and only the last is a guess:

1. recorded in the tool's [bio.tools](https://bio.tools) entry
2. read from a bioconda recipe, Bioconductor, CRAN or PyPI metadata
3. **inferred** by matching against the tool's homepage or a GitHub search,
   then validated against the description

The third kind is marked with a dotted underline on the catalog site and carries
a report button that opens a pre-filled issue. Those are the links most likely to
be wrong, and a correction takes one line in `curation/overlay.yaml`.

Correcting the entry at bio.tools instead fixes it here on the next monthly
refresh, and for everyone else consuming that registry, which is worth more than
correcting it only here.

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
pip install -r requirements.txt      # requests, PyYAML; Python 3.12+
pip install -r requirements-dev.txt  # the above plus pytest, for `make test`

make test             # unit-test the scope, repository and citation rules
make curate           # rebuild from cached data after editing curation/*.yaml
make build-strict     # rebuild on rules alone, ignoring the LLM proposals
make all              # re-select, enrich, resolve links, rebuild  (needs network)
make refresh          # also re-sweep bio.tools  (over an hour end to end)
make links            # resolve preprint DOIs and check every publication link
make audit            # measure recall against curation/benchmark.yaml
make serve            # preview at localhost:8000 (make serve PORT=8420 if taken)
make check            # sanity-check the built catalog
```

Optional stages needing `DEEPINFRA_API_KEY` (see [docs/llm-stage.md](docs/llm-stage.md)):

```bash
make llm               # category, description and scope proposals
make verify-additions  # third-model check on hand-added records
make bench             # compare candidate models on this task
```

### Changing a rule

`pipeline/config.py` holds the patterns and term sets that decide what is in
scope; `select_domain.py`, `resolve_repos.py` and `build.py` apply them. If you
are loosening a rule to admit a tool you think is missing, run `make test`
first. Those tests exist because every regression this project has shipped came
from a reasonable-looking loosening: adding `sequence` and `genome` to the
repository stopword list rejected the correct WebLogo repository, and substring
matching gave CUDA-MEME an unrelated particle-swarm project. A failure there is
usually the rule protecting something, not the test being wrong. CI runs the
same suite on every pull request.

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
