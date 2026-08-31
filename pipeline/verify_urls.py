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

Cached on the content hash, so re-running after a rule change is free and only
genuinely changed pages are re-examined.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

import requests

from check_homepages import classify
from config import user_agent
from jsonio import read_json, write_json
# Imported for its side effect as much as its function: llm_assist puts the
# DeepInfra key into the environment when it loads, so reading the key before
# this import reports "no key" on a machine that has one.
from llm_assist import call as llm_call, parse_json

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "cache" / "url_identity.json"
OUT = ROOT / "data" / "raw" / "url_identity.json"

# A browser string, because several university hosts refuse anything else and a
# 403 from a live page is indistinguishable from a dead one at this layer.
BROWSER = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
           "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

TAG = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.S | re.I)
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
    body = TAG.sub(" ", html)
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


def judge(tool: dict, title: str, text: str) -> tuple[str, str]:
    """Deterministic verdict, or 'undecided' when a model should look."""
    named = name_present(tool["name"], title, text)
    shared = terms(tool.get("description", "")) & terms(title + " " + text)
    n = len(shared)
    sample = ", ".join(sorted(shared)[:5])
    if named and n >= 2:
        return "confirmed", f"name on the page and {n} shared terms ({sample})"
    if named and n == 0 and len(text) > 400:
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

Answer ONLY with json: {"belongs": true|false, "confidence": "high"|"medium"|"low", "reason": "<one sentence>"}

Say true when the page is the tool's own page, its repository, its
documentation, or a lab or project page that clearly hosts it.
Say false when the page is about something else entirely - a different tool
that shares the name, a re-registered domain now selling something unrelated, a
generic institutional index, a parked or error page, or a journal landing page.
A page can be sparse, dated or ugly and still be the tool's own page; judge
subject matter, not quality. If the page is empty or gives you nothing to go
on, say false with low confidence."""


def ask_model(tool: dict, title: str, text: str, key: str, model: str, cache: dict) -> dict:
    user = (f"Tool: {tool['name']}\n"
            f"Description: {tool.get('description', '')[:300]}\n\n"
            f"Page title: {title}\n"
            f"Page text: {text[:1800]}")
    ck = f"{model}:{hashlib.sha256((LLM_SYSTEM + user).encode()).hexdigest()[:16]}"
    if ck in cache:
        return cache[ck]
    text_out, _cost, _s = llm_call(model, LLM_SYSTEM, user, key, max_tokens=300)
    got = parse_json(text_out) or {"belongs": None, "confidence": "low",
                                   "reason": "model returned no usable json"}
    cache[ck] = got
    return got


def fetch(http: requests.Session, url: str) -> tuple[str, str, str]:
    try:
        r = http.get(url, timeout=30, allow_redirects=True)
        return classify(r.status_code, ""), r.text if r.status_code < 400 else "", str(r.url)
    except requests.RequestException as e:
        return classify(None, type(e).__name__), "", url


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default=str(ROOT / "data" / "catalog.json"))
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--no-llm", action="store_true", help="deterministic verdicts only")
    ap.add_argument("--model", default="deepseek-ai/DeepSeek-V4-Flash")
    ap.add_argument("--only", help="one tool, by name")
    args = ap.parse_args()

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

    http = requests.Session()
    http.headers.update({"User-Agent": BROWSER, "Accept-Language": "en"})

    out, counts = [], {}
    for i, t in enumerate(rows, 1):
        url = t.get("url") or t.get("homepage")
        grade, html, final = fetch(http, url)
        if grade != "ok" or not html:
            verdict, why = "unchecked", f"page not readable ({grade})"
            title, text = "", ""
        else:
            title, text = page_title(html), visible_text(html)
            h = hashlib.sha256(text.encode()).hexdigest()[:16]
            verdict, why = judge(t, title, text)
            if verdict == "undecided" and not args.no_llm:
                got = ask_model(t, title, text, key, args.model, llm)
                b = got.get("belongs")
                verdict = "confirmed" if b else ("mismatch" if b is False else "undecided")
                why = f"model({got.get('confidence', '?')}): {got.get('reason', '')[:110]}"
            pages[url] = {"hash": h, "title": title, "grade": grade}
        counts[verdict] = counts.get(verdict, 0) + 1
        out.append({"name": t["name"], "url": url, "final_url": final,
                    "grade": grade, "verdict": verdict, "why": why, "title": title})
        if verdict == "mismatch":
            print(f"  MISMATCH {t['name'][:22]:24s} {url[:44]:46s} {why[:50]}")
        if i % 50 == 0:
            print(f"  {i}/{len(rows)}", file=sys.stderr)
            write_json(CACHE, cache)
        time.sleep(0.2)

    write_json(CACHE, cache)
    write_json(OUT, {"count": len(out), "list": out})
    print(f"\n{len(out)} urls checked")
    for k in ("confirmed", "undecided", "mismatch", "unchecked"):
        if counts.get(k):
            print(f"  {counts[k]:5d}  {k}")
    print(f"-> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
