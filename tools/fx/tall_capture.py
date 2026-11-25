"""Tall real-page capture for capture_pass.py (browser_exec helper; exec() this file inside a browser_exec call after
quote_capture.py). Captures a document-coordinate band [y0, y0+h) of the live page at DPR 2 in ONE screenshot
(captureBeyondViewport) so the camera can scroll from the headline down to a later paragraph, and writes JSON with the
mark rects in band coordinates (CSS px) — the format capture_pass.py expects (marks[i] = list of line rects).

cap_tall(key, marks, out_dir, y0=None, h=None, pad_top=140, pad_bot=260)
  page must already be loaded + consent cleared. y0/h default to a band spanning all marks (+ padding).
"""
import json, time, base64, os

HIDE_FIXED_JS = r"""
(() => { let n = 0;
  for (const e of document.querySelectorAll('body *')) { const s = getComputedStyle(e);
    if (s.position === 'fixed' || s.position === 'sticky') { e.style.setProperty('display', 'none', 'important'); n++; } }
  return n; })()
"""


VIS_RECTS_JS = r"""
((marks) => {
  const norm = s => s.replace(/[\u2018\u2019]/g,"'").replace(/[\u201c\u201d]/g,'"').replace(/[\u00a0\u202f\u2009]/g,' ').replace(/\s+/g,' ').toLowerCase();
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const nodes = []; let full = '';
  while (walker.nextNode()) { const n = walker.currentNode; if (!n.parentElement || n.parentElement.closest('script,style,noscript')) continue; nodes.push([n, full.length]); full += n.data; }
  const nf = norm(full); const map = []; let prevSpace = false;
  for (let i = 0; i < full.length; i++) { const sp = /[\s\u00a0\u202f\u2009]/.test(full[i]); if (sp && prevSpace) continue; map.push(i); prevSpace = sp; }
  function rangeFor(a, b) { const r = document.createRange(); let s=null,e=null;
    for (const [n, off] of nodes) { if (s===null && a < off+n.data.length) s=[n,a-off]; if (b <= off+n.data.length) { e=[n,b-off]; break; } }
    if (!s||!e) return null; r.setStart(s[0],Math.max(0,s[1])); r.setEnd(e[0],Math.max(0,e[1])); return r; }
  const res = {marks: [], vw: innerWidth, vh: innerHeight, title: document.title, url: location.href};
  for (const m of marks) { const q = norm(m); let k = nf.indexOf(q), got = null;
    while (k >= 0 && !got) { const r = rangeFor(map[k], map[k+q.length-1]+1);
      const rs = r ? [...r.getClientRects()].filter(x=>x.width>1&&x.height>1) : [];
      if (rs.length) got = rs.map(x=>[x.left,x.top,x.right,x.bottom]); k = nf.indexOf(q, k+1); }
    res.marks.push(got); }
  return res;
})
"""


def cap_tall(key, marks, out_dir, y0=None, h=None, pad_top=140, pad_bot=260, hide_fixed=True):
    os.makedirs(out_dir, exist_ok=True)
    try:
        js(CLEAN_JS); time.sleep(0.6)
    except Exception as e:
        print("clean failed", str(e)[:120])
    if hide_fixed:
        js(HIDE_FIXED_JS)
    js("window.scrollTo(0,0)"); time.sleep(1.0)
    # walk down the page once so lazy content/images load, then back to top
    tot = js("document.documentElement.scrollHeight")
    for yy in range(0, min(tot, 6000), 700):
        js(f"window.scrollTo(0,{yy})"); time.sleep(0.25)
    js("window.scrollTo(0,0)"); time.sleep(1.2)
    if hide_fixed:
        js(HIDE_FIXED_JS)
    prev = None
    for _ in range(6):
        info = js("(" + VIS_RECTS_JS + ")(" + json.dumps(marks) + ")")
        cur = json.dumps(info.get("marks"))
        if cur == prev:
            break
        prev = cur; time.sleep(0.8)
    sy = js("window.scrollY")
    doc = [[[q[0], q[1] + sy, q[2], q[3] + sy] for q in m] if m else None for m in info["marks"]]
    ys = [q[1] for m in doc if m for q in m] + [q[3] for m in doc if m for q in m]
    if y0 is None:
        y0 = max(0, min(ys) - pad_top)
    if h is None:
        h = max(ys) + pad_bot - y0
    w = info["vw"]
    shot = cdp("Page.captureScreenshot", format="png", captureBeyondViewport=True,
               clip={"x": 0, "y": y0, "width": w, "height": h, "scale": 1})   # scale multiplies the DPR-2 override -> 2x image
    open(os.path.join(out_dir, key + ".png"), "wb").write(base64.b64decode(shot["data"]))
    out = {"key": key, "url": info["url"], "title": info["title"], "dpr": 2, "band_y0": y0, "band_h": h, "vw": w,
           "phrases": marks, "marks": [[[q[0], q[1] - y0, q[2], q[3] - y0] for q in m] if m else None for m in doc]}
    json.dump(out, open(os.path.join(out_dir, key + ".json"), "w"), indent=1)
    return out
