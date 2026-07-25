"""Transparent JSON read/write, gzipping when the path ends in ``.gz``.

The raw sweep and the enriched records are ~23 MB of JSON, which compresses
about eight-fold. Storing them gzipped keeps the repository small enough to
clone comfortably while still committing every intermediate, so a contributor
can rebuild the catalog offline and diff exactly what upstream changed.
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    if str(path).endswith(".gz"):
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            return json.load(fh)
    return json.loads(path.read_text())


def write_json(path: Path, obj: Any, indent: int | None = 1) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if str(path).endswith(".gz"):
        # mtime=0 keeps the output byte-identical across runs, so an unchanged
        # catalog produces an empty git diff instead of a spurious one.
        with gzip.GzipFile(path, "wb", compresslevel=9, mtime=0) as raw:
            raw.write(json.dumps(obj, indent=indent).encode("utf-8"))
    else:
        path.write_text(json.dumps(obj, indent=indent))
