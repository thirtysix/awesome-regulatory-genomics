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

## Next, roughly in order of value

- [ ] **Unit tests for the rule functions.** `select_domain.classify()`,
      `resolve_repos.validate()` and `build.primary_identifier()` are where every
      bug this project has had actually lived, and nothing tests them directly.
      `make check` only validates the output shape; the 89/89 benchmark is real
      but coarse. A contributor loosening a regex currently has no safety net.
      This is the single highest-value item.

- [ ] **Work through the unsearched records.** ~940 of the repo-less records were
      never reached by GitHub search, because each run is budget-capped at 80 to
      stay well inside the 30/min limit. `make repos` is incremental and caches
      both hits and misses, so repeated runs converge without ever approaching a
      rate limit.

- [ ] **Human review of the two backlogs.** `docs/repo-review.md` holds 235
      candidates and `docs/addition-review.md` 147 scope disputes, all carrying
      model opinions only. Sampling suggests roughly a quarter of the closest
      repo near-misses are genuine.

- [ ] **The 135 preprint links.** Crossref records no published version for them.
      Title matching was tested and rejected: preprint titles routinely change on
      publication, so strict matching finds almost nothing and loose matching
      attaches wrong papers. Hand-correction via `overlay.yaml` works, as done
      for Signac and ArchR.

- [ ] **Watch the first automated refresh** (1 August 2026, 04:00 UTC). It opens
      a PR rather than committing. Review the `data/catalog.tsv` diff; treat a
      drop in `docs/coverage.md` recall as a blocker rather than noise.

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
