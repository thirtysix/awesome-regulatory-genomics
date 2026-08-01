# Minting a DOI on Zenodo

Not automated, because it needs an account authorisation that cannot be scripted
and it should be a deliberate act rather than a side effect of a build.

`.zenodo.json` supplies the metadata; `CITATION.cff` is what a reader sees on the
repository page. Both are committed and should be kept in step.

## First time

1. Sign in at https://zenodo.org with GitHub.
2. Under **GitHub** in the account settings, flip the switch on
   `thirtysix/awesome-regulatory-genomics`. Only repositories you own appear,
   and the switch must be on **before** the release is created; Zenodo archives
   on the release webhook and cannot pick up an earlier one.
3. Create a release on GitHub. The tag becomes the version, so use `v1.0.0` to
   match `version` in `CITATION.cff`.
4. Zenodo archives the tarball and mints two DOIs: a **concept DOI** that always
   resolves to the newest version, and a **version DOI** for that release.
   **Cite the concept DOI**, which is the one to add to `CITATION.cff` and the
   README badge.

## Each release after that

Tag and release; the archive and a new version DOI happen automatically. The
concept DOI does not change, so nothing else needs editing.

## Keeping the metadata honest

- `version` and `date-released` in `CITATION.cff` should match the tag.
- The catalog count in `.zenodo.json` is deliberately absent: it changes every
  refresh and a stale number in an immutable archive is worse than none.
- Data is CC BY 4.0 and the pipeline is MIT. `.zenodo.json` declares CC BY 4.0
  because the archive is primarily the dataset; the split is explained in its
  `notes` field and in the two LICENSE files.
