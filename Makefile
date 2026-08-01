PY ?= python3
PORT ?= 8000        # override if 8000 is taken: make serve PORT=8420
PIPELINE := $(PY) pipeline

.PHONY: all harvest select enrich links build render audit curate refresh clean check test serve llm bench verify-additions repos repos-revalidate discover discover-refresh discover-lit discover-pubs check-links fill-metadata installs audit-scope recheck-pubs search-pubs verify-upstream biotools-edit

## build everything from the existing sweep (no network beyond enrichment)
all: select enrich repos links build render audit

## full refresh, including a new bio.tools sweep (~10 min)
refresh: harvest all

harvest:
	$(PIPELINE)/harvest.py --refresh

select:
	$(PIPELINE)/select_domain.py

enrich:
	$(PIPELINE)/enrich.py

## rebuild the catalog and outputs from cached enrichment (fast, offline)
build:
	$(PIPELINE)/build.py --apply-scope

render:
	$(PIPELINE)/render.py

## find source repositories bio.tools does not record (validated).
## GitHub search is throttled to ~17 req/min against a 30/min ceiling and
## capped per run; raise the budget across several runs rather than in one.
repos:
	$(PIPELINE)/resolve_repos.py --search-budget 80

## re-apply the current validation rules to cached candidates (core API only)
repos-revalidate:
	$(PIPELINE)/resolve_repos.py --revalidate

## resolve preprint links to the published version and check every DOI
links:
	$(PIPELINE)/resolve_pubs.py

## check that the tools' own homepages still resolve. Nearly half the catalog
## has no repository, only a homepage, and academic URLs rot. Graded outcomes:
## only a 404/410 counts as dead. Cached, so re-runs only recheck stale entries.
check-links:
	$(PIPELINE)/check_homepages.py

## read install routes (PyPI/conda/CRAN/Bioconductor/Docker) off each tool's
## own repository README. Better evidence than a name match in a registry, and
## it is how MACS, pySCENIC and RSAT get install links bio.tools never records.
installs:
	$(PIPELINE)/resolve_installs.py

## fill fields derivable from data already held: publication year from
## OpenAlex, licence from the resolved repository. Both are marked, neither
## overwrites a stated value.
fill-metadata:
	$(PIPELINE)/fill_metadata.py

## measure recall against curation/benchmark.yaml
audit:
	$(PIPELINE)/audit_coverage.py --probe

## find in-domain tools bio.tools does not index, from registries that carry
## their own domain taxonomy. Writes docs/registry-discovery.md for review;
## nothing is added to the catalog automatically. Cached, so re-runs are
## offline; use `make discover-refresh` to re-fetch.
discover:
	$(PIPELINE)/discover_registries.py

discover-refresh:
	$(PIPELINE)/discover_registries.py --refresh

## find tools announced in the literature but indexed nowhere, using the
## "NAME: what it does" title convention of tool papers. Writes
## docs/literature-discovery.md for review. Every row carries a DOI and a year.
discover-lit:
	$(PIPELINE)/discover_literature.py

## find the paper for a tool bio.tools records none for, by reading the tool's
## OWN declared citation (Bioconductor citation page, CITATION.cff, codemeta,
## README) rather than searching the literature by name. Writes
## docs/publication-discovery.md for review; promote rows into overlay.yaml
## (bio.tools records) or seeds.yaml (curated entries).
discover-pubs:
	$(PIPELINE)/discover_pubs.py

## OPTIONAL: LLM proposals for categories, descriptions and the reject pile.
## Needs DEEPINFRA_API_KEY. Writes curation/llm_proposals.yaml for review;
## `make build` merges it BELOW the hand-written overlay. Cached by content
## hash, so re-runs are free and CI never needs a key.
llm:
	$(PIPELINE)/llm_assist.py --jobs categorise,describe,adjudicate,verify-scope

## OPTIONAL: re-read records admitted on one unreliable EDAM operation.
## Writes docs/scope-audit.md; promote rows into overlay.yaml: exclude.
audit-scope:
	$(PIPELINE)/llm_assist.py --jobs audit-scope

## OPTIONAL: re-derive the paper for records flagged as carrying the wrong one,
## by asking each tool what to cite. Deterministic, no API key.
recheck-pubs:
	$(PIPELINE)/discover_pubs.py --recheck-flagged

## Re-check that changes contributed upstream are still in place. Read-only,
## no token needed. bio.tools keeps no contribution history, so
## curation/upstream-log.yaml is the only record that a change was ever made.
verify-upstream:
	$(PIPELINE)/verify_upstream.py

## Edit one bio.tools record safely: snapshots the original first and refuses
## to proceed without it, then verifies by GET because a write can return 500
## and still succeed. Needs BIOTOOLS_TOKEN. Use --dry-run first.
biotools-edit:
	@echo 'Usage: $(PIPELINE)/biotools_edit.py --record ID --set field=value [--dry-run]'
	@echo '       $(PIPELINE)/biotools_edit.py --record ID --restore'

## OPTIONAL, LAST RESORT: search for the paper when the tool itself names none,
## and have a model adjudicate the candidates. Needs DEEPINFRA_API_KEY.
search-pubs:
	$(PIPELINE)/search_pubs.py

## OPTIONAL: third-model check on records added by hand or by a text rule
verify-additions:
	$(PIPELINE)/verify_additions.py

## OPTIONAL: benchmark candidate models on this task before choosing one
bench:
	$(PIPELINE)/bench_models.py --n 40

## deterministic build, ignoring any LLM proposals
build-strict:
	$(PIPELINE)/build.py --no-llm

## regenerate README + site only, after editing curation/*.yaml
curate: build render

## serve the site locally (make serve PORT=8420 if 8000 is in use)
serve:
	$(PY) -m http.server $(PORT) --directory docs

## unit-test the rule functions that decide scope, repository links and
## citations. Offline and fast; run it before touching pipeline/config.py.
test:
	$(PY) -m pytest tests/ -q

check:
	$(PY) -c "import json,sys; c=json.load(open('data/catalog.json')); \
	  assert c['meta']['count']>0; \
	  ids=[t['id'] for t in c['tools']]; assert len(ids)==len(set(ids)), 'duplicate ids'; \
	  print('catalog ok:', c['meta']['count'], 'tools')"

clean:
	rm -f data/catalog.json data/catalog.tsv docs/catalog.js docs/index.html README.md
