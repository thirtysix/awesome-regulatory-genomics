"""Small helpers for writing Markdown that survives the content it contains."""
from __future__ import annotations

import re


def cell(value: object, limit: int = 0) -> str:
    """Make a value safe to drop into a Markdown table cell.

    A pipe inside a cell silently ends the column, so a row carrying a regex
    like ``\\bsc(ATAC|-ATAC)`` or a tool named "A | B" corrupts the table from
    that point on. Newlines do the same to the row. Both appear in real data
    here: the selection reasons are regex patterns, and bio.tools descriptions
    regularly contain " | ".
    """
    text = "" if value is None else str(value)
    text = re.sub(r"\s*\n\s*", " ", text).replace("|", "\\|")
    if limit and len(text) > limit:
        text = text[: limit - 1].rstrip() + "…"
    return text
