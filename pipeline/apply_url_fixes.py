#!/usr/bin/env python3
"""Fold a hand review of the broken-link report into curation/overlay.yaml.

Decisions arrive as a json map of tool name -> {"verdict": ..., "url": ...},
from the review page's Copy button. Three verdicts:

    replace   point the entry at the reviewed url
    drop      the tool is real and its url is not; record that rather than
              keeping a link that serves somebody else's website
    keep      the checker was wrong; the current url stands

Written into `corrections:`, which build.py merges over the harvested row, so
the fix survives the next `make refresh` - editing data/catalog.json would not.
Appended as text, never round-tripped through a yaml dumper: overlay.yaml is a
comment-heavy audit trail and a dumper would silently reflow it.

    python pipeline/apply_url_fixes.py --decisions review.json          # dry run
    python pipeline/apply_url_fixes.py --decisions review.json --apply
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
OVERLAY = ROOT / "curation" / "overlay.yaml"
CATALOG = ROOT / "data" / "catalog.json"


def yaml_str(s: str) -> str:
    s = re.sub(r"\s+", " ", str(s or "")).strip().rstrip(".")
    if not s:
        return '""'
    reserved = {"y", "n", "yes", "no", "true", "false", "on", "off", "null", "~"}
    if (re.match(r"^[A-Za-z0-9]", s) and not re.search(r"[:#\[\]{}&*!|>'\"%@`,]", s)
            and s.lower() not in reserved
            and not re.fullmatch(r"[-+]?[0-9._]+([eE][-+]?[0-9]+)?", s)):
        return s
    return "'" + s.replace("'", "''") + "'"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--decisions", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    marks = json.loads(Path(args.decisions).read_text())
    cat = json.loads(CATALOG.read_text())
    cat = cat["tools"] if isinstance(cat, dict) else cat
    by_name = {t["name"]: t for t in cat}
    doc = yaml.safe_load(OVERLAY.read_text()) or {}
    have = doc.get("corrections") or {}

    stamp = dt.date.today().isoformat()
    lines, skipped = [], []
    for name, mark in marks.items():
        verdict = mark.get("verdict") if isinstance(mark, dict) else mark
        t = by_name.get(name)
        if t is None:
            skipped.append((name, "not in the catalog")); continue
        key = t.get("id")
        if not key:
            skipped.append((name, "no catalog id")); continue
        if key in have:
            skipped.append((name, f"'{key}' already has a correction; merge it by hand")); continue
        if verdict == "keep":
            continue
        if verdict == "replace":
            url = (mark or {}).get("url")
            if not url:
                skipped.append((name, "replace with no url")); continue
            lines.append(f"  {key}:\n"
                         f"    homepage: {url}\n"
                         f"    note: {yaml_str(f'url reviewed {stamp}; the previous one served a different site')}")
        elif verdict == "drop":
            lines.append(f"  {key}:\n"
                         f"    homepage: \"\"\n"
                         f"    note: {yaml_str(f'url reviewed {stamp} and removed; no page for this tool was found')}")
        else:
            skipped.append((name, f"unknown verdict {verdict!r}"))

    print(f"decisions read : {len(marks)}")
    print(f"  to write     : {len(lines)}")
    print(f"  kept as-is   : {sum(1 for m in marks.values() if (m.get('verdict') if isinstance(m, dict) else m) == 'keep')}")
    if skipped:
        print(f"  skipped      : {len(skipped)}")
        for n, why in skipped:
            print(f"      {n[:26]:28s} {why}")
    if not lines:
        print("nothing to write"); return

    block = (f"\n  # --- urls reviewed by hand {stamp} "
             + "-" * 34 + "\n"
             + "  # Each of these served a page that was not the tool: a re-registered\n"
             + "  # domain, a different tool of the same name, or a lab index that no\n"
             + "  # longer hosts it. Replacements were verified the same way before being\n"
             + "  # offered, and a human made the call.\n"
             + "\n".join(lines) + "\n")
    print("\n--- would append under corrections: ---")
    print(block[:1400] + ("\n  ...\n" if len(block) > 1400 else ""))

    text = OVERLAY.read_text()
    idx = text.index("corrections:")
    nxt = re.search(r"^\w[\w_]*:", text[idx + 12:], re.M)
    cut = idx + 12 + (nxt.start() if nxt else len(text) - idx - 12)
    merged = text[:cut].rstrip("\n") + "\n" + block + "\n" + text[cut:]
    parsed = yaml.safe_load(merged) or {}
    added = set(parsed.get("corrections") or {}) - set(have)
    want = {l.split(":")[0].strip() for l in lines}
    if not want <= added:
        raise SystemExit(f"refusing to write: {sorted(want - added)} did not survive the round trip")
    print(f"overlay.yaml parses with {len(added)} new corrections present")

    if not args.apply:
        print("dry run; pass --apply to write")
        return
    OVERLAY.write_text(merged)
    print(f"wrote {len(lines)} corrections to {OVERLAY.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
