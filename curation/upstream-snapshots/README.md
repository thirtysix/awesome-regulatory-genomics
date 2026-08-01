# Pre-edit snapshots of upstream records

The complete record as it stood **immediately before** we changed it, one file
per edit.

bio.tools has no version history and no undo. If a change here turns out to be
wrong, or is disputed, the only way back to the original is a copy we kept
ourselves. The `before:` field in `curation/upstream-log.yaml` records what
changed; these files record everything that did not, which is what a restore
actually needs.

Written by `pipeline/biotools_edit.py`, which refuses to submit an edit unless
the snapshot is on disk first. Tracked in git, never generated from anything.

Naming: `<record>.<date>.before.json`

To restore a record to its snapshot, see `pipeline/biotools_edit.py --restore`.
