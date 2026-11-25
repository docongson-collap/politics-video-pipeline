"""vidIQ VPH collection from YouTube watch pages (sidebar 'N VPH' badges + the watched video's own tags).
Run inside browser_exec via exec(open(...).read()). Profile must be congson.neu (vidIQ logged in)."""
import json, re, time

SIDE_JS = r"""
(() => {
  const out = [];
  for (const r of document.querySelectorAll('yt-lockup-view-model, ytd-compact-video-renderer')) {
    const t = r.innerText || '';
    const m = t.match(/([\d.,]+\s*[KkMm]?)\s*VPH/);
    const a = r.querySelector('a[href*="watch?v="]');
    if (!a) continue;
    const id = (a.href.match(/v=([\w-]{11})/) || [])[1];
    const lines = t.split('\n').map(s => s.trim()).filter(Boolean);
    out.push({id, title: lines.find(s => s.length > 12 && !/VPH|^\d/.test(s)) || lines[0], channel: lines[lines.findIndex(s => s.length > 12 && !/VPH|^\d/.test(s)) + 1] || '',
              vph: m ? m[1].replace(/\s/g, '') : null, raw: lines.slice(0, 8).join(' | ')});
  }
  return out;
})()
"""

SELF_JS = r"""
(() => {
  const d = (window.ytInitialPlayerResponse || {}).videoDetails || {};
  const t = document.body.innerText;
  return {id: d.videoId, title: d.title, channel: d.author, views: +d.viewCount || 0, keywords: d.keywords || []};
})()
"""


def num(s):
    if not s:
        return 0.0
    s = s.replace(",", "")
    k = 1000 if s[-1] in "kK" else 1e6 if s[-1] in "mM" else 1
    try:
        return float(s.rstrip("kKmM")) * k
    except ValueError:
        return 0.0


def ev(sid, e):
    return cdp("Runtime.evaluate", session_id=sid, expression=e, returnByValue=True)["result"].get("value")


def watch(sid, vid, wait=9):
    cdp("Page.navigate", session_id=sid, url=f"https://www.youtube.com/watch?v={vid}")
    time.sleep(wait)
    ev(sid, "window.scrollBy(0, 1800)"); time.sleep(2.5)
    me = ev(sid, SELF_JS) or {}
    side = ev(sid, SIDE_JS) or []
    for s in side:
        s["vph_n"] = num(s["vph"])
    return me, side
