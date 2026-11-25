#!/usr/bin/env python3
"""Facebook via the ShardBrowser profile "Facebook" (same pattern as Aviation/tools/shard_*.py: local ShardBrowser API
from /Volumes/WORK/Application/shard_migrate.py, profile started HEADLESS with its own proxy, driven over CDP, stopped after).
READ-ONLY for now: login state, account name, managed Pages, proxy IP. Never prints cookies/secrets.
usage: ~/.hermes/hermes-agent/venv/bin/python tools/shard_fb.py check [OUT.json]"""
import asyncio, importlib.util, json, sys, time, urllib.request
import websockets

spec = importlib.util.spec_from_file_location("sm", "/Volumes/WORK/Application/shard_migrate.py")
argv, sys.argv = sys.argv, ["x", "__none__"]
sm = importlib.util.module_from_spec(spec); spec.loader.exec_module(sm)  # type: ignore
sys.argv = argv
NAME = "Facebook"  # owner: Politics manages ONLY this profile. Never touch any other ShardBrowser profile.
OUT = sys.argv[2] if len(sys.argv) > 2 else None

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

        async def go(u, w=10):
            await call("Page.navigate", {"url": u}); await asyncio.sleep(w)

        await call("Emulation.setDeviceMetricsOverride", {"width": 1440, "height": 900, "deviceScaleFactor": 1, "mobile": False})
        out: dict = {"read_at": time.strftime("%Y-%m-%d %H:%M")}
        await go("https://ipinfo.io/json", 6)
        try:
            j = json.loads(await ev("document.body.innerText")); out["ip"] = {k: j.get(k) for k in ("city", "region", "country", "timezone", "org")}
        except Exception as e:
            out["ip"] = f"err {e}"
        await go("https://www.facebook.com/", 12)
        out["url"] = await ev("location.href"); out["title"] = await ev("document.title")
        out["logged_in"] = bool(await ev('!!document.querySelector("[aria-label=\\"Your profile\\"], [aria-label=\\"Account controls and settings\\"], div[role=navigation] a[href*=\\"/me\\"]")')) \
            and "login" not in (out["url"] or "")
        await go("https://www.facebook.com/me", 10)
        out["me_url"] = await ev("location.href")
        out["me_name"] = await ev('(document.querySelector("h1")||{}).innerText||""')
        await go("https://www.facebook.com/pages/?category=your_pages", 12)
        out["pages_text"] = (await ev('document.body.innerText') or "")[:1500]
        return out


try:
    res = asyncio.run(main())
finally:
    try: sm.api("POST", f"/profiles/{pid}/stop", {})
    except SystemExit: pass
s = json.dumps(res, indent=1, ensure_ascii=False)
print(s)
if OUT: open(OUT, "w").write(s)
