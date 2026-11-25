"""vidIQ Search Companion keyword score for a query (YouTube search page). Run inside browser_exec."""
import re, time, urllib.parse

KW_JS = r"""(() => { const p=[...document.querySelectorAll('*')].find(e => /Keyword Score/.test(e.innerText||'') && /Search Term Statistics/.test(e.innerText||'') && (e.innerText||'').length<2500); return p ? p.innerText : ''; })()"""


def kw_score(sid, q, wait=8):
    cdp("Page.navigate", session_id=sid, url="https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(q))
    txt = ""
    for _ in range(8):
        time.sleep(wait / 4 if _ else wait)
        txt = cdp("Runtime.evaluate", session_id=sid, expression=KW_JS, returnByValue=True)["result"].get("value") or ""
        if re.search(r"Overall Score", txt):
            break
    g = lambda pat: (re.search(pat, txt, re.S) or [None, None])[1]
    return {"q": q, "score": g(r"(\d+)\s*\n\s*Overall Score"), "volume": g(r"VOLUME\s*\n\s*(\w+)"),
            "competition": g(r"COMPETITION\s*\n\s*(\w+)"), "highest_views": g(r"HIGHEST VIEWS\s*\n\s*([\d.,]+[KMB]?)"),
            "avg_views": g(r"AVG VIEWS\s*\n\s*([\d.,]+[KMB]?)"), "raw": txt[:600]}
