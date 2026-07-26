PY ?= python3
PORT ?= 8000        # override if 8000 is taken: make serve PORT=8420
PIPELINE := $(PY) pipeline

.PHONY: all harvest select enrich links build render audit curate refresh clean check serve llm bench verify-additions repos

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

## find source repositories bio.tools does not record (validated)
repos:
	$(PIPELINE)/resolve_repos.py

## resolve preprint links to the published version and check every DOI
links:
	$(PIPELINE)/resolve_pubs.py

## measure recall against curation/benchmark.yaml
audit:
	$(PIPELINE)/audit_coverage.py --probe

## OPTIONAL: LLM proposals for categories, descriptions and the reject pile.
## Needs DEEPINFRA_API_KEY. Writes curation/llm_proposals.yaml for review;
## `make build` merges it BELOW the hand-written overlay. Cached by content
## hash, so re-runs are free and CI never needs a key.
llm:
	$(PIPELINE)/llm_assist.py --jobs categorise,describe,adjudicate,verify-scope

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

check:
	$(PY) -c "import json,sys; c=json.load(open('data/catalog.json')); \
	  assert c['meta']['count']>0; \
	  ids=[t['id'] for t in c['tools']]; assert len(ids)==len(set(ids)), 'duplicate ids'; \
	  print('catalog ok:', c['meta']['count'], 'tools')"

clean:
	rm -f data/catalog.json data/catalog.tsv docs/catalog.js docs/index.html README.md
