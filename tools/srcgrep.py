#!/usr/bin/env python3
"""Grab verbatim source sentences for a ledger.

Usage: tools/srcgrep.py <url> <regex> [<regex> ...] [--w 220]
Fetches the page (SEC-friendly UA, strips tags), prints each match with surrounding text so the quote can be
copied verbatim into the ledger. Caches pages in /tmp/srcgrep/.
"""
import hashlib, html, os, re, sys, urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Macintosh) CatchingKnives research son.research@example.com"}


def page(url):
    os.makedirs("/tmp/srcgrep", exist_ok=True)
    f = "/tmp/srcgrep/" + hashlib.md5(url.encode()).hexdigest()
    if os.path.exists(f):
        return open(f, encoding="utf-8").read()
    raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read().decode("utf-8", "ignore")
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
    t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw))).replace("\xa0", " ")
    open(f, "w", encoding="utf-8").write(t)
    return t


def main():
    a = sys.argv[1:]
    w = 220
    if "--w" in a:
        i = a.index("--w"); w = int(a[i + 1]); del a[i:i + 2]
    url, pats = a[0], a[1:]
    t = page(url)
    print(f"# {url} ({len(t)} chars)")
    for p in pats:
        ms = list(re.finditer(p, t, re.I))
        print(f"\n## /{p}/ {len(ms)} hits")
        for m in ms[:4]:
            print("  ..." + t[max(0, m.start() - w):m.end() + w] + "...")


if __name__ == "__main__":
    main()
