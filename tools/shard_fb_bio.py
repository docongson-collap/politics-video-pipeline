#!/usr/bin/env python3
"""Read or set the Intro bio of the account in ShardBrowser profile "Facebook" (Politics only; same pattern as shard_fb.py).
usage: ~/.hermes/hermes-agent/venv/bin/python tools/shard_fb_bio.py read [OUT.json]
       ~/.hermes/hermes-agent/venv/bin/python tools/shard_fb_bio.py set "new bio text (<=101 chars)" [OUT.json]
Screenshots go to control/facebook/."""
import asyncio, base64, importlib.util, json, sys, time, urllib.request
import websockets

spec = importlib.util.spec_from_file_location("sm", "/Volumes/WORK/Application/shard_migrate.py")
argv, sys.argv = sys.argv, ["x", "__none__"]
sm = importlib.util.module_from_spec(spec); spec.loader.exec_module(sm)  # type: ignore
sys.argv = argv
NAME = "Facebook"  # owner: Politics manages ONLY this profile. Never touch any other ShardBrowser profile.
MODE = sys.argv[1]
BIO = sys.argv[2] if MODE == "set" else None
OUT = sys.argv[3] if MODE == "set" and len(sys.argv) > 3 else (sys.argv[2] if MODE == "read" and len(sys.argv) > 2 else None)
if BIO is not None and len(BIO) > 101:
    raise SystemExit(f"bio too long: {len(BIO)} > 101")
LOG = "control/facebook"
TS = time.strftime("%Y%m%d_%H%M")

prof = next(p for p in sm.api("GET", "/profiles") if p.get("name") == NAME)
pid = prof["id"]
if prof.get("running"):
    raise SystemExit("profile is open (someone is using it) - not touching it")
port = sm.api("POST", f"/profiles/{pid}/start", {"headless": True})["cdp"]["port"]
time.sleep(5)

INTRO_JS = r'''(() => {
  const h = [...document.querySelectorAll('h2, span')].find(e => e.innerText && e.innerText.trim() === 'Intro');
  if (!h) return null;
  let box = h; for (let i = 0; i < 8 && box; i++) { box = box.parentElement; if (box && box.innerText.length > 40) break; }
  return box ? box.innerText.slice(0, 800) : null;
})()'''


async def main():
    t = json.load(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{port}/json/new?about:blank", method="PUT")))
    async with websockets.connect(t["webSocketDebuggerUrl"], max_size=None) as ws:
        n = 0

        async def call(m, p={}):
            nonlocal n; n += 1; await ws.send(json.dumps({"id": n, "method": m, "params": p}))
            while True:
                x = json.loads(await ws.recv())
                if x.get("id") == n: return x.get("result", {})

        async def ev(e):
            return (await call("Runtime.evaluate", {"expression": e, "returnByValue": True, "awaitPromise": True})).get("result", {}).get("value")

        async def shot(tag):
            d = (await call("Page.captureScreenshot", {"format": "png"})).get("data")
            if d:
                p = f"{LOG}/bio_{TS}_{tag}.png"; open(p, "wb").write(base64.b64decode(d)); return p

        async def click_text(txt, scope="document"):
            return await ev(f'''(() => {{
              const els = [...{scope}.querySelectorAll('div[role=button], span, a[role=button]')].filter(e => e.innerText && e.innerText.trim() === {json.dumps(txt)} && e.offsetParent);
              if (!els.length) return false; const e = els[0].closest('[role=button]') || els[0]; e.scrollIntoView({{block:'center'}}); e.click(); return true; }})()''')

        await call("Emulation.setDeviceMetricsOverride", {"width": 1440, "height": 1000, "deviceScaleFactor": 1, "mobile": False})
        await call("Page.navigate", {"url": "https://www.facebook.com/me"}); await asyncio.sleep(12)
        out: dict = {"read_at": time.strftime("%Y-%m-%d %H:%M"), "url": await ev("location.href"),
                     "name": await ev('(document.querySelector("h1")||{}).innerText||""')}
        out["intro_before"] = await ev(INTRO_JS)
        out["shot_before"] = await shot("before")
        if MODE == "set":
            ok = await click_text("Edit bio") or await click_text("Add bio")
            if not ok:  # new profile layout: top "Edit" -> Edit profile dialog -> Bio row's Edit/Add
                out["clicked_profile_edit"] = await click_text("Edit")
                await asyncio.sleep(4)
                out["shot_dialog"] = await shot("dialog")
                xy = await ev(r'''(() => {
                  const fol = [...document.querySelectorAll('a, span')].find(e => /followers/.test(e.innerText||'') && e.offsetParent);
                  const bios = [...document.querySelectorAll('div[dir=auto]')].filter(e => e.offsetParent && e.children.length === 0 && (e.innerText||'').length > 10);
                  const head = fol && bios.find(e => e.getBoundingClientRect().top > fol.getBoundingClientRect().top);
                  const t = head && bios.filter(e => e.innerText === head.innerText).pop();
                  if (!t) return null; t.scrollIntoView({block:'center'});
                  const r = t.getBoundingClientRect(); const cy = r.top + r.height/2;
                  const c = [...document.querySelectorAll('svg, i')].map(e => [e, e.getBoundingClientRect()])
                    .filter(([e, q]) => q.width > 8 && q.width < 40 && Math.abs(q.top + q.height/2 - cy) < 20 && q.left > r.right);
                  if (!c.length) return null; c.sort((a, b) => b[1].left - a[1].left); const q = c[0][1];
                  return [q.left + q.width/2, q.top + q.height/2]; })()''')
                ok = xy
                if xy:
                    for typ in ("mousePressed", "mouseReleased"):
                        await call("Input.dispatchMouseEvent", {"type": typ, "x": xy[0], "y": xy[1], "button": "left", "clickCount": 1})
                await asyncio.sleep(3)
                out["shot_after_pencil"] = await shot("pencil")
            out["clicked_edit"] = ok
            await asyncio.sleep(2)
            ta = await ev('''(() => { const t = document.querySelector('textarea'); if (!t) return false; t.focus(); t.select(); return true; })()''')
            out["textarea"] = ta
            if ta:
                await call("Input.dispatchKeyEvent", {"type": "keyDown", "key": "a", "code": "KeyA", "modifiers": 4, "windowsVirtualKeyCode": 65})
                await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": "a", "code": "KeyA", "modifiers": 4, "windowsVirtualKeyCode": 65})
                await call("Input.dispatchKeyEvent", {"type": "rawKeyDown", "key": "Backspace", "code": "Backspace", "windowsVirtualKeyCode": 8})
                await call("Input.dispatchKeyEvent", {"type": "keyUp", "key": "Backspace", "code": "Backspace", "windowsVirtualKeyCode": 8})
                await call("Input.insertText", {"text": BIO})
                await asyncio.sleep(1)
                out["typed"] = await ev("document.querySelector('textarea').value")
                out["shot_typed"] = await shot("typed")
                out["clicked_save"] = await click_text("Save")
                await asyncio.sleep(5)
                await call("Page.navigate", {"url": "https://www.facebook.com/me"}); await asyncio.sleep(12)
                out["intro_after"] = await ev(INTRO_JS)
                out["shot_after"] = await shot("after")
        return out


try:
    res = asyncio.run(main())
finally:
    try: sm.api("POST", f"/profiles/{pid}/stop", {})
    except SystemExit: pass
s = json.dumps(res, indent=1, ensure_ascii=False)
print(s)
if OUT: open(OUT, "w").write(s)
