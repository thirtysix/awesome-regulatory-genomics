#!/usr/bin/env python3
"""Stage 2e - is the page at that url actually THIS tool?

`check_homepages.py` answers whether a url still resolves. It cannot answer the
question that actually matters, and the gap is not theoretical:

    HHMD, the human histone modification database, offers www.hhmd.org in its
    own paper. That domain resolves, returns 200, and is now the Hip Hop Museum
    Denmark. A lapsed domain answers exactly like a live one.

Three of the same class turned up in one afternoon of review - a repository
called `sedb` that is "Search Engine DataBase utils", a `bisearch` that is a
python binary-search package, and a Xenbase link pointing at whatwg/fetch, a
javascript polyfill scraped out of the journal's own page furniture. Every one
would have been published as the tool.

The check is deterministic first and only asks a model about the middle:

    confirmed   the tool's name appears in the page, and the page shares
                vocabulary with the tool's description
    mismatch    the page is fine, says nothing about this tool, and shares no
                vocabulary. This is the Hip Hop Museum case
    undecided   anything else - a name too generic to match on, a page that is
                mostly javascript, a redirect to a departmental index. These go
                to a cheap model, which sees the same text a person would

Nothing here asserts a tool is gone. `mismatch` means "the url is wrong", which
is a reason to look for a better one, not to drop the tool.

The extracted text of each page is cached, not a hash of it. Caching the hash
would make a verdict cheap to repeat and a *rule change* cost 2,137 refetches,
which is the same trade the full-text store already got wrong once. `--rejudge`
re-runs every verdict from the cache without touching the network.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import sys
import threading
import time
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from concurrent.futures import ThreadPoolExecutor

from check_homepages import classify
from config import user_agent
from jsonio import read_json, redact_emails, write_json
# Imported for its side effect as much as its function: llm_assist puts the
# DeepInfra key into the environment when it loads, so reading the key before
# this import reports "no key" on a machine that has one.
from llm_assist import call as llm_call, parse_json

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "cache" / "url_identity.json"
# The pages themselves, gzipped. The extracted text was cached once and the
# extraction rule then changed - site chrome had to come off - which cost a
# full refetch. Same lesson as the full-text store and the llm prompt hashes:
# keep the input, because the rule that reads it is the thing that changes.
PAGES = ROOT / "data" / "cache" / "pages"
OUT = ROOT / "data" / "raw" / "url_identity.json"

# A browser string, because several university hosts refuse anything else and a
# 403 from a live page is indistinguishable from a dead one at this layer.
BROWSER = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
           "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

TAG = re.compile(r"<(script|style|noscript|svg)[^>]*>.*?</\1>", re.S | re.I)
# Site furniture. Sanger's tool pages put a careers menu ahead of the content,
# so the first 4,000 characters of GWAVA's page are "Working at the Sanger
# Institute is truly unique" and a model reading that calls it an about page.
CHROME = re.compile(r"<(nav|header|footer|aside|form)\b[^>]*>.*?</\1>", re.S | re.I)
MAIN = re.compile(r"<(main|article)\b[^>]*>(.*?)</\1>", re.S | re.I)
STRIP = re.compile(r"<[^>]+>")
WORD = re.compile(r"[a-z0-9]{4,}")

# Words shared by every bioinformatics page; overlap on these means nothing.
STOP = {
    "data", "analysis", "software", "tool", "tools", "using", "used", "with",
    "from", "this", "that", "which", "based", "http", "https", "www", "html",
    "page", "home", "download", "downloads", "version", "release", "install",
    "documentation", "docs", "github", "please", "university", "research",
    "available", "here", "more", "about", "contact", "supplementary", "paper",
    "publication", "citation", "cite", "license", "copyright", "reserved",
}


def visible_text(html: str, limit: int = 4000) -> str:
    """The page's own words, with the site's furniture taken off first.

    Truncating raw markup to a fixed budget spends it on whatever the CMS puts
    first, which is a navigation menu. Prefer <main> or <article> when the page
    marks one, and drop nav/header/footer/aside either way.
    """
    body = TAG.sub(" ", html)
    body = CHROME.sub(" ", body)
    m = MAIN.search(body)
    if m and len(STRIP.sub(" ", m.group(2)).strip()) > 200:
        body = m.group(2)
    body = STRIP.sub(" ", body)
    body = re.sub(r"&[a-z]+;|&#\d+;", " ", body)
    return re.sub(r"\s+", " ", body).strip()[:limit]


def page_title(html: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.S | re.I)
    return re.sub(r"\s+", " ", STRIP.sub(" ", m.group(1))).strip()[:200] if m else ""


def terms(text: str) -> set[str]:
    return {w for w in WORD.findall(text.lower()) if w not in STOP}


def name_present(name: str, *fields: str) -> bool:
    """Is the tool's name in the page, allowing for punctuation and case?

    Compared on letters and digits only, so BRAT-BW matches "BRAT BW" and
    CUT-RUNTools-2.0 matches "CUT&RUNTools 2.0".
    """
    flat = re.sub(r"[^a-z0-9]", "", name.lower())
    if len(flat) < 3:
        return False
    hay = re.sub(r"[^a-z0-9]", "", " ".join(fields).lower())
    return flat in hay


# Below this, the page carried no prose to reason about: a javascript shell, a
# Shiny or Galaxy app, the Google Code archive viewer. Absence of evidence is
# not evidence of the wrong tool, and calling it a mismatch retires live pages.
MIN_TEXT = 300

META_REFRESH = re.compile(
    r"""<meta[^>]+http-equiv=['"]?refresh['"]?[^>]*content=['"][^'"]*url=([^'"]+)""",
    re.I)


def authors_on_page(tool: dict, title: str, text: str) -> tuple[list[str], list[str]]:
    """(known author surnames, those appearing on the page).

    Weak evidence for finding a tool and strong evidence for checking one.
    Catalog SteinerNet is Tuncbag and Fraenkel's omics web server; CRAN's
    SteinerNet is Afshin Sadeghi's generic Steiner-tree package. The names are
    identical, both pages say "steiner", "tree" and "problem", and both the
    rules and the model called the second one a match. Neither author appears
    on it, and that is the difference nothing else could see.
    """
    try:
        from recover_urls import author_tokens
    except Exception:
        return [], []
    known = author_tokens(tool)
    if not known:
        return [], []
    hay = (title + " " + text).lower()
    return known, [a for a in known if a.lower() in hay]


def judge(tool: dict, title: str, text: str) -> tuple[str, str]:
    """Deterministic verdict, or 'undecided' when a model should look."""
    named = name_present(tool["name"], title, text)
    if len(text) < MIN_TEXT and not named:
        return "unreadable", f"only {len(text)} characters of text; nothing to judge"
    shared = terms(tool.get("description", "")) & terms(title + " " + text)
    n = len(shared)
    sample = ", ".join(sorted(shared)[:5])
    if named and n >= 2:
        known, seen = authors_on_page(tool, title, text)
        # A name match plus generic method vocabulary is exactly what a
        # same-name different-tool looks like. When we know who wrote the tool
        # and none of them are anywhere on the page, that is not a confirmation
        # to make on the rules alone.
        if known and not seen and n < 5:
            return "undecided", (f"name matches and {n} shared terms ({sample}), but none of "
                                 f"{'/'.join(known[:2])} appear")
        credit = f"; {'/'.join(seen)} on the page" if seen else ""
        return "confirmed", f"name on the page and {n} shared terms ({sample}){credit}"
    if named and n == 0 and len(text) > MIN_TEXT:
        # The name is there but nothing else is. Usually a person's page or a
        # departmental index that merely lists the tool - real, but not the
        # tool's own page. Worth a look rather than a verdict.
        return "undecided", "name present, no shared vocabulary"
    if not named and n == 0:
        return "mismatch", "neither the name nor any shared vocabulary appears"
    if not named and n >= 4:
        return "undecided", f"no name, but {n} shared terms ({sample})"
    return "undecided", f"name={named}, {n} shared terms"


LLM_SYSTEM = """You decide whether a web page belongs to a named scientific software tool.

You are given the tool's name, its one-line description, and the title plus an
extract of the page found at the url the tool's publication gave.

Answer ONLY with json: {"belongs": true|false|"unjudgeable", "confidence": "high"|"medium"|"low", "reason": "<one sentence>"}

Answer "unjudgeable" when the page did not show you its content: a sign-in or
login screen, a bot-protection or captcha challenge, a "please enable
JavaScript" shell, a maintenance or "temporarily unavailable" notice, or raw
binary. Those tell you nothing about the tool either way, and calling them
false would retire a tool for being behind a login. Prefer "unjudgeable" over a
guess in exactly those cases, and only those.

Say true when the page is the tool's own page, its repository, its
documentation, or a lab or project page that clearly hosts it.
Say false when the page is about something else entirely - a different tool
that shares the name, a re-registered domain now selling something unrelated, a
generic institutional index, a parked or error page, or a journal landing page.
A page can be sparse, dated or ugly and still be the tool's own page; judge
subject matter, not quality. When you are told the tool's authors and none of
their names appear, treat a match on the tool's name alone with suspicion: two
groups naming different software the same thing is common, and shared generic
vocabulary is not evidence that this is the same tool. If the page is empty or gives you nothing to go
on, say false with low confidence."""


def ask_model(tool: dict, title: str, text: str, key: str, model: str,
              cache: dict, lock: threading.Lock | None = None) -> dict:
    known, seen = authors_on_page(tool, title, text)
    who = ""
    if known:
        who = (f"Published by: {', '.join(known[:2])}. "
               + (f"Those names DO appear on this page: {', '.join(seen)}."
                  if seen else "None of those names appear anywhere on this page.")
               + "\n")
    user = (f"Tool: {tool['name']}\n"
            f"Description: {tool.get('description', '')[:300]}\n"
            f"{who}\n"
            f"Page title: {title}\n"
            f"Page text: {text[:1800]}")
    ck = f"{model}:{hashlib.sha256((LLM_SYSTEM + user).encode()).hexdigest()[:16]}"
    if lock:
        with lock:
            if ck in cache:
                return cache[ck]
    elif ck in cache:
        return cache[ck]
    text_out, _cost, _s = llm_call(model, LLM_SYSTEM, user, key, max_tokens=300)
    got = parse_json(text_out) or {"belongs": None, "confidence": "low",
                                   "reason": "model returned no usable json"}
    if lock:
        with lock:
            cache[ck] = got
    else:
        cache[ck] = got
    return got


# Connect and read budgets, separately. A host that will not complete a TCP
# handshake in five seconds is not going to serve a page, and the old single
# 30-second budget meant the ~26% of urls that do not answer consumed about
# three quarters of the wall clock.
TIMEOUT = (5, 15)
MAX_BYTES = 1_500_000     # a page bigger than this is not a tool homepage

_local = threading.local()
_host_locks: dict[str, threading.Lock] = {}
_host_lock_guard = threading.Lock()


def session() -> requests.Session:
    """One Session per thread: requests.Session is not thread-safe."""
    sess = getattr(_local, "sess", None)
    if sess is None:
        sess = requests.Session()
        sess.headers.update({"User-Agent": BROWSER, "Accept-Language": "en"})
        _local.sess = sess
    return sess


def host_lock(url: str) -> threading.Lock:
    """One request at a time per host, however many workers are running.

    Concurrency here is a win because the catalog points at ~2,000 different
    hosts; it must not become eight simultaneous requests to one university
    that is already struggling to answer once.
    """
    host = urlparse(url).netloc.lower()
    with _host_lock_guard:
        return _host_locks.setdefault(host, threading.Lock())


def page_path(url: str) -> Path:
    return PAGES / (hashlib.sha1(url.encode()).hexdigest() + ".html.gz")


def store_page(url: str, html: str) -> None:
    try:
        PAGES.mkdir(parents=True, exist_ok=True)
        with gzip.open(page_path(url), "wt", encoding="utf-8") as fh:
            fh.write(html)
    except OSError:
        pass


def load_page(url: str) -> str:
    p = page_path(url)
    if not p.exists():
        return ""
    try:
        with gzip.open(p, "rt", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def fetch(url: str, hops: int = 2) -> tuple[str, str, str]:
    """Fetch, following meta-refresh as well as HTTP redirects.

    requests follows 3xx; it cannot follow a page that redirects in markup.
    Signac's homepage is 573 bytes titled "Page Redirection", and judging that
    shell says the page has nothing to do with Signac.
    """
    http = session()
    with host_lock(url):
        try:
            r = http.get(url, timeout=TIMEOUT, allow_redirects=True, stream=True)
            body = r.raw.read(MAX_BYTES, decode_content=True) or b""
        except Exception as e:
            return classify(None, type(e).__name__), "", url
        finally:
            time.sleep(0.2)
    if r.status_code >= 400:
        r.close()
        return classify(r.status_code, ""), "", str(r.url)
    text = body.decode(r.encoding or "utf-8", "replace")
    r.close()
    m = META_REFRESH.search(text[:4000])
    if m and hops > 0:
        nxt = urljoin(str(r.url), m.group(1).strip())
        if nxt.rstrip("/") != str(r.url).rstrip("/"):
            return fetch(nxt, hops - 1)
    return classify(r.status_code, ""), text, str(r.url)


def verdict_for(t: dict, title: str, text: str, grade: str,
                key: str, model: str, llm: dict, lock: threading.Lock,
                use_llm: bool) -> tuple[str, str]:
    if grade != "ok":
        return "unchecked", f"page not readable ({grade})"
    v, why = judge(t, title, text)
    # A deterministic mismatch is a *candidate*, not a verdict. It is the one
    # consequential call this stage makes - it says a catalog url is wrong - and
    # the rule behind it is crude: the name is absent and no vocabulary
    # overlaps. That is also what a Google Drive sign-in wall, a bot challenge,
    # a "please enable javascript" notice and a maintenance page all look like.
    # Asked for a second opinion, the model overturned 3 of 31.
    if v in ("undecided", "mismatch") and use_llm:
        got = ask_model(t, title, text, key, model, llm, lock)
        b = got.get("belongs")
        if b == "unjudgeable":
            v = "unreadable"
        elif b is True:
            v = "confirmed"
        elif b is False:
            v = "mismatch"
        why = f"model({got.get('confidence', '?')}): {got.get('reason', '')[:110]}"
    return v, why


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(ROOT / "data" / "catalog.json"))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--no-llm", action="store_true", help="deterministic verdicts only")
    ap.add_argument("--model", default="deepseek-ai/DeepSeek-V4-Flash")
    ap.add_argument("--only", help="one tool, by name")
    ap.add_argument("--rejudge", action="store_true",
                    help="re-run verdicts from the cache, no network at all")
    ap.add_argument("--reextract", action="store_true",
                    help="re-derive the text from the stored pages, then judge. "
                         "Use after changing visible_text; costs no requests.")
    ap.add_argument("--workers", type=int, default=8,
                    help="parallel fetches; this laptop's ceiling is 12")
    ap.add_argument("--max-age", type=int, default=30,
                    help="days before a cached SUCCESSFUL probe is refetched")
    ap.add_argument("--retry-age", type=int, default=3,
                    help="days before a cached FAILURE is retried; check_homepages' "
                         "rule is that a non-200 needs two runs to agree, so a "
                         "timeout or a 429 must not be trusted for a month")
    ap.add_argument("--refresh", action="store_true", help="ignore cached probes")
    ap.add_argument("--output", help="where to write the verdicts; defaults to "
                    "data/raw/url_identity.json. Pass it when checking a list "
                    "that is not the catalog, or the catalog's own results are "
                    "silently overwritten by a 55-row side quest.")
    args = ap.parse_args()
    # I/O-bound or not, this machine throttles hard above eight.
    workers = max(1, min(args.workers, 12))

    src = read_json(Path(args.input))
    rows = src["tools"] if isinstance(src, dict) and "tools" in src else (
        src["list"] if isinstance(src, dict) else src)
    rows = [t for t in rows if t.get("url") or t.get("homepage")]
    if args.only:
        rows = [t for t in rows if t.get("name") == args.only]
    if args.limit:
        rows = rows[:args.limit]

    cache = read_json(CACHE) if CACHE.exists() else {}
    pages, llm = cache.setdefault("pages", {}), cache.setdefault("llm", {})
    key = os.environ.get("DEEPINFRA_API_KEY") or os.environ.get("DEEPINFRA_TOKEN") or ""
    if not key and not args.no_llm:
        print("no DEEPINFRA_API_KEY; running deterministic verdicts only", file=sys.stderr)
        args.no_llm = True
    use_llm = not args.no_llm
    clock = threading.Lock()
    fresh_after = (date.today() - timedelta(days=args.max_age)).isoformat()
    retry_after = (date.today() - timedelta(days=args.retry_age)).isoformat()

    def probe(t: dict) -> dict | None:
        """Fetch if needed, judge, and return one row."""
        url = t.get("url") or t.get("homepage")
        with clock:
            hit = pages.get(url)
        # A cached probe is reused whatever its grade. Caching only the
        # successes meant a resume re-probed every dead host, which is the
        # slowest quarter of the run and the part least likely to have changed.
        cutoff = fresh_after if (hit or {}).get("grade") == "ok" else retry_after
        usable = hit and not args.refresh and hit.get("checked", "") >= cutoff
        if args.rejudge or args.reextract:
            if not hit:
                return None
            usable = True
        if usable:
            grade, final = hit.get("grade", "ok"), hit.get("final_url", url)
            title, text = hit.get("title", ""), hit.get("text", "")
            if args.reextract:
                html = load_page(url)
                if html:
                    title, text = page_title(html), visible_text(html)
                    with clock:
                        pages[url] = redact_emails({**hit, "title": title, "text": text})
        elif args.rejudge:
            return None
        else:
            grade, html, final = fetch(url)
            if html:
                store_page(url, html)
            title = page_title(html) if html else ""
            text = visible_text(html) if html else ""
            with clock:
                # Scrubbed on the way in. This cache is committed and the repo
                # is public, and a lab homepage's "contact: someone@..." is
                # exactly the third-party address repo_map.json was leaking.
                pages[url] = redact_emails(
                    {"grade": grade, "title": title, "text": text,
                     "final_url": final, "checked": date.today().isoformat()})
        v, why = verdict_for(t, title, text, grade, key, args.model, llm, clock, use_llm)
        return {"name": t["name"], "url": url, "final_url": final,
                "grade": grade, "verdict": v, "why": why, "title": title}

    out_path = Path(args.output) if args.output else OUT
    out, counts, done = [], {}, 0
    serial = args.rejudge or args.reextract
    with ThreadPoolExecutor(max_workers=1 if serial else workers) as pool:
        for row in pool.map(probe, rows):
            done += 1
            if row is None:
                continue
            counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
            out.append(row)
            if row["verdict"] == "mismatch":
                print(f"  MISMATCH {row['name'][:22]:24s} {row['url'][:44]:46s} {row['why'][:52]}")
            # Written as we go. The last run was killed at 1550/2137 and the
            # results existed only in memory, so none of them survived.
            if done % 50 == 0:
                with clock:
                    write_json(CACHE, cache)
                    write_json(out_path, {"count": len(out), "list": out})
                print(f"  {done}/{len(rows)}", file=sys.stderr)

    write_json(CACHE, cache)
    write_json(out_path, {"count": len(out), "list": out})
    print(f"\n{len(out)} urls checked")
    for k in ("confirmed", "undecided", "mismatch", "unreadable", "unchecked"):
        if counts.get(k):
            print(f"  {counts[k]:5d}  {k}")
    print(f"-> {out_path}")


if __name__ == "__main__":
    main()
