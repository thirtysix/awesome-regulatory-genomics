"""Fold a human review of the promotion queue back into the curation files.

The review happens in a browser page whose marks live in that browser, so the
decisions arrive here as a json map of name -> keep | skip. Keeps become
`curation/seeds.yaml` entries; skips become `curation/literature-declined.yaml`
entries, which exists so a declined candidate stops resurfacing in every later
sweep - being declined is a decision, and a decision that is not written down is
made again next week.

Both files are appended as text rather than rewritten through a yaml dumper.
They are hand-maintained, comment-heavy audit trails, and a round-trip would
silently reflow the comments and reorder the keys.

Usage:
    python pipeline/ingest_review.py --decisions review.json          # dry run
    python pipeline/ingest_review.py --decisions review.json --apply
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path

import yaml

from promotion_queue import absolute, build, slug_of

ROOT = Path(__file__).resolve().parent.parent
SEEDS = ROOT / "curation" / "seeds.yaml"
DECLINED = ROOT / "curation" / "literature-declined.yaml"

DECLINED_HEADER = """\
# Literature candidates reviewed by hand and declined.
#
# The discovery sweep re-runs and would offer each of these again; this file is
# what makes a decline stick. It is a record of judgement, not of failure - most
# entries here are real software that belongs to a neighbouring field.
#
# name: reason, where the name is the candidate name as the queue showed it.

declined:
"""


# yaml 1.1 resolves these bare words to booleans or null, so a tool honestly
# named "No" would load as False. Quote them even though they look harmless.
RESERVED = {"y", "n", "yes", "no", "true", "false", "on", "off", "null", "~"}


def _yaml_str(s: str) -> str:
    """Quote only when the plain form would not survive a round trip."""
    s = re.sub(r"\s+", " ", str(s or "")).strip().rstrip(".")
    if not s:
        return '""'
    if (re.match(r"^[A-Za-z0-9]", s)
            and not re.search(r"[:#\[\]{}&*!|>'\"%@`,]", s)
            and s.lower() not in RESERVED
            and not re.fullmatch(r"[-+]?[0-9._]+([eE][-+]?[0-9]+)?", s)):
        return s
    return "'" + s.replace("'", "''") + "'"


def existing_names() -> set[str]:
    names = set()
    if SEEDS.exists():
        doc = yaml.safe_load(SEEDS.read_text()) or {}
        names |= {str(t.get("name", "")).lower() for t in (doc.get("tools") or [])}
    return names


def already_declined() -> dict:
    if not DECLINED.exists():
        return {}
    doc = yaml.safe_load(DECLINED.read_text()) or {}
    return doc.get("declined") or {}


def seed_entry(r: dict) -> str:
    # A tool with no software location still has a paper, and for older entries
    # the paper is the only thing that still resolves. Pointing at the doi is
    # honest - here is the work, its code is not findable - and better than
    # dropping a real tool for having outlived its hosting.
    url = r["software_url"] or f"https://doi.org/{r['doi']}"
    lines = [f"  - name: {_yaml_str(r['name'])}",
             f"    url: {url}"]
    if not r["software_url"]:
        lines.append("    tags: [no-software-url]")
    if r.get("rejected_repo"):
        lines.append(f"    note: {_yaml_str('a repository named for this tool exists at ' + r['rejected_repo'] + ' but did not verify as the same software')}")
    slug = slug_of(r["repo"] or r["code"])
    if slug:
        lines.append(f"    repo: {slug}")
    if r["description"]:
        lines.append(f"    description: {_yaml_str(r['description'])}")
    lines.append(f"    categories: [{', '.join(r['categories'])}]")
    if r["doi"]:
        lines.append(f"    doi: {r['doi']}")
    elif r["pmid"]:
        lines.append(f"    pmid: {r['pmid']}")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--decisions", required=True, help="json map of name -> keep|skip")
    ap.add_argument("--apply", action="store_true", help="write the files")
    args = ap.parse_args()

    marks = json.loads(Path(args.decisions).read_text())
    rows = {r["name"]: r for r in build()}
    have, declined = existing_names(), already_declined()

    keep, skip, blocked, unknown, unchecked = [], [], [], [], []
    for name, mark in marks.items():
        verdict = mark.get("verdict") if isinstance(mark, dict) else mark
        reason = (mark.get("reason") or "").strip() if isinstance(mark, dict) else ""
        r = rows.get(name)
        # A reviewer may correct the url the pipeline found. This is not a
        # nicety: an unvalidated url can point at entirely different software -
        # SEdb's stored repo was "Search Engine DataBase utils" - so the review
        # is the last place a wrong one can be caught before it is published.
        if r is not None and isinstance(mark, dict) and (mark.get("url") or mark.get("repo")):
            r = dict(r)
            if mark.get("url"):
                r["software_url"] = r["code"] = mark["url"]
            r["repo"] = absolute(mark["repo"]) if mark.get("repo") else (
                mark.get("url", "") if "github.com" in str(mark.get("url", "")) else "")
            r["corrected"] = True
        if r is None:
            unknown.append(name)
        elif verdict == "keep":
            if name.lower() in have:
                blocked.append((name, "already in seeds.yaml"))
            elif not r["software_url"] and not r.get("doi"):
                blocked.append((name, "no url and no doi, so nothing to point at"))
            elif not r["categories"]:
                blocked.append((name, "no categories from the categorise stage"))
            elif r["layer1"] in ("hold", "fail") and not r.get("corrected"):
                # A doubtful REPOSITORY is not a reason to drop the TOOL. The
                # catalog is deliberately inclusive, so the entry goes in
                # pointing at its paper and the unverified repository is
                # recorded rather than published: SEdb's "repository" was
                # "Search Engine DataBase utils", and printing that as a
                # tool's source is worse than printing no source at all.
                r = dict(r)
                r["rejected_repo"] = r["software_url"]
                r["software_url"] = r["code"] = r["repo"] = ""
                keep.append(r)
                # A code-host url layer 1 would not confirm is the one way this
                # pipeline writes the WRONG software into the catalog rather
                # than merely a useless link. SEdb's was "Search Engine
                # DataBase utils"; BiSearch's was a binary-search package;
                # Xenbase's was a javascript polyfill. Keeping one is fine, but
                # it has to be a deliberate act: supply the url in the decision.

            elif (not r["layer1"]) and slug_of(r["software_url"]) and not r.get("corrected"):
                unchecked.append(r)
            else:
                keep.append(r)
        elif verdict == "skip":
            if name not in declined:
                skip.append((r, reason))

    # A keep whose repo was never validated gets validated now, rather than
    # trusted or refused. Names in this field are short and generic, so a repo
    # called bisearch is not evidence of anything on its own.
    if unchecked:
        import requests
        from config import user_agent
        from enrich import github_token
        from resolve_repos import github_meta, validate as l1_validate
        http = requests.Session(); http.headers.update({"User-Agent": user_agent()})
        token, cache = github_token(), {}
        print(f"validating {len(unchecked)} repos the pipeline never checked")
        for r in unchecked:
            slug = slug_of(r["software_url"])
            meta = github_meta(http, slug, token, cache)
            ok, why = l1_validate({"name": r["name"], "description": r["description"]},
                                  slug, meta, source="review")
            r["layer1"], r["layer1_why"] = ("pass" if ok else "hold"), why
            print(f"    {'PASS' if ok else 'HOLD'} {r['name'][:20]:22s} {slug:32s} {why[:44]}")
            if not ok:
                # Same rule: keep the tool, drop the unproven repository.
                r["rejected_repo"] = r["software_url"]
                r["software_url"] = r["code"] = r["repo"] = ""
            keep.append(r)

    print(f"decisions read : {len(marks)}")
    print(f"  to seed      : {len(keep)}")
    print(f"  to decline   : {len(skip)}")
    if blocked:
        print(f"  blocked      : {len(blocked)}")
        for n, why in blocked:
            print(f"      {n[:26]:28s} {why}")
    if unknown:
        print(f"  not in queue : {len(unknown)} -> {', '.join(unknown[:6])}")

    stamp = dt.date.today().isoformat()
    if keep:
        n_fixed = sum(1 for r in keep if r.get("corrected"))
        block = (f"\n  # --- promoted from the literature queue, reviewed by hand {stamp} "
                 + "-" * max(0, 12) + "\n"
                 + (f"  # {n_fixed} of these carry a url the reviewer corrected; the one the\n"
                    f"  # pipeline had pointed at different software entirely.\n" if n_fixed else "")
                 + "\n\n".join(seed_entry(r) for r in keep) + "\n")
        print("\n--- would append to curation/seeds.yaml ---")
        print(block[:1200] + ("\n  ...\n" if len(block) > 1200 else ""))
    if skip:
        # Never reuse scope_reason here: it is the auditor's argument for why
        # the tool IS in scope, and pasting it under a decline reads as a
        # justification for the opposite decision.
        lines = "\n".join(
            f"  {_yaml_str(r['name'])}: "
            f"{_yaml_str(why or 'Reviewed ' + stamp + ' and declined by hand; no reason recorded')}"
            for r, why in skip)
        print("--- would append to curation/literature-declined.yaml ---")
        print(lines[:800] + ("\n  ...\n" if len(lines) > 800 else ""))

    # Parse the would-be file before writing it. These are append-by-text
    # edits to hand-maintained yaml, so a bad quote in one description would
    # otherwise land as a broken curation file that the next build trips over.
    def checked(path: Path, addition: str, header: str, key: str, expect: set[str]) -> str:
        base = path.read_text().rstrip("\n") if path.exists() else header.rstrip("\n")
        merged = base + "\n" + addition
        doc = yaml.safe_load(merged) or {}
        got = doc.get(key)
        if got is None:
            raise SystemExit(f"refusing to write {path.name}: no '{key}' key after the append")
        names = {str(t.get("name", "")) for t in got} if isinstance(got, list) else set(got)
        missing = expect - names
        if missing:
            raise SystemExit(f"refusing to write {path.name}: {sorted(missing)} did not survive the round trip")
        return merged

    seeds_text = checked(SEEDS, block, "tools:\n", "tools",
                         {r["name"] for r in keep}) if keep else None
    decl_text = checked(DECLINED, lines + "\n", DECLINED_HEADER, "declined",
                        {r["name"] for r, _ in skip}) if skip else None
    print("\nboth files parse with the new entries present")

    if not args.apply:
        print("dry run; pass --apply to write")
        return

    if seeds_text is not None:
        SEEDS.write_text(seeds_text + "\n")
        print(f"appended {len(keep)} entries to {SEEDS.relative_to(ROOT)}")
    if decl_text is not None:
        DECLINED.write_text(decl_text + "\n")
        print(f"appended {len(skip)} entries to {DECLINED.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
