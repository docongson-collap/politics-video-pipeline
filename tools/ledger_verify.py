#!/usr/bin/env python3
"""Mechanical ledger gate: open every claim URL and check the quoted text is really on the page.

Usage: tools/ledger_verify.py <ledger.md> [--out report.md]
Per claim: OK (≥60% of quote fragments found), WEAK (some found), MISSING (page loads, quote not there),
DEAD (404/timeout), PAYWALL (401/403), NOSRC (no URL), LOCAL (URL unreachable, quote only in a **Local:** file).
Exit 1 if any MISSING/DEAD/NOSRC/LOCAL. The live URL always wins over a Local file.
Fragments = quote split on '...' / ';' / '[...]' brackets, numbers normalised; short fragments (<12 chars) skipped.
"""
import argparse, html, os, re, ssl, sys, urllib.error, urllib.request
try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except Exception:
    SSL_CTX = None

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}


def norm(s):
    s = html.unescape(s).replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    s = s.replace("\u2014", "-").replace("\u2013", "-").replace("\xa0", " ")
    return re.sub(r"\s+", " ", s).lower()


def fetch(url, cache={}):
    if url in cache:
        return cache[url]
    try:
        req = urllib.request.Request(url, headers=UA)
        if SSL_CTX:
            r = urllib.request.urlopen(req, timeout=40, context=SSL_CTX)
        else:
            r = urllib.request.urlopen(req, timeout=40)
        raw = r.read()
        if raw[:5] == b"%PDF-" or "pdf" in (r.headers.get("Content-Type") or "").lower():
            import subprocess, tempfile
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                f.write(raw)
            t = subprocess.run(["pdftotext", "-q", f.name, "-"], capture_output=True, text=True).stdout
            os.unlink(f.name)
            cache[url] = ("ok", norm(t))
            return cache[url]
        t = raw.decode("utf-8", "ignore")
        t = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", t, flags=re.S | re.I)
        res = ("ok", norm(re.sub(r"<[^>]+>", " ", t)))
    except urllib.error.HTTPError as e:
        res = ("paywall" if e.code in (401, 402, 403) else "dead", str(e.code))
    except Exception as e:
        res = ("dead", str(e) or type(e).__name__)
    cache[url] = res
    return res


def claims(md):
    for blk in re.split(r"\n(?=### )", md):
        m = re.match(r"### ([CH]\d+)\s*\|?\s*(.*)", blk)
        if not m:
            continue
        q = re.search(r"\*\*Exact Quote:\*\*\s*`?(.+?)`?\s*$", blk, re.M)
        u = re.search(r"\*\*URL:\*\*\s*(\S+)", blk)
        loc = re.search(r"\*\*Local:\*\*\s*(\S+)", blk)
        yield m.group(1), m.group(2).strip(), (q.group(1) if q else ""), (u.group(1) if u else ""), ("DROPPED" in blk), (loc.group(1) if loc else "")


def frags(q):
    q = re.sub(r"\[[^\]]*\]", "|", q)
    parts = re.split(r"\.\.\.|…|;|\|", q)
    return [norm(p).strip(" .,:\"'") for p in parts if len(p.strip()) >= 12]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ledger")
    ap.add_argument("--out")
    a = ap.parse_args()
    rows, bad = [], 0
    for cid, title, quote, url, dropped, local in claims(open(a.ledger, encoding="utf-8").read()):
        if dropped:
            st, note = "DROPPED", ""
        elif not url.startswith("http"):
            st, note = "NOSRC", ""
        else:
            # Always check the LIVE URL first. A Local file is only a fallback when the URL cannot be fetched, and is
            # reported as LOCAL (blocking): 2026-11-06 a researcher wrote its own "extracts" file and 76 rows passed on it.
            kind, body = fetch(url)
            used_local = False
            if kind != "ok" and local:
                lp = os.path.join(os.path.dirname(os.path.abspath(a.ledger)), local)
                if os.path.exists(lp):
                    kind, body, used_local = "ok", norm(open(lp, encoding="utf-8", errors="ignore").read()), True
            if kind != "ok":
                st, note = kind.upper(), body
            else:
                fs = frags(quote)
                hit = [f for f in fs if f in body]
                share = len(hit) / len(fs) if fs else 0
                st = "OK" if share >= 0.6 else "WEAK" if hit else "MISSING"
                nums = set(re.findall(r"\d[\d,]*\.?\d*", quote)) - {""}
                nums = {n.rstrip(".,") for n in nums if len(n.rstrip(".,")) >= 3}
                nhit = {n for n in nums if n in body}
                if st != "OK" and nums and len(nhit) == len(nums):
                    st = "NUMS"  # every number is on the page but the wording was paraphrased
                note = f"{len(hit)}/{len(fs)} fragments, {len(nhit)}/{len(nums)} numbers"
                if used_local:
                    st, note = "LOCAL", note + " (URL unreachable; quote only in local file)"
        bad += st in ("MISSING", "DEAD", "NOSRC", "LOCAL")
        rows.append(f"| {cid} | {st} | {note} | {title[:60]} | {url[:90]} |")
    rep = "| ID | status | note | claim | url |\n|---|---|---|---|---|\n" + "\n".join(rows)
    summ = {s: sum(f"| {s} |" in r for r in rows) for s in ("OK", "NUMS", "WEAK", "MISSING", "DEAD", "PAYWALL", "NOSRC", "LOCAL", "DROPPED")}
    rep += "\n\nSUMMARY: " + " ".join(f"{k}={v}" for k, v in summ.items()) + f" total={len(rows)}\n"
    if a.out:
        open(a.out, "w", encoding="utf-8").write(rep)
    print(rep)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
