#!/usr/bin/env python3
"""Stage 2d - is the tool's own page still there?

47% of this catalog has no source repository, only a homepage, and academic
URLs rot: labs move, funding ends, a department renames its web server. The DOI
checker already exists (`resolve_pubs.py`); nothing checked the links most of
the catalog actually depends on.

**The hard-won rule from the DOI checker applies here too, and more so: a
non-200 is not a dead link.** An early version of that checker reported 152
broken DOIs and 151 were Crossref rate-limiting. Web servers fail in more ways
than Crossref does, so the outcomes are graded rather than binary:

    ok          2xx, or a redirect chain ending in one
    blocked     401/403, and 405 to a HEAD. The page is there; we are not
                welcome, or the server dislikes the method. Not a dead link.
    ratelimited 429, and 5xx. The server is up and having a bad day. Recheck,
                never report.
    unreachable DNS failure, connection refused, TLS failure, timeout. Often
                genuine death, but also often a slow institutional host, so it
                is reported separately from a 404 and needs two runs to agree.
    dead        404 or 410, and only that. The server answered and said no.

Only `dead` is asserted anywhere user-visible. Everything else is recorded and
left alone.

Results are cached with the date they were obtained, so re-runs are cheap and
`--max-age` decides what to recheck rather than re-fetching 1,900 URLs.

    python pipeline/check_homepages.py [--limit N] [--max-age DAYS] [--workers N]
"""
from __future__ import annotations

import argparse
import json
import threading
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import zip_longest
from datetime import date, datetime, timedelta
from urllib.parse import urlparse

import requests

from config import CACHE, DATA, DOCS, user_agent
from mdutil import cell

CHECK_CACHE = CACHE / "homepage_check.json"
REPORT = DOCS / "homepage-check.md"

# Per-host spacing. One tool's lab often hosts a dozen entries here, and hitting
# a small departmental server twelve times in a second is rude and gets you a
# 429 that means nothing about the link.
HOST_INTERVAL = 1.0
_host_lock = threading.Lock()
_host_last: dict[str, float] = defaultdict(float)


def wait_for_host(host: str) -> None:
    while True:
        with _host_lock:
            now = time.monotonic()
            gap = now - _host_last[host]
            if gap >= HOST_INTERVAL:
                _host_last[host] = now
                return
            sleep_for = HOST_INTERVAL - gap
        time.sleep(sleep_for)


def classify(status: int | None, error: str) -> str:
    if error:
        return "unreachable"
    if status is None:
        return "unreachable"
    if status in (404, 410):
        return "dead"
    if status in (401, 403, 405):
        return "blocked"
    if status == 429 or status >= 500:
        return "ratelimited"
    if 200 <= status < 400:
        return "ok"
    return "blocked"


def check_one(session: requests.Session, url: str) -> dict:
    host = urlparse(url).netloc.lower()
    wait_for_host(host)
    status, error, final = None, "", url
    try:
        # HEAD first: cheaper, and most servers answer it. A surprising number
        # answer 405 or lie, so fall back to a ranged GET rather than trusting
        # a HEAD failure.
        r = session.head(url, timeout=12, allow_redirects=True)
        if r.status_code in (405, 501) or r.status_code >= 400:
            wait_for_host(host)
            r = session.get(url, timeout=15, allow_redirects=True, stream=True)
            r.close()
        status, final = r.status_code, r.url
    except requests.RequestException as exc:
        error = type(exc).__name__
    return {"url": url, "status": status, "final": final, "error": error,
            "state": classify(status, error), "checked": date.today().isoformat()}


def load_cache() -> dict[str, dict]:
    if CHECK_CACHE.exists():
        try:
            return json.loads(CHECK_CACHE.read_text())
        except ValueError:
            return {}
    return {}


def save_cache(cache: dict[str, dict]) -> None:
    CHECK_CACHE.parent.mkdir(parents=True, exist_ok=True)
    CHECK_CACHE.write_text(json.dumps(cache, indent=1, sort_keys=True))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, help="check at most N URLs this run")
    ap.add_argument("--max-age", type=int, default=30,
                    help="recheck entries older than this many days (default 30)")
    ap.add_argument("--workers", type=int, default=10)
    args = ap.parse_args()

    catalog = json.loads((DATA / "catalog.json").read_text())
    urls: dict[str, list[str]] = defaultdict(list)
    for tool in catalog["tools"]:
        hp = (tool.get("homepage") or "").strip()
        if hp.startswith(("http://", "https://")):
            urls[hp].append(tool["name"])

    cache = load_cache()
    cutoff = (datetime.now() - timedelta(days=args.max_age)).date().isoformat()
    stale = [u for u in urls if cache.get(u, {}).get("checked", "") < cutoff]
    # Sorted order is alphabetical, which puts every http:// URL first and makes
    # a --limit run a biased sample of exactly the oldest, rottenest hosts.
    # Interleave by host instead, so a partial run is representative and no one
    # server takes the whole batch.
    by_host: dict[str, list[str]] = defaultdict(list)
    for url in sorted(stale):
        by_host[urlparse(url).netloc.lower()].append(url)
    todo = [u for group in zip_longest(*by_host.values()) for u in group if u]
    dropped = 0
    if args.limit:
        dropped = max(0, len(todo) - args.limit)
        todo = todo[:args.limit]

    fresh = len(urls) - len(stale)
    print(f"{len(urls)} distinct homepages: {fresh} cached within {args.max_age} days, "
          f"{len(todo)} to check now"
          + (f", {dropped} left for a later run (--limit)" if dropped else ""))

    if todo:
        session = requests.Session()
        session.headers.update({"User-Agent": user_agent(),
                                "Accept": "text/html,*/*"})
        done = 0
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(check_one, session, u): u for u in todo}
            for fut in as_completed(futures):
                result = fut.result()
                # Consecutive agreement, so a state that is not 404 can
                # eventually be asserted. The graded outcomes exist because one
                # observation of a timeout means little; two mean something,
                # and nothing was counting them.
                prev = cache.get(result["url"]) or {}
                result["agree"] = (prev.get("agree", 0) + 1
                                   if prev.get("state") == result["state"] else 1)
                cache[result["url"]] = result
                done += 1
                if done % 100 == 0:
                    print(f"  {done}/{len(todo)}")
                    save_cache(cache)
        save_cache(cache)

    write_report(cache, urls)
    states = Counter(cache[u]["state"] for u in urls if u in cache)
    print("  ".join(f"{k}={v}" for k, v in sorted(states.items())))
    print(f"-> {REPORT.relative_to(DOCS.parent)}")


def write_report(cache: dict[str, dict], urls: dict[str, list[str]]) -> None:
    checked = {u: cache[u] for u in urls if u in cache}
    states = Counter(r["state"] for r in checked.values())
    total = max(len(checked), 1)

    out = [
        "# Homepage check",
        "",
        f"Generated {date.today().isoformat()} by `make check-links`.",
        "",
        "Nearly half of this catalog has no source repository, only a homepage, "
        "and academic URLs rot. This is the link check for those.",
        "",
        "**A non-200 is not a dead link.** The DOI checker learned this the "
        "expensive way: it once reported 152 broken DOIs, of which 151 were "
        "rate-limiting. Web servers fail in more ways than Crossref does, so "
        "the outcomes are graded and only `dead` is asserted anywhere the "
        "reader sees.",
        "",
        "| State | Count | Share | Meaning |",
        "| --- | ---: | ---: | --- |",
    ]
    MEANING = {
        "ok": "answered 2xx, possibly after a redirect",
        "blocked": "401/403/405. The page is there; the server refuses us or the method",
        "ratelimited": "429 or 5xx. The server is up and struggling. Recheck, never report",
        "unreachable": "DNS, TLS, refused or timeout. Often real death, often a slow institutional host",
        "dead": "404 or 410. The server answered and said no",
    }
    for state in ("ok", "blocked", "ratelimited", "unreachable", "dead"):
        n = states.get(state, 0)
        out.append(f"| `{state}` | {n} | {n/total:.0%} | {MEANING[state]} |")

    for state, title, note in [
        ("dead", "Dead links",
         "These are the ones worth acting on. Fix the entry at bio.tools where "
         "possible, so the correction reaches every consumer of that registry."),
        ("unreachable", "Unreachable",
         "Not asserted as dead. Two runs on different days should agree before "
         "treating any of these as gone."),
    ]:
        rows = sorted((u, r) for u, r in checked.items() if r["state"] == state)
        out += ["", f"## {title} ({len(rows)})", "", note, ""]
        if not rows:
            out.append("None.")
            continue
        out += ["| Tool | URL | Detail |", "| --- | --- | --- |"]
        for url, r in rows:
            names = ", ".join(sorted(urls[url])[:3])
            detail = r["error"] or (f"HTTP {r['status']}" if r["status"] else "no response")
            out.append(f"| {cell(names)} | {cell(url[:90])} | {cell(detail)} |")
    out.append("")
    REPORT.write_text("\n".join(out))


if __name__ == "__main__":
    main()
