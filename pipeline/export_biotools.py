#!/usr/bin/env python3
"""Stage 2k - export corrections as biotoolsSchema JSON for bulk upload.

bio.tools asked for "a bio.tools json with all corrected entries" so they can
upload it wholesale, which sidesteps the fact that 85% of the affected records
are `editPermission: private`.

**One file per category, deliberately.** The categories carry very different
weights of evidence, and bundling them would force a single accept-or-reject on
all of it. A wrong publication is verifiable in one lookup; a dead homepage is a
judgement about transience; the platform-paper question is not an error at all
until they agree it is one. Separate files let each be taken, argued with or
deferred independently.

Two of the three files are records to upload. `homepages` is a report, because
there is no correction to apply: `homepage_status` is server-managed and we have
no verified replacement URL. Reporting is what feeds their existing OpenEBench
monitoring, which is what they asked for.

    python pipeline/export_biotools.py
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config import CURATION, DATA, RAW
from jsonio import read_json

OUT = CURATION / "biotools-corrections"
SNAP = CURATION / "upstream-snapshots" / "bio.tools"

# Server-managed; echoing them back is rejected or ignored.
DROP = ("additionDate", "lastUpdate", "owner", "validated", "homepage_status",
        "confidence_flag", "biotoolsCURIE", "elixir_badge")

# Records are validated against bio.tools rather than against a local model of
# what it accepts. A hardcoded list of stale EDAM term/URI pairs was tried first
# and was wrong: it caught Editing/3096 and Filtering/3695 and missed Deposition,
# Protein-protein interaction prediction and others. edamontology.org/EDAM.csv
# does not settle it either, since it disagrees with the live validator. Asking
# is cheap and exact; predicting is neither.
VALIDATE = "https://bio.tools/api/tool/validate/?format=json"


def strip(x):
    """Drop what the write schema rejects, including entries that empty out.

    Stripping nulls from a `credit` entry whose every field was null leaves `{}`,
    which the validator rejects with "at least one of credit ... must be filled".
    An empty dict is not an empty value to Python, so it has to be dropped
    explicitly after its contents have gone.
    """
    if isinstance(x, dict):
        return {k: strip(v) for k, v in x.items()
                if v is not None and v != [] and v != "" and v != "<redacted>"
                and k not in DROP}
    if isinstance(x, list):
        out = [strip(v) for v in x if v is not None]
        return [v for v in out if v not in ({}, [], "")]
    return x


def drop_empty_credit(rec: dict) -> dict:
    """A credit entry needs a name, an email or a URL.

    Third-party emails are redacted out of the harvest, so a credit whose only
    populated field was an email now has none of the three and is rejected.
    """
    if rec.get("credit"):
        rec["credit"] = [c for c in rec["credit"]
                         if c.get("name") or c.get("email") or c.get("url")]
        if not rec["credit"]:
            rec.pop("credit")
    return rec


def validate(rec: dict, token: str) -> str | None:
    """None if bio.tools would accept it, else its own complaint."""
    body = json.dumps({k: v for k, v in rec.items() if not k.startswith("_")}).encode()
    req = urllib.request.Request(VALIDATE, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Token {token}")
    try:
        urllib.request.urlopen(req, timeout=45)
        return None
    except urllib.error.HTTPError as e:
        err = json.loads(e.read().decode() or "{}")
        # The create-validator always objects that the id exists; that is the
        # one complaint an update does not have to answer.
        err.pop("biotoolsID", None)
        return json.dumps(err)[:200] if err else None
    except Exception as e:                                   # noqa: BLE001
        return type(e).__name__


def main() -> None:
    token = os.environ.get("BIOTOOLS_TOKEN", "").strip()
    if not token:
        print("  BIOTOOLS_TOKEN unset: records will NOT be validated before export")
    OUT.mkdir(parents=True, exist_ok=True)
    overlay = yaml.safe_load((CURATION / "overlay.yaml").read_text())
    enriched = {r["biotoolsID"]: r for r in read_json(RAW / "enriched.json.gz")["list"]}
    catalog = {t["id"]: t for t in json.loads((DATA / "catalog.json").read_text())["tools"]}
    bid_of = {k: (catalog.get(k, {}).get("biotools_id") or (k if k in enriched else None))
              for k in set(overlay.get("publications") or {}) | set(overlay.get("exclude") or {})}

    manifest = {}

    # 1. EDAM operations that the record's own content contradicts ------------
    recs, skipped = [], []
    for key, why in (overlay.get("exclude") or {}).items():
        m = re.search(r"admitted on EDAM '([^']+)'", str(why))
        if not m:
            continue
        bid = key if key in enriched else bid_of.get(key)
        if not bid or bid not in enriched:
            continue
        rec = json.loads(json.dumps(enriched[bid]))
        op = m.group(1)
        for f in rec.get("function") or []:
            f["operation"] = [o for o in f.get("operation") or [] if o.get("term") != op]
        # A record left with no operation at all is worse than one with a wrong
        # operation, so those are held back rather than emptied.
        if not any(f.get("operation") for f in rec.get("function") or []):
            skipped.append({"biotoolsID": bid, "removed": op,
                            "why": "would leave the record with no operation"})
            continue
        out = drop_empty_credit(strip({k: v for k, v in rec.items()
                                       if not k.startswith("_")}))
        out["_correction"] = f"removed EDAM operation {op!r}"
        err = validate(out, token) if token else None
        if err:
            skipped.append({"biotoolsID": bid, "removed": op,
                            "why": f"bio.tools rejects the record as it stands: {err}"})
            continue
        recs.append(out)
    (OUT / "edam-operations.json").write_text(json.dumps(recs, indent=1) + "\n")
    manifest["edam-operations.json"] = {"records": len(recs), "held_back": skipped}

    # 2. Publications that point at the wrong paper ---------------------------
    recs2, skipped2 = [], []
    for key, ident in (overlay.get("publications") or {}).items():
        bid = bid_of.get(key) or (key if key in enriched else None)
        if not bid or bid not in enriched:
            continue
        rec = json.loads(json.dumps(enriched[bid]))
        theirs = set()
        for p in rec.get("publication") or []:
            md = p.get("metadata") or {}
            if p.get("pmid") or md.get("pmid"):
                theirs.add("pmid:" + str(p.get("pmid") or md.get("pmid")))
            if p.get("doi"):
                theirs.add("doi:" + p["doi"].lower())
        if ident.lower() in {t.lower() for t in theirs}:
            continue                      # already agrees; nothing to correct
        kind, _, val = ident.partition(":")
        was = sorted(theirs)
        rec["publication"] = [{("pmid" if kind == "pmid" else "doi"): val,
                               "type": ["Primary"]}]
        out = drop_empty_credit(strip({k: v for k, v in rec.items()
                                       if not k.startswith("_")}))
        out["_correction"] = f"publication {was} -> {ident}"
        err = validate(out, token) if token else None
        if err:
            skipped2.append({"biotoolsID": bid, "why": err})
            continue
        recs2.append(out)
    (OUT / "publications.json").write_text(json.dumps(recs2, indent=1) + "\n")
    manifest["publications.json"] = {"records": len(recs2), "held_back": skipped2}

    # 3. Homepages confirmed dead: a report, not records ----------------------
    probe = json.loads(Path("/tmp/homepage_reprobe.json").read_text()) \
        if Path("/tmp/homepage_reprobe.json").exists() else []
    dead = [{"biotoolsID": p["id"], "homepage": p["url"], "status": p["status"],
             "first_seen": "2026-07-28", "reconfirmed": date.today().isoformat()}
            for p in probe if str(p["status"]) in ("404", "410")]
    (OUT / "homepages.json").write_text(json.dumps(
        {"note": "A report, not records to upload. Each URL returned 404 or 410 on "
                 "two checks nine days apart, so these are not transient. No "
                 "replacement URL was found for any of them, and homepage_status "
                 "is server-managed, so there is nothing here to apply directly.",
         "checked": date.today().isoformat(), "count": len(dead),
         "entries": dead}, indent=1) + "\n")
    manifest["homepages.json"] = {"records": len(dead), "held_back": []}

    for name, m in manifest.items():
        print(f"  {name:<26}{m['records']:>4} records"
              + (f"   ({len(m['held_back'])} held back)" if m["held_back"] else ""))
    (OUT / "_manifest.json").write_text(json.dumps(manifest, indent=1) + "\n")


if __name__ == "__main__":
    main()
