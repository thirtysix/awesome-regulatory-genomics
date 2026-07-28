# Roadmap

Nothing here is committed work. It is a record of what is known to be
incomplete, so the next session starts from evidence rather than from memory.

## Done

- [x] Verify the dissertation table against its intermediates (0 mismatches)
- [x] Reproducible harvest of bio.tools with recall and precision separated
- [x] Tiered selection: strong/weak EDAM operations, hard/soft exclusions, text escape hatch
- [x] Recall benchmark against a hand-written list of standard tools (89/89)
- [x] Repository resolution from bioconda, Bioconductor, CRAN, PyPI, homepage, GitHub search
- [x] Publication links: preprint upgrade via Crossref, verification of hand-written identifiers
- [x] Optional LLM stage for categories and descriptions, model chosen by measurement
- [x] Two-model gate on removals, third-model check on additions
- [x] Searchable site with per-column filters and sortable link columns
- [x] Published: repository public, GitHub Pages live

## Committed, in the agreed order

Chosen 2026-07-28. The aim of this block is to be *more complete and better
evidenced than bio.tools*, which is the only defensible reason for this resource
to exist. Curation depth (featured entries, superseded markers, task-oriented
paths) is deliberately deferred until after it.

- [x] **1. Unit tests for the rule functions.** Done 2026-07-28. 42 tests in
      `tests/`, run by `make test` and by `.github/workflows/test.yml` on every
      push and pull request, offline and in under a second. They cover
      `select_domain.classify()`, `resolve_repos.validate()` and
      `build.primary_identifier()`, using the real records that motivated each
      rule: the `cudameme`/`cudamemeticalgorithm` prefix collision, the WebLogo
      stopword failure, MEDUSA's cross-field name clash, SEProm's lab
      boilerplate, TOBIAS's preprint-before-paper ordering, and FiMO as the
      backstop against the name collision documented in `docs/provenance.md`.
      CI also rebuilds from committed data and fails if the outputs drift.

      *Found a real bug.* `norm_name()` stripped `+`, so "SCENIC+" normalised to
      "scenic" and the hand-written SCENIC+ seed was skipped as a duplicate of
      SCENIC, a different tool. `+` is now spelled out. The catalog is
      byte-identical (bio.tools' own `scenicplus` record was already carrying
      the tool), but the latent failure is gone and the convention is tested.

- [x] **2. Discovery beyond bio.tools.** Done 2026-07-28.
      `pipeline/discover_registries.py` (`make discover`) sweeps Bioconductor's
      `VIEWS` and the Galaxy ToolShed and puts every candidate through
      `select_domain.classify()`, the same filter the bio.tools records face.
      A registry's own taxonomy supplies the corroborating signal EDAM topics
      normally provide: `biocViews: ChIPSeq` maps to the EDAM topic `ChIP-seq`.
      Scanned 2,418 Bioconductor packages and 7,772 ToolShed repositories,
      found 161 in-domain candidates absent from the catalog, and **46 were
      promoted into `seeds.yaml` by hand**, taking the catalog from 1,800 to
      1,846. Among them: AlphaGenome, SnapATAC2, Cicero, Chromap, MotifDb,
      epic2, VIPER and RTN, none of which bio.tools indexes.

      Two things were needed to make the Galaxy source usable. The ToolShed
      publishes one repository per *wrapper*, so candidates sharing a homepage
      are merged (AlphaGenome arrived five times); and it has no domain
      taxonomy, so its candidates must clear a strong text pattern unaided.
      That cut Galaxy's raw 90 candidates to 37 real ones.

      **bioconda was evaluated and rejected as a discovery source.** Its public
      index gives names without summaries and the API that carried them now
      returns 401, so admitting from it would mean matching on a name alone,
      which is the failure this project rejects everywhere else. It remains in
      use for resolving repositories of tools already known.

- [ ] **2b. Follow-up: the remaining 115 candidates.** `docs/registry-discovery.md`
      still lists them. Most of the untaken ones are Hi-C/TAD and DNA
      methylation tools, which raises a scope question rather than a curation
      one: neither is currently named in `pipeline/config.py`'s scope, but 3D
      contact and methylation sit close to the chromatin boundary. Decide the
      boundary first, then promote in a batch. Also run `make repos` to resolve
      repositories for the 46 new seeds; only the GitHub-hosted ones carry a
      code link so far.

- [x] **3. Literature-driven discovery.** Done 2026-07-28.
      `pipeline/discover_literature.py` (`make discover-lit`) exploits the
      naming convention of the field: tool papers are titled *NAME: what it
      does*, which turns tool-name extraction into a regular expression. The
      name comes from before the colon, the evidence from after it, and the
      evidence goes through `select_domain.classify()` like everything else.
      18 title-scoped Europe PMC queries over 10,926 papers yielded 673 named
      in-domain tools, 437 of them absent from the catalog, and **47 were
      promoted**. The catalog is now 1,893 tools, up from 1,800 at the start.

      Queries are title-scoped deliberately: an abstract-scoped query returns
      every paper that merely *uses* a tool, and the name before the colon is
      then the wrong name. The 236 extracted tools already in the catalog are
      the control, and they are the field's canonical entries (JASPAR, STREME,
      HOCOMOCO, iRegulon, ChIPpeakAnno), which is evidence the extraction is
      finding this population rather than a neighbouring one.

      Better than the registry sweep in one respect: every row carries a DOI, a
      PMID and a year, so a promoted seed gets a real publication and citation
      count instead of a bare link.

      *Found a second bug.* `from_seed()` hard-coded `citations: None`, so a
      curated tool showed no count even with its DOI in the citation cache.
      FIMO, one of the most-cited papers in the field, displayed blank. Seeds
      now take the same citation path as harvested records, including the
      suite-paper suppression. 80 of 129 seeds gained a count; FIMO reads 4,992.

      Known noise: the title convention also matches assay and protocol papers
      ("ChIP-chip", "ChIPmentation") and the occasional biological element
      ("R11"). That is acceptable in a review queue and is documented in the
      report.

- [x] **4. Harden the benchmark.** Done 2026-07-28. A second tier takes
      `curation/benchmark.yaml` from 89 entries to 168, across ten new groups
      covering motif comparison, nucleosome and chromatin state, single-cell,
      and harder tiers of the existing categories. **Recall fell from 100% to
      137/168 (82%)**, which is the point: the number discriminates again, and
      `docs/coverage.md` now lists 31 concrete, diagnosed gaps.

      *Found a third bug, in the audit itself.* `probe_biotools()` decides
      whether a miss is "in bio.tools but unharvested" or "absent from
      bio.tools" by matching on the **name**, and reported it as settled fact.
      Of the eight records it offered, three were different tools wearing the
      same name: `Thor` is a spatial-transcriptomics package rather than the
      RGT differential peak caller, and `inps` and `maestro` are both
      protein-stability predictors. The same failure as FiMO, in the tool whose
      job is to find failures. The diagnosis now says the match is on name
      alone and must be opened before acting.

      Five verified IDs were added to `SEED_BIOTOOLS_IDS` (`danpos`, `dbsuper`,
      `ggseqlogo`, `logolas`, `rgreat`); they take effect on the next
      `make refresh`, since fetch-by-ID happens during harvest.

- [ ] **4b. Follow-up: work the 31 misses down.** Most are genuinely absent
      from bio.tools and belong in `seeds.yaml`: Tomtom, MoSBAT, universalmotif,
      MEME-ChIP, HMMRATAC, Wellington, CellOracle, Pando, FigR, deltaSVM,
      dbSUPER and the rest. That is curation work rather than pipeline work, so
      it sits with the deferred block below. Re-run `make audit` after each
      batch; treat a fall in recall as a blocker.

- [x] **5. Surface package availability.** Done 2026-07-28. `_registries` was
      collected and never displayed. It is now an *Install* column on the
      catalog site (sortable, filterable, one short link per registry) and a
      `registries` field in `data/catalog.tsv`.

      Coverage was widened at the same time, reusing the Bioconductor data the
      discovery sweep already caches: `discover_registries.py` now also matches
      packages to tools the catalog *already has*, taking availability from 219
      tools to **278**, with Bioconductor alone going 168 to 227. The match
      requires the package description to share at least two content words with
      the tool's, the same bar `resolve_repos.validate()` applies, because
      matching a package on its name is the `medusa` failure again.

      *A build-order trap worth remembering.* `build.py` writes
      `data/catalog.json` before it writes the TSV, so a row mutation placed
      between the two lands in the TSV and silently not in the JSON, and
      therefore not on the site. The symptom was the new links appearing in the
      TSV while the site stayed at 219.

- [x] **6. Homepage liveness.** Done 2026-07-28. `pipeline/check_homepages.py`
      (`make check-links`) checked all 1,837 distinct homepages: **1,384 ok
      (75%), 131 dead, 283 unreachable, 20 rate-limited, 19 blocked**.

      Outcomes are graded rather than binary, because the DOI checker learned
      the cost of the alternative when it reported 152 broken DOIs of which 151
      were rate-limiting. Only 404 and 410 count as `dead`; a timeout is
      `unreachable` and is not asserted anywhere the reader sees, since a slow
      institutional host looks identical to a departed one. Requests are spaced
      one second per host, because a single lab often hosts a dozen entries
      here. Results are cached with the date obtained, so `--max-age` decides
      what to recheck rather than refetching 1,837 URLs.

      The 131 dead links are struck through on the catalog site. Six of them
      are deleted *repositories* rather than homepages, which needed the check
      to compare canonicalised links: PROBC's record holds
      `http://www.github.com/seferlab/probc` and `https://github.com/seferlab/probc`
      for the same dead repository.

- [x] **7. Fill the missing fields.** Done 2026-07-28.
      `pipeline/fill_metadata.py` (`make fill-metadata`) fills what is
      derivable from data already held, and marks it rather than merging it
      silently.

      **Year: 1,052 to 1,800 of 1,893 (95%).** 729 publications were looked up
      in OpenAlex and 723 resolved. An empty answer is cached as an answer, so
      a missing year is not re-asked on every run.

      **Licence: 772 to 857.** Where a tool declares none but its resolved
      repository has one, the repository's is used and `license_source` records
      which it is. A repository licence is weaker evidence than a declared one,
      so the two are distinguishable rather than merged.

      **Citations for seeds** were fixed as part of item 3: 80 of 129 seeds now
      carry a count, FIMO among them at 4,992.

- [ ] **7b. Follow-up: the 144 preprints and the remaining 1,036 licences.**
      The preprints are the known-hard case already documented below: Crossref
      records no published version, and loose title matching was tried and
      rejected. The licences are mostly genuinely unstated upstream rather than
      derivable, so this needs contributions, not code.

## Also outstanding

- [ ] **Work through the unsearched records.** ~940 of the repo-less records were
      never reached by GitHub search, because each run is budget-capped at 80 to
      stay well inside the 30/min limit. `make repos` is incremental and caches
      both hits and misses, so repeated runs converge without ever approaching a
      rate limit.

- [ ] **Human review of the two backlogs.** `docs/repo-review.md` holds 235
      candidates and `docs/addition-review.md` 147 scope disputes, all carrying
      model opinions only. Sampling suggests roughly a quarter of the closest
      repo near-misses are genuine.

- [ ] **Watch the first automated refresh** (1 August 2026, 04:00 UTC). It opens
      a PR rather than committing. Review the `data/catalog.tsv` diff; treat a
      drop in `docs/coverage.md` recall as a blocker rather than noise.

## Scope widening, 2026-07-28

Batch 1 plus the QTL half of batch 2, chosen from a sizing pass over the reject
pile and the unpromoted discovery candidates. **1,893 to 1,951 tools**, and five
new categories.

- [x] **DNA methylation** (96 tools). A genuine widening: 54 records were being
      rejected as `no-match`, since nothing admitted them.
- [x] **3D genome & chromatin interactions** (72). Mostly a *category* for tools
      already present. Nothing was being rejected.
- [x] **Histone modifications** (33) and **Reporter assays** (4). Both were
      already in scope; they only lacked anywhere to go.
- [x] **Molecular QTL** (19). A widening; 8 records were rejected as `no-match`.

The benchmark gained a third tier for the new areas, written before looking at
what the rules admitted: 168 to 221 entries, recall 82% to **153/221 (69%)**.

**Three vocabulary traps, all found by checking what the first run admitted:**

  `Hi-C` is a technology used by two fields. In the strong tier it admitted
  "A high-quality genome sequence of alkaligrass", a genome-announcement paper
  that used Hi-C to scaffold. It now needs a corroborating domain topic, and
  genome-announcement papers are hard-excluded outright.

  `Loop modelling`, `Gene expression QTL analysis` and `Bisulfite mapping` look
  like decisive EDAM operations and are not. bio.tools attaches them to RNA
  secondary structure (CRISPRtracrRNA), protein conformation (Rascore),
  expression atlases (ZFIN, Mouse Atlas) and general commercial suites (CLC,
  Genedata). Topic corroboration was not enough either, because the domain
  topics are applied liberally. They admit nothing; the text patterns reach
  every genuine case.

  `methylation` spans DNA, RNA and protein. Only DNA-specific wording admits.
  A side effect: 12 RNA-modification tools (m6A, m5C, pseudouridine) that had
  been in the catalog left with this pass, which is a precision gain.

- [ ] **Follow-up: 68 benchmark misses**, concentrated in the new areas. Juicer,
      cooler, HiC-Pro, MPRAnalyze, coloc and SuSiE are absent from bio.tools and
      belong in `seeds.yaml`. That is curation work.

## Install routes from repository READMEs, 2026-07-28

- [x] `pipeline/resolve_installs.py` (`make installs`) reads PyPI, conda, CRAN,
      Bioconductor and Docker routes off each tool's own repository README.
      **Install coverage 278 to 413 tools.** A badge on a project's own
      repository is the project stating where it ships, which is far better
      evidence than the name match `discover_registries.py` uses.

      Guarded, because a README also advertises everybody else's packages:
      a route is accepted only when the package name matches the tool or its
      repository. 134 tools found package names that did not match and are
      listed in `docs/install-review.md`. Galaxy repositories are the
      systematic case, since every one says `pip install planemo`.

      Parsing traps worth keeping: `pip install -r requirements.txt` names a
      file, `pip install --editable .` and `-v` put flags in the capture group,
      `mamba install --yes -c conda-forge -c bioconda x` needs the flag
      consumer to refuse flag-shaped arguments, and a `ghcr.io/...` image is
      not on Docker Hub, so formatting one as such fabricates a 404.

- [ ] **Follow-up: the 134 held routes.** RSAT is the interesting one: its
      repository is `rsat-code` and its conda package is `rsat-core`, one letter
      apart and genuinely different words, so the guard correctly refuses it.

## Full-bleed layout and a statistics panel, 2026-07-28

- [x] The content column was capped at 1180px while the table needs ~1240px, so
      eleven columns always scrolled sideways. The page is now full bleed and the
      table fits unaided from about 1180px up; below that its wrapper still
      scrolls, and the page itself never does. Prose in the footer keeps a
      110ch measure, because full bleed is right for a table and wrong for text.

- [x] A statistics panel above the table: four stat tiles (tools shown, source
      repository, installable, dead links) and four column charts (publication
      year, repository last updated, citations, stars). Collapsible, and it
      **reflects the current filter**, which is the point: clicking *Peak
      calling* and reading the year chart answers "when was this subfield
      written, and is it still maintained".

      Built to the data-viz method rather than to taste. Every chart is one
      series, so bar length carries the magnitude and colour carries nothing;
      shading bars darker-where-bigger would encode the same fact twice. The
      hue is the validated series-1 blue, checked with the palette validator
      against this site's actual surfaces (`#ffffff` and `#14171a`) in both
      modes rather than eyeballed. Marks follow the spec: 24px cap, 4px rounded
      data-end square at the baseline, a 2px surface gap between neighbours,
      hairline solid gridlines at zero and the top of the scale only, one direct
      label on the tallest column and never a number on every bar, axis text in
      the muted ink token rather than the series colour, and a hover tooltip
      whose hit target is the whole band rather than the mark.

      No dependency and no build step, in keeping with the rest of the site: the
      SVG is generated in the page. Charts are drawn at a measured pixel width
      instead of being scaled by a viewBox, so a resize redraws them rather than
      stretching the type.

## Deferred: curation depth

Queued behind the block above, by decision rather than by oversight.

- [ ] **Expand the featured set.** 19 of 1,800 entries are featured. A registry
      can list; only a curated list can say which tool to reach for. This is the
      largest single difference between this resource and a data dump.
- [ ] **Mark superseded and abandoned tools.** 186 repositories have had no push
      since before 2021. "Use X instead" is information bio.tools cannot give.
- [ ] **Task-oriented entry points.** Categories answer *what is this*; users
      arrive with *what do I do*.

## Considered and deliberately not done

- **Regenerating the dissertation table from this pipeline.** It stands as
  published and remains citable; the catalog supersedes it going forward.
- **Loose title matching for preprints.** Rejected above; a dated link beats a
  wrong one.
- **Rewriting history on the other 18 public repos** to scrub the personal email.
  471 commits, and the address is already public on the Transcription paper.
  GitHub's block-push protection now prevents recurrence, verified with a real
  rejected push.

## Speculative

- **An awesome-list template.** The reusable part is the discipline, not the tool
  list: separating recall from precision, requiring two independent models to
  remove anything, marking inferred data as inferred, and measuring recall
  against a benchmark. Roughly 60% of the code is bio.tools- and EDAM-specific,
  so this means extracting a source-agnostic spine into a separate repository
  rather than contorting this one.
