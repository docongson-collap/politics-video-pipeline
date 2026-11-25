"""Quote-card source capture helpers (auto-imported by browser_exec harness via agent_helpers.py import below).

cap_quote(url, key, marks, out_dir): open the real source page, clear consent walls, find the paragraph that
contains marks[0], scroll it to ~42% of the viewport, screenshot at 2x, and save JSON with:
  url, title, paragraph rect, and one or more rects per mark phrase (CSS px, viewport coords).
"""
import json, time, base64, os

CONSENT_JS = r"""
(() => {
  const words = /^(continue without agreeing|reject all|alle ablehnen|ablehnen|accept all|accept|agree|i agree|agree and close|got it|ok|alle akzeptieren|akzeptieren|zustimmen|allow all|accept cookies|accept all cookies)$/i;
  const btns = [...document.querySelectorAll('button, a, [role=button]')];
  for (const b of btns) { const t = (b.innerText || '').trim(); if (words.test(t)) { b.click(); return t; } }
  for (const f of document.querySelectorAll('iframe')) {
    try { for (const b of f.contentDocument.querySelectorAll('button')) { const t=(b.innerText||'').trim(); if (words.test(t)) { b.click(); return 'iframe:'+t; } } } catch(e) {}
  }
  return null;
})()
"""

FIND_JS = r"""
((marks) => {
  const norm = s => s.replace(/[\u2018\u2019]/g,"'").replace(/[\u201c\u201d]/g,'"').replace(/[\u00a0\u202f\u2009]/g,' ').replace(/\s+/g,' ').toLowerCase();
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const nodes = []; let full = '';
  while (walker.nextNode()) { const n = walker.currentNode; if (!n.parentElement || n.parentElement.closest('script,style,noscript')) continue;
    nodes.push([n, full.length]); full += n.data; }
  const nf = norm(full);
  // map normalized index -> raw index (normalization only collapses whitespace + swaps quotes)
  const map = []; let j = 0; let prevSpace = false;
  for (let i = 0; i < full.length; i++) { const c = full[i]; const sp = /[\s\u00a0\u202f\u2009]/.test(c);
    if (sp && prevSpace) continue; map.push(i); prevSpace = sp; }
  function rangeFor(rawStart, rawEnd) {
    const r = document.createRange(); let s = null, e = null;
    for (const [n, off] of nodes) {
      if (s === null && rawStart < off + n.data.length) s = [n, rawStart - off];
      if (rawEnd <= off + n.data.length) { e = [n, rawEnd - off]; break; }
    }
    if (!s || !e) return null; r.setStart(s[0], Math.max(0,s[1])); r.setEnd(e[0], Math.max(0,e[1])); return r;
  }
  const out = {marks: []};
  for (const m of marks) {
    const k = nf.indexOf(norm(m));
    if (k < 0) { out.marks.push(null); continue; }
    const r = rangeFor(map[k], map[k + norm(m).length - 1] + 1);
    out.marks.push(r);
  }
  if (!out.marks[0]) return {error: 'first mark not found'};
  const block = out.marks[0].startContainer.parentElement.closest('p,li,blockquote,h1,h2,h3,td,div');
  document.documentElement.style.scrollBehavior = 'auto'; document.body.style.scrollBehavior = 'auto';
  const rr = out.marks[0].getBoundingClientRect();
  const dy = rr.top - window.innerHeight * 0.42;
  window.scrollTo({top: Math.max(0, window.scrollY + dy), behavior: 'instant'});
  // some sites scroll <body> (html height = viewport) instead of the window
  if (Math.abs(out.marks[0].getBoundingClientRect().top - window.innerHeight * 0.42) > 60) {
    for (const el of [document.body, document.documentElement, document.scrollingElement]) {
      if (el && el.scrollHeight > el.clientHeight + 50) { el.style.scrollBehavior = 'auto'; el.scrollTop = el.scrollTop + (out.marks[0].getBoundingClientRect().top - window.innerHeight * 0.42); }
    }
  }
  return {ok: true};
})
"""

RECTS_JS = r"""
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
  const res = {marks: [], block: null, vw: innerWidth, vh: innerHeight, title: document.title, url: location.href};
  let first = null;
  for (const m of marks) { const k = nf.indexOf(norm(m)); if (k<0) { res.marks.push(null); continue; }
    const r = rangeFor(map[k], map[k+norm(m).length-1]+1); if (!first) first = r;
    res.marks.push([...r.getClientRects()].filter(q=>q.width>1).map(q=>[q.left,q.top,q.right,q.bottom])); }
  if (first) { const b = first.startContainer.parentElement.closest('p,li,blockquote,h1,h2,h3,td,div'); const q=b.getBoundingClientRect(); res.block=[q.left,q.top,q.right,q.bottom];
    res.block_text = b.innerText.slice(0, 600);
    const r = document.createRange(); r.selectNodeContents(b); const L = {};
    for (const q of r.getClientRects()) { if (q.width < 2 || q.height < 4) continue; const k = Math.round(q.top / 3);
      const o = L[k]; L[k] = o ? [Math.min(o[0], q.left), Math.min(o[1], q.top), Math.max(o[2], q.right), Math.max(o[3], q.bottom)] : [q.left, q.top, q.right, q.bottom]; }
    res.lines = Object.values(L).sort((a, b) => a[1] - b[1]); }
  return res;
})
"""


CLEAN_JS = r"""
(() => {
  // remove consent dialogs / modal overlays / sticky ads that cover the article (keep the site header)
  let n = 0;
  for (const e of document.querySelectorAll('body *')) {
    const s = getComputedStyle(e); if (s.position !== 'fixed' && s.position !== 'sticky') continue;
    const r = e.getBoundingClientRect();
    const big = r.width * r.height > innerWidth * innerHeight * 0.12;
    const isHeader = r.top <= 2 && r.height < 140 && r.width > innerWidth * 0.8;
    const bottomBar = r.bottom >= innerHeight - 4 && r.width > innerWidth * 0.6;          // cookie bars docked at the bottom
    const dimmer = parseFloat(s.opacity) < 1 || /rgba\(0, 0, 0, 0?\.\d+\)/.test(s.backgroundColor);
    if ((big || bottomBar || dimmer || /cookie|consent|privacy|gdpr|modal|overlay|popup|banner|newsletter|subscribe|onetrust|truste|didomi|cmp/i.test(e.className + ' ' + e.id)) && !isHeader) { e.style.setProperty('display', 'none', 'important'); n++; }
  }
  for (const id of ['onetrust-consent-sdk', 'truste-consent-track', 'CybotCookiebotDialog', 'usercentrics-root', 'didomi-host', 'usercentrics-cmp-ui']) {
    const e = document.getElementById(id); if (e) { e.remove(); n++; }
  }
  // site-specific modal hosts seen in the wild (FedEx country picker); generic: any [class*=modal] wrapper + its backdrop
  for (const e of document.querySelectorAll('fedex-geo-locator, .js-geo-locator, div[class*="u-modal__"], [class*="modal-backdrop"], [class*="Modal__overlay"], [aria-modal="true"]')) { if (e !== document.body && e !== document.documentElement && !e.contains(document.querySelector('main, article'))) { e.remove(); n++; } }
  if (document.body) document.body.classList.forEach(c => { if (/modal|noscroll|no-scroll|overflow|locked/i.test(c)) document.body.classList.remove(c); });
  for (const e of document.querySelectorAll('iframe, [id^="google_ads"], [class*="advert" i], [class*="ad-slot" i], [class*="adslot" i], video')) { e.style.setProperty('visibility', 'hidden', 'important'); n++; }
  // paywall blur / scroll-reveal animations: force every text container fully visible and sharp
  const st = document.createElement('style');
  st.textContent = `*{filter:none!important;-webkit-filter:none!important;backdrop-filter:none!important;animation:none!important;transition:none!important}
    p,li,h1,h2,h3,h4,blockquote,span,div,section,article{opacity:1!important;transform:none!important;visibility:visible!important}
    iframe,video,[id^="google_ads"],[class*="player" i],[class*="video" i]:not(body):not(html){visibility:hidden!important}`;
  document.head.appendChild(st);
  document.documentElement.style.overflow = 'auto'; document.body.style.overflow = 'auto';
  return n;
})()
"""


def _measure_and_shoot(marks):
    """scroll onto the marks, wait until the layout is STABLE (two equal measurements), then screenshot."""
    info = None; prev = None
    for attempt in range(8):
        rs = [q for m in ((info or {}).get("marks") or []) if m for q in m]
        if not (rs and min(q[1] for q in rs) > 40 and max(q[3] for q in rs) < (info or {}).get("vh", 900) - 40):
            js("(" + FIND_JS + ")(" + json.dumps(marks) + ")")
        time.sleep(0.7 + 0.2 * attempt)
        info = js("(" + RECTS_JS + ")(" + json.dumps(marks) + ")")
        cur = json.dumps(info.get("marks"))
        rs = [q for m in (info.get("marks") or []) if m for q in m]
        inview = rs and min(q[1] for q in rs) > 40 and max(q[3] for q in rs) < info["vh"] - 40
        if inview and cur == prev:
            break
        prev = cur
    shot = cdp("Page.captureScreenshot", format="png")
    after = js("(" + RECTS_JS + ")(" + json.dumps(marks) + ")")        # layout must not have moved during the shot
    info["stable"] = json.dumps(after.get("marks")) == json.dumps(info.get("marks"))
    return info, shot


def cap_quote(url, key, marks, out_dir, w=1440, h=900, wait=4):
    os.makedirs(out_dir, exist_ok=True)
    cdp("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=2, mobile=False)
    cdp("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "light"}])
    goto_url(url); wait_for_load(); time.sleep(wait)
    for _ in range(3):
        c = js(CONSENT_JS)
        if c:
            time.sleep(1.5)
        else:
            break
    r = js("(" + FIND_JS + ")(" + json.dumps(marks) + ")")
    time.sleep(1.2)
    js(CONSENT_JS)
    js(CLEAN_JS); time.sleep(0.8)                  # clean FIRST (it reflows the page), then scroll + measure + shoot
    for _ in range(3):
        info, shot = _measure_and_shoot(marks)
        if info["stable"]:
            break
    open(os.path.join(out_dir, key + ".png"), "wb").write(base64.b64decode(shot["data"]))
    info["find"] = r; info["key"] = key; info["req_url"] = url; info["dpr"] = 2
    json.dump(info, open(os.path.join(out_dir, key + ".json"), "w"), indent=1)
    return info
