"""Transparent JSON read/write, gzipping when the path ends in ``.gz``.

The raw sweep and the enriched records are ~23 MB of JSON, which compresses
about eight-fold. Storing them gzipped keeps the repository small enough to
clone comfortably while still committing every intermediate, so a contributor
can rebuild the catalog offline and diff exactly what upstream changed.
"""
from __future__ import annotations

import gzip
import json
import re
from pathlib import Path
from typing import Any

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def redact_emails(obj: Any) -> Any:
    """Replace third-party contact addresses in harvested data.

    bio.tools records carry maintainer contact addresses in `credit[].email`,
    and a few more appear in free text. The harvest held roughly 1,800 distinct
    addresses and this repository is public, so committing them republishes
    other people's contact details in bulk. The licence permits it and nobody
    here uses the field, which makes redaction free.

    Applied at the write boundary rather than as a cleanup pass, because a
    cleanup pass is undone by the next `make refresh`.
    """
    if isinstance(obj, dict):
        return {k: ("<redacted>" if k == "email" and isinstance(v, str) and v
                    else redact_emails(v)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact_emails(v) for v in obj]
    if isinstance(obj, str):
        return EMAIL_RE.sub("<redacted>", obj)
    return obj


def read_json(path: Path) -> Any:
    if str(path).endswith(".gz"):
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            return json.load(fh)
    return json.loads(path.read_text())


def write_json(path: Path, obj: Any, indent: int | None = 1) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    obj = redact_emails(obj)
    if str(path).endswith(".gz"):
        # mtime=0 keeps the output byte-identical across runs, so an unchanged
        # catalog produces an empty git diff instead of a spurious one.
        with gzip.GzipFile(path, "wb", compresslevel=9, mtime=0) as raw:
            raw.write(json.dumps(obj, indent=indent).encode("utf-8"))
    else:
        path.write_text(json.dumps(obj, indent=indent))
