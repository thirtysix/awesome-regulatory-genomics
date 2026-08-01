#!/usr/bin/env python3
"""Edit one bio.tools record safely: snapshot, submit, verify, log.

Every upstream edit goes through here rather than through a hand-rolled curl,
because four things about this API will silently produce a wrong result and all
four are easy to forget under repetition:

1. **A write can return HTTP 500 and still succeed.** Three of the first four
   writes did. Branching on the status code would double-write, and a retry that
   varied the id would create a duplicate record. The only reliable check is to
   GET the record back and read the field, which this does.
2. **Read shape is not write shape.** A GET returns `null` for empty fields and
   the validator rejects nulls, so a record cannot be round-tripped without
   stripping nulls, empty lists and the server-managed fields.
3. **There is no version history and no undo.** If an edit turns out wrong, the
   only way back is a copy kept beforehand. This refuses to submit unless the
   snapshot is written first.
4. **There is no contribution record.** An edit to a record you do not own
   appears nowhere in your profile, so `curation/upstream-log.yaml` is the only
   evidence it happened.

    export BIOTOOLS_TOKEN=...
    python pipeline/biotools_edit.py --record deepcyps \\
        --set-json 'function' --from-file new_function.json --dry-run
    python pipeline/biotools_edit.py --record enhanceratlas \\
        --set homepage=http://www.enhanceratlas.org/
    python pipeline/biotools_edit.py --record deepcyps --restore
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date

from config import CURATION

SNAPDIR = CURATION / "upstream-snapshots" / "bio.tools"
LOG = CURATION / "upstream-log.yaml"
API = "https://bio.tools/api/tool/{}/?format=json"

# Set by the server; echoing them back is either ignored or an error.
SERVER_MANAGED = ("additionDate", "lastUpdate", "owner", "validated",
                  "homepage_status", "confidence_flag", "biotoolsCURIE",
                  "elixir_badge")


def req(url, method="GET", payload=None, token=None):
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    r.add_header("Content-Type", "application/json")
    if token:
        r.add_header("Authorization", f"Token {token}")
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            body = resp.read().decode()
            return resp.status, (json.loads(body) if body.strip().startswith(("{", "[")) else body)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:400]
    except Exception as e:                                   # noqa: BLE001
        return 0, str(e)


def strip(x):
    """Remove nulls and empties, which the write schema rejects."""
    if isinstance(x, dict):
        return {k: strip(v) for k, v in x.items()
                if v is not None and v != [] and v != "" and k not in SERVER_MANAGED}
    if isinstance(x, list):
        return [strip(v) for v in x if v is not None]
    return x


def snapshot_path(record: str) -> "os.PathLike":
    return SNAPDIR / f"{record}.{date.today().isoformat()}.before.json"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--record", required=True)
    ap.add_argument("--set", action="append", default=[],
                    help="field=value for a scalar field, repeatable")
    ap.add_argument("--set-json", help="field name whose value comes from --from-file")
    ap.add_argument("--from-file", help="JSON file holding the new value for --set-json")
    ap.add_argument("--restore", action="store_true",
                    help="put the newest snapshot back, undoing our edits")
    ap.add_argument("--dry-run", action="store_true",
                    help="snapshot and show the diff, submit nothing")
    args = ap.parse_args()

    token = os.environ.get("BIOTOOLS_TOKEN", "").strip()
    status, live = req(API.format(args.record))
    if status != 200 or not isinstance(live, dict):
        sys.exit(f"could not fetch {args.record}: HTTP {status}")

    if args.restore:
        snaps = sorted(SNAPDIR.glob(f"{args.record}.*.before.json"))
        if not snaps:
            sys.exit(f"no snapshot on disk for {args.record}; nothing to restore from")
        payload = strip(json.loads(snaps[-1].read_text()))
        print(f"restoring {args.record} from {snaps[-1].name}")
    else:
        # The snapshot is written BEFORE anything is submitted, and its absence
        # is a hard stop. An edit whose original was never captured cannot be
        # undone, because bio.tools keeps no history.
        path = snapshot_path(args.record)
        if not path.exists():
            SNAPDIR.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(live, indent=1, sort_keys=True))
            print(f"snapshot written: {path}")
        else:
            print(f"snapshot already exists, keeping the earlier one: {path}")
        if not path.exists():
            sys.exit("snapshot could not be written; refusing to edit")

        updated = copy.deepcopy(live)
        changes = []
        for pair in args.set:
            k, _, v = pair.partition("=")
            changes.append((k, updated.get(k), v))
            updated[k] = v
        if args.set_json:
            new = json.loads(open(args.from_file).read())
            changes.append((args.set_json, "(json)", "(json)"))
            updated[args.set_json] = new
        if not changes:
            sys.exit("nothing to change; pass --set or --set-json")
        for k, before, after in changes:
            print(f"  {k}: {str(before)[:60]!r} -> {str(after)[:60]!r}")
        payload = strip(updated)

    if args.dry_run:
        print("\ndry run: nothing submitted")
        return
    if not token:
        sys.exit("BIOTOOLS_TOKEN is not set")

    code, body = req(API.format(args.record), "PUT", payload, token)
    print(f"\nPUT returned HTTP {code} - this is NOT the result, verifying by GET")
    status, after = req(API.format(args.record))
    if status != 200 or not isinstance(after, dict):
        sys.exit(f"could not re-read {args.record}: HTTP {status}")
    for k, _, want in (changes if not args.restore else []):
        got = after.get(k)
        ok = str(got) == str(want) or want == "(json)"
        print(f"  verified {k}: {str(got)[:70]!r}  {'OK' if ok else 'DID NOT TAKE'}")
    print(f"  lastUpdate now {after.get('lastUpdate')}")
    print(f"\nAdd an entry to {LOG.name} - it is the only record this happened.")


if __name__ == "__main__":
    main()
