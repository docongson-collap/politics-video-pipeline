"""vidIQ VPH scan helpers, run inside browser_exec via exec(open(...).read()).
scan(target_id, query) -> list of {title, channel, vph, views, href} read from YouTube search results with the vidIQ overlay."""
import json, time, urllib.parse

READ_JS = r"""
(() => {
  const out = [];
  for (const r of document.querySelectorAll('ytd-video-renderer')) {
    const a = r.querySelector('a#video-title'); if (!a) continue;
    const txt = r.innerText;
    const m = txt.match(/([\d.,]+\s*[KkMm]?)\s*VPH/);
    const ch = r.querySelector('ytd-channel-name a, #channel-name a');
    out.push({title: a.title || a.innerText.trim(), href: a.href, channel: ch ? ch.innerText.trim() : '',
              vph: m ? m[1].replace(/\s/g,'') : null, meta: (r.querySelector('#metadata-line')||{}).innerText || ''});
  }
  return out;
})()
"""


def _ev(sid, expr):
    r = cdp("Runtime.evaluate", session_id=sid, expression=expr, returnByValue=True, awaitPromise=True)
    return r.get("result", {}).get("value")


def vph_num(s):
    if not s:
        return 0.0
    s = s.replace(",", "")
    mult = 1000 if s[-1] in "kK" else 1e6 if s[-1] in "mM" else 1
    try:
        return float(s.rstrip("kKmM")) * mult
    except ValueError:
        return 0.0


def scan(sid, q, wait=7, sp=""):
    """sp = YouTube filter param, e.g. 'EgIIBA%3D%3D' (This month). Never append it to q (it gets URL-quoted into the search text)."""
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(q) + (f"&sp={sp}" if sp else "")
    cdp("Page.navigate", session_id=sid, url=url)
    time.sleep(wait)
    _ev(sid, "window.scrollBy(0, 2500)"); time.sleep(2.5)
    _ev(sid, "window.scrollTo(0, 0)"); time.sleep(1)
    rows = _ev(sid, READ_JS) or []
    for x in rows:
        x["vph_n"] = vph_num(x["vph"])
    return rows


def keywords(sid, vid):
    cdp("Page.navigate", session_id=sid, url=f"https://www.youtube.com/watch?v={vid}")
    time.sleep(6)
    return _ev(sid, "(window.ytInitialPlayerResponse && ytInitialPlayerResponse.videoDetails && ytInitialPlayerResponse.videoDetails.keywords) || []")
