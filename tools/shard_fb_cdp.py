#!/usr/bin/env python3
"""Step-by-step CDP driver for the ShardBrowser profile "Facebook" (Politics only; same API as tools/shard_fb.py).
The profile stays up between steps so a human-paced flow (composer, upload, post) can be driven and checked by eye.

usage (~/.hermes/hermes-agent/venv/bin/python tools/shard_fb_cdp.py ...):
  start                 start headless (refuses if it is already running and we did not start it)
  stop                  stop it (only if we started it)
  nav URL [WAIT]        navigate the working tab
  eval JS               Runtime.evaluate, prints the value (wrap bodies as (()=>{...})())
  shot OUT.png          screenshot of the working tab
  click X Y             mouse click at viewport coords
  type TEXT             Input.insertText into the focused element (use \\n for newlines -> Shift+Enter)
  files CSS PATH...     DOM.setFileInputFiles on the first element matching CSS
  key NAME              press a key (Enter, Escape, Tab)
  paste TEXT            insert the whole text at once (long captions = pasted from notes)
  wheel DY [X Y]        trusted mouse-wheel scroll (human; prefer over window.scrollBy)
Human-like by default (owner 24/11: run the account like a person, not a bot): click moves the mouse along a short
path with jitter; type sends characters one by one at a human speed with small pauses.
State file: control/facebook/cdp_state.json {pid, port, target}. Never prints cookies/secrets."""
import asyncio, base64, importlib.util, json, random, sys, time, urllib.request
from pathlib import Path
import websockets

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "control/facebook/cdp_state.json"
spec = importlib.util.spec_from_file_location("sm", "/Volumes/WORK/Application/shard_migrate.py")
argv, sys.argv = sys.argv, ["x", "__none__"]
sm = importlib.util.module_from_spec(spec); spec.loader.exec_module(sm)  # type: ignore
sys.argv = argv
NAME = "Facebook"  # owner: Politics manages ONLY this profile. Never touch any other ShardBrowser profile.


def prof():
    return next(p for p in sm.api("GET", "/profiles") if p.get("name") == NAME)


OWNER = __import__("os").environ.get("FB_OWNER", "agent")   # who drives the session: agent | human-session | week-run


def start():
    p = prof()
    if p.get("running"):
        if STATE.exists() and json.loads(STATE.read_text()).get("pid") == p["id"]:
            o = json.loads(STATE.read_text()).get("owner", "agent")
            if o != OWNER:
                raise SystemExit(f"busy: our own '{o}' session is driving the profile - wait and retry later")
            print("already started by us"); return
        raise SystemExit("profile is open (someone is using it) - not touching it")
    port = sm.api("POST", f"/profiles/{p['id']}/start", {"headless": True})["cdp"]["port"]
    time.sleep(5)
    t = json.load(urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{port}/json/new?about:blank", method="PUT")))
    STATE.write_text(json.dumps({"owner": OWNER, "pid": p["id"], "port": port, "target": t["id"], "ws": t["webSocketDebuggerUrl"]}))
    print("started, port", port)


def stop():
    if not STATE.exists():
        raise SystemExit("not started by us")
    st = json.loads(STATE.read_text())
    if st.get("owner", "agent") != OWNER:
        raise SystemExit(f"not ours: '{st.get('owner')}' session is running")
    try:
        sm.api("POST", f"/profiles/{st['pid']}/stop", {})
    except SystemExit:
        pass
    STATE.unlink(); print("stopped")


async def run(cmd, args):
    st = json.loads(STATE.read_text())
    async with websockets.connect(st["ws"], max_size=None) as ws:
        n = 0

        async def call(m, p=None):
            nonlocal n; n += 1; await ws.send(json.dumps({"id": n, "method": m, "params": p or {}}))
            while True:
                x = json.loads(await ws.recv())
                if x.get("id") == n:
                    if "error" in x: raise SystemExit(f"{m}: {x['error']}")
                    return x.get("result", {})

        await call("Emulation.setDeviceMetricsOverride", {"width": 1440, "height": 900, "deviceScaleFactor": 1, "mobile": False})
        if cmd == "nav":
            await call("Page.enable"); await call("Page.navigate", {"url": args[0]})
            await asyncio.sleep(float(args[1]) if len(args) > 1 else 10)
            print((await call("Runtime.evaluate", {"expression": "location.href", "returnByValue": True}))["result"].get("value"))
        elif cmd == "eval":
            r = await call("Runtime.evaluate", {"expression": args[0], "returnByValue": True, "awaitPromise": True})
            print(json.dumps(r.get("result", {}).get("value"), ensure_ascii=False))
        elif cmd == "shot":
            r = await call("Page.captureScreenshot", {"format": "png"})
            Path(args[0]).write_bytes(base64.b64decode(r["data"])); print(args[0])
        elif cmd == "click":
            x, y = float(args[0]) + random.uniform(-3, 3), float(args[1]) + random.uniform(-2, 2)
            lx, ly = st.get("mx", x + random.uniform(-200, 200)), st.get("my", y + random.uniform(-150, 150))
            steps = random.randint(6, 14)
            for i in range(1, steps + 1):
                f = i / steps
                await call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": lx + (x - lx) * f + random.uniform(-2, 2),
                                                        "y": ly + (y - ly) * f + random.uniform(-2, 2)})
                await asyncio.sleep(random.uniform(0.01, 0.04))
            await asyncio.sleep(random.uniform(0.08, 0.3))
            for t in ("mousePressed", "mouseReleased"):
                await call("Input.dispatchMouseEvent", {"type": t, "x": x, "y": y, "button": "left", "clickCount": 1})
                await asyncio.sleep(random.uniform(0.05, 0.14))
            st["mx"], st["my"] = x, y; STATE.write_text(json.dumps(st))
            print("clicked", round(x), round(y))
        elif cmd == "wheel":
            dy = float(args[0]); x = float(args[1]) if len(args) > 1 else random.uniform(500, 900)
            y = float(args[2]) if len(args) > 2 else random.uniform(350, 650)
            left = dy
            while abs(left) > 1:
                d = (1 if left > 0 else -1) * min(abs(left), random.uniform(80, 130))
                await call("Input.dispatchMouseEvent", {"type": "mouseWheel", "x": x, "y": y, "deltaX": 0, "deltaY": d})
                left -= d; await asyncio.sleep(random.uniform(0.02, 0.07))
            print("wheel", dy)
        elif cmd == "paste":   # long captions: a real creator pastes them from notes
            await call("Input.insertText", {"text": args[0].replace("\\n", "\n")}); print("pasted", len(args[0]))
        elif cmd == "type":
            parts = args[0].split("\\n")
            for i, part in enumerate(parts):
                for ch in part:
                    await call("Input.insertText", {"text": ch})
                    d = random.uniform(0.045, 0.19)
                    if ch in " ,." and random.random() < 0.12: d += random.uniform(0.3, 1.2)   # thinking pause
                    await asyncio.sleep(d)
                if i < len(parts) - 1:
                    for t in ("keyDown", "keyUp"):
                        await call("Input.dispatchKeyEvent", {"type": t, "key": "Enter", "code": "Enter",
                                                              "windowsVirtualKeyCode": 13, "modifiers": 8})
                await asyncio.sleep(0.05)
            print("typed", len(args[0]))
        elif cmd == "files":
            doc = await call("DOM.getDocument", {"depth": -1, "pierce": True})
            q = await call("DOM.querySelectorAll", {"nodeId": doc["root"]["nodeId"], "selector": args[0]})
            ids = q.get("nodeIds", [])
            if not ids: raise SystemExit("no element for " + args[0])
            await call("DOM.setFileInputFiles", {"nodeId": ids[-1], "files": args[1:]})
            print("files set on", len(ids), "match(es), used last")
        elif cmd == "key":
            k = args[0]; code = {"Enter": 13, "Escape": 27, "Tab": 9}[k]
            for t in ("keyDown", "keyUp"):
                await call("Input.dispatchKeyEvent", {"type": t, "key": k, "code": k, "windowsVirtualKeyCode": code})
            print("key", k)


def fresh():
    """Open a new working tab and close the old one. Use when the old tab hangs (headless FB tabs freeze after
    leaving a composer that held an upload; Page.navigate/evaluate then never return)."""
    st = json.loads(STATE.read_text())
    old = st["target"]
    t = json.load(urllib.request.urlopen(urllib.request.Request(
        f"http://127.0.0.1:{st['port']}/json/new?about:blank", method="PUT"), timeout=10))
    st["target"], st["ws"] = t["id"], t["webSocketDebuggerUrl"]
    STATE.write_text(json.dumps(st))
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{st['port']}/json/close/{old}", timeout=10)
    except Exception:
        pass
    print("fresh tab", t["id"][:8])


if __name__ == "__main__":
    c, a = sys.argv[1], sys.argv[2:]
    if c == "start": start()
    elif c == "stop": stop()
    elif c == "fresh": fresh()
    else: asyncio.run(run(c, a))
