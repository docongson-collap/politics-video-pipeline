#!/usr/bin/env python3
"""Read-only: open URLs in ShardBrowser profile "Facebook" (Politics only), save innerText + screenshot per URL.
usage: ~/.hermes/hermes-agent/venv/bin/python tools/shard_fb_peek.py TAG URL [URL ...]
SHOT_AT='Text A|Text B' scrolls to each label (clicks tabs starting 'Top') and screenshots.
Outputs control/facebook/peek_<TAG>_<i>.txt / .png. Optional env SCROLL=n scrolls n screens before reading."""
import asyncio, base64, importlib.util, json, os, sys, time, urllib.request
import websockets

spec = importlib.util.spec_from_file_location("sm", "/Volumes/WORK/Application/shard_migrate.py")
argv, sys.argv = sys.argv, ["x", "__none__"]
sm = importlib.util.module_from_spec(spec); spec.loader.exec_module(sm)  # type: ignore
sys.argv = argv
NAME = "Facebook"  # owner: Politics manages ONLY this profile.
TAG, URLS = sys.argv[1], sys.argv[2:]
SCROLL = int(os.environ.get("SCROLL", "0"))
LOG = "control/facebook"

prof = next(p for p in sm.api("GET", "/profiles") if p.get("name") == NAME)
pid = prof["id"]
if prof.get("running"):
    raise SystemExit("profile is open (someone is using it) - not touching it")
port = sm.api("POST", f"/profiles/{pid}/start", {"headless": True})["cdp"]["port"]
time.sleep(5)


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
            return (await call("Runtime.evaluate", {"expression": e, "returnByValue": True})).get("result", {}).get("value")

        await call("Emulation.setDeviceMetricsOverride", {"width": 1440, "height": 1000, "deviceScaleFactor": 1, "mobile": False})
        for i, u in enumerate(URLS):
            await call("Page.navigate", {"url": u}); await asyncio.sleep(14)
            for _ in range(SCROLL):
                await ev("window.scrollBy(0, 900)"); await asyncio.sleep(2.5)
            shots = []
            for k, sel in enumerate([x for x in os.environ.get("SHOT_AT", "").split("|") if x]):
                await ev(f"(() => {{ const e=[...document.querySelectorAll('span,h2,div[role=tab],div[role=button]')].find(e=>e.innerText&&e.innerText.trim()==={json.dumps(sel)}&&e.offsetParent); if(e){{e.scrollIntoView({{block:'start'}}); if({json.dumps(sel)}.startsWith('Top')||{json.dumps(sel)}==='Women') e.click();}} }})()")
                await asyncio.sleep(3)
                d = (await call("Page.captureScreenshot", {"format": "png"})).get("data")
                if d: open(f"{LOG}/peek_{TAG}_{i}_s{k}.png", "wb").write(base64.b64decode(d))
            txt = await ev("document.body.innerText") or ""
            links = await ev("[...new Set([...document.querySelectorAll('a[href]')].map(a=>a.href).filter(h=>/videos|reel|watch|insights|posts|story_fbid|permalink/.test(h)))].slice(0,80).join('\\n')") or ""
            base = f"{LOG}/peek_{TAG}_{i}"
            open(base + ".txt", "w").write(f"URL {await ev('location.href')}\n\n{txt}\n\n--- LINKS ---\n{links}")
            await ev("window.scrollTo(0,0)")
            d = (await call("Page.captureScreenshot", {"format": "png"})).get("data")
            if d: open(base + ".png", "wb").write(base64.b64decode(d))
            print(base, len(txt))


try:
    asyncio.run(main())
finally:
    try: sm.api("POST", f"/profiles/{pid}/stop", {})
    except SystemExit: pass
