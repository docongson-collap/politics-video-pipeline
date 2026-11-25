#!/usr/bin/env python3
"""Envato (app.envato.com) via owner's exported cookies (.secrets/envato_cookies.txt) — no Chrome/CDP needed.
  envato.py search "<term>" [stock-video|music]      -> JSON list {itemUuid,title,author}
  envato.py get <itemUuid> <itemType> <out_path> [project] -> licenses item to project + downloads original + license PDF
Cookies expire: if a call returns sign-in HTML, re-export cookies from Chrome."""
import json, os, subprocess, sys, urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# copied from Travel/tools/envato.py 22/11; cookies are owner's single Envato login, read in place (never copied/printed)
SEC = Path(os.environ.get("ENVATO_SECRETS", str(ROOT.parent / "Travel/.secrets")))
CK = SEC / "envato_cookies.txt"; UA = (SEC / "envato_ua.txt").read_text().strip()
APP = "https://app.envato.com"


def fetch(path):
    r = subprocess.run(["curl", "-s", "-f", "-b", str(CK), "-A", UA, APP + path], capture_output=True, text=True)
    if r.returncode: raise RuntimeError(f"HTTP fail {path[:80]} rc={r.returncode}")
    return r.stdout


def turbo(txt):
    """decode React-Router turbo-stream (first line) into python objects"""
    a = json.loads(txt.split("\n")[0]); memo = {}

    def d(i):
        if isinstance(i, int) and i < 0: return None
        if i in memo: return memo[i]
        v = a[i]
        if isinstance(v, dict):
            o = {}; memo[i] = o
            for k, x in v.items(): o[a[int(k[1:])]] = d(x)
            return o
        if isinstance(v, list):
            if v and isinstance(v[0], str) and v[0] in ("D", "P", "Z", "R", "S", "Y"): return v  # special types
            o = []; memo[i] = o; o.extend(d(x) for x in v); return o
        return v
    return d(0)


def uuid_of(code):
    """Elements item code (e.g. 2VCXVNU) -> app itemUuid + itemType via the legacy redirect"""
    r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{redirect_url}", "-b", str(CK), "-A", UA,
                        f"https://elements.envato.com/x-{code}"], capture_output=True, text=True).stdout
    q = urllib.parse.parse_qs(urllib.parse.urlparse(r).query)
    if "itemUuid" not in q: raise RuntimeError(f"{code}: no redirect ({r[:120]})")
    return q["itemUuid"][0], q.get("itemType", ["stock-video"])[0]


def search(term, itype="stock-video", page=1):
    q = urllib.parse.urlencode({"itemType": itype, "term": term, "page": page})
    D = turbo(fetch(f"/search.data?{q}"))
    sr = ((D.get("routes/_explore/layout") or {}).get("data") or {}).get("searchResults") or {}
    if sr.get("cards"):  # 11/2026 layout: real results are searchResults.cards (the generic walk picked up promo music first)
        return [{"itemUuid": c["item"]["itemUuid"], "title": c["item"]["title"], "authorUsername": c["item"].get("authorUsername"),
                 "duration": c["item"].get("lengthSeconds"), "itemType": c["item"].get("itemType"),
                 "preview": c["item"].get("videoUrl"),
                 "img": ((c["item"].get("image") or {}).get("srcSet") or "").split(" ")[0] or None,
                 "formats": [f.get("shortLabel") for f in c["item"].get("downloadFormats") or []]}
                for c in sr["cards"] if c.get("item", {}).get("itemUuid")]
    out, seen = [], set()

    def walk(o):  # results live in the layout route; collect every item-like dict
        if isinstance(o, dict):
            if o.get("itemUuid") and o.get("title") and o["itemUuid"] not in seen:
                seen.add(o["itemUuid"]); out.append({k: o.get(k) for k in ("itemUuid", "title", "authorUsername", "duration", "itemType")})
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(D)
    return out


def get(uuid, itype, out, project="Politics"):
    out = Path(out); out.parent.mkdir(parents=True, exist_ok=True)
    q = urllib.parse.urlencode({"itemUuid": uuid, "itemType": itype, "projectName": project})
    D = turbo(fetch(f"/download.data?{q}"))["routes/download/route"]["data"]
    url = D.get("downloadUrl")
    if not url: raise RuntimeError(f"no downloadUrl: {str(D)[:300]}")
    ext = Path(urllib.parse.urlparse(url).path).suffix or ".bin"
    dst = out.with_suffix(ext)
    if not (dst.exists() and dst.stat().st_size > 0):
        subprocess.run(["curl", "-s", "-f", "--retry", "3", "-o", str(dst) + ".part", url], check=True)
        os.replace(str(dst) + ".part", dst)
    L = turbo(fetch(f"/item-licenses.data?{urllib.parse.urlencode({'itemUuid': uuid})}"))["routes/item-licenses/route"]["data"]["licenses"]
    lic = [x for x in L if x.get("name") == project] or L
    pdf = None
    if lic and lic[0].get("licenseFileDownloadUrl"):
        pdf = out.parent / f"{out.stem}.license.pdf"
        subprocess.run(["curl", "-s", "-f", "-L", "-b", str(CK), "-A", UA, "-o", str(pdf), lic[0]["licenseFileDownloadUrl"]])
    return {"file": str(dst), "license_id": lic[0]["id"] if lic else None, "license_pdf": str(pdf) if pdf else None}


if __name__ == "__main__":
    if sys.argv[1] == "search": print(json.dumps(search(sys.argv[2], *(sys.argv[3:4] or ["stock-video"])), ensure_ascii=False, indent=0))
    elif sys.argv[1] == "get": print(json.dumps(get(*sys.argv[2:])))
    elif sys.argv[1] == "code":  # code out_path_noext -> resolve + license + download
        u, t = uuid_of(sys.argv[2]); print(json.dumps({"code": sys.argv[2], "itemUuid": u, "itemType": t, **get(u, t, sys.argv[3])}))
