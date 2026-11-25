"""Read vidIQ's live VPH (Views tab of the vidIQ panel) + tags for a list of video ids. Run inside browser_exec."""
import json, re, time

PANEL_JS = r"""(() => {
  const all = [...document.querySelectorAll('*')];
  const el = all.find(e => /VPH/.test(e.innerText || '') && e.innerText.length < 500);
  return el ? el.innerText : '';
})()"""
SELF_JS = r"""(() => { const d=(window.ytInitialPlayerResponse||{}).videoDetails||{}; const m=(window.ytInitialPlayerResponse||{}).microformat?.playerMicroformatRenderer||{};
  return {id:d.videoId,title:d.title,channel:d.author,views:+d.viewCount||0,keywords:d.keywords||[],published:m.publishDate||'',len:+d.lengthSeconds||0,
          thumb:(d.thumbnail?.thumbnails||[]).slice(-1)[0]?.url||''}; })()"""


def _ev(sid, e):
    kwargs = {}
    if sid:
        kwargs["session_id"] = sid
    return cdp("Runtime.evaluate", expression=e, returnByValue=True, **kwargs)["result"].get("value")


def vidiq_vph(sid, vid, wait=8):
    kwargs = {}
    if sid:
        kwargs["session_id"] = sid
    cdp("Page.navigate", url=f"https://www.youtube.com/watch?v={vid}", **kwargs)
    time.sleep(wait)
    _ev(sid, "document.querySelector('video') && document.querySelector('video').pause()")
    _ev(sid, "[...document.querySelectorAll('button, div[role=tab]')].find(b => /^Views$/.test((b.innerText||'').trim()))?.click()")
    txt = ""
    for _ in range(5):
        time.sleep(1.5)
        txt = _ev(sid, PANEL_JS) or ""
        if "VPH" in txt:
            break
    m = re.search(r"VPH\s*\n+\s*([\d.,]+\s*[KkMm]?)", txt)
    me = _ev(sid, SELF_JS) or {}
    me["vidiq_vph_raw"] = m.group(1).strip() if m else None
    s = (me["vidiq_vph_raw"] or "").replace(",", "")
    me["vidiq_vph"] = (float(s.rstrip("kKmM")) * (1000 if s[-1:] in "kK" else 1e6 if s[-1:] in "mM" else 1)) if s else None
    return me
