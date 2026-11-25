"""Fill the delivery row in owner's real Chrome (signed in) via the CDP relay ws://127.0.0.1:9333 (cdp_relay.py),
falling back to DevToolsActivePort. Own background tab only (tid in sheet_tid.txt); never touches his tabs.
  venv-python sheet_cdp.py open <sheet_id>
  venv-python sheet_cdp.py tabs | tab <name> | goto <A12> | paste <row.tsv> | js <expr> | key <Key> | close
"""
import asyncio, json, os, socket, sys
import websockets

HERE = os.path.dirname(os.path.abspath(__file__))
TF = os.path.join(HERE, "sheet_tid.txt")
PORTF = os.path.expanduser("~/Library/Application Support/Google/Chrome/DevToolsActivePort")


class C:
    def __init__(self, ws):
        self.ws, self.n = ws, 0

    async def call(self, method, sid=None, **params):
        self.n += 1
        i = self.n
        msg = {"id": i, "method": method, "params": params}
        if sid:
            msg["sessionId"] = sid
        await self.ws.send(json.dumps(msg))
        while True:
            r = json.loads(await asyncio.wait_for(self.ws.recv(), 60))
            if r.get("id") == i:
                if "error" in r:
                    raise RuntimeError(r["error"])
                return r.get("result", {})


async def ev(c, sid, expr):
    r = await c.call("Runtime.evaluate", sid, expression=expr, returnByValue=True, awaitPromise=True)
    return r.get("result", {}).get("value")


async def click(c, sid, x, y, n=1):
    for t in ("mousePressed", "mouseReleased"):
        await c.call("Input.dispatchMouseEvent", sid, type=t, x=x, y=y, button="left", clickCount=n)


async def key(c, sid, k, code=None, mods=0, vk=0):
    for t in ("rawKeyDown", "keyUp"):
        await c.call("Input.dispatchKeyEvent", sid, type=t, key=k, code=code or k, modifiers=mods, windowsVirtualKeyCode=vk)


async def center(c, sid, sel_js):
    return await ev(c, sid, f"(()=>{{const e={sel_js};if(!e)return null;const r=e.getBoundingClientRect();return [r.x+r.width/2,r.y+r.height/2];}})()")


async def main():
    url = None
    try:
        socket.create_connection(("127.0.0.1", 9333), 1).close(); url = "ws://127.0.0.1:9333/"
    except OSError:
        port, path = open(PORTF).read().split()[:2]; url = f"ws://127.0.0.1:{port}{path}"
    async with websockets.connect(url, max_size=2**26) as ws:
        c = C(ws)
        cmd = sys.argv[1]
        tid = open(TF).read().strip() if os.path.exists(TF) else None
        ids = [t["targetId"] for t in (await c.call("Target.getTargets"))["targetInfos"]]
        if tid not in ids:
            tid = (await c.call("Target.createTarget", url="about:blank", background=True))["targetId"]
            open(TF, "w").write(tid)
        sid = (await c.call("Target.attachToTarget", targetId=tid, flatten=True))["sessionId"]
        await c.call("Emulation.setFocusEmulationEnabled", sid, enabled=True)
        if cmd == "open":
            await c.call("Page.navigate", sid, url=f"https://docs.google.com/spreadsheets/d/{sys.argv[2]}/edit")
            await asyncio.sleep(10)
            print(await ev(c, sid, "document.title"))
        elif cmd == "tabs":
            print(await ev(c, sid, "[...document.querySelectorAll('.docs-sheet-tab')].map(t=>t.innerText.trim()+(t.classList.contains('docs-sheet-active-tab')?'*':'')).join(' | ')"))
        elif cmd == "tab":
            name = sys.argv[2]
            xy = await center(c, sid, f"[...document.querySelectorAll('.docs-sheet-tab')].find(t=>t.innerText.trim()==={json.dumps(name)})")
            await click(c, sid, *xy); await asyncio.sleep(2)
            print(await ev(c, sid, "(document.querySelector('.docs-sheet-active-tab')||{}).innerText"))
        elif cmd == "goto":
            xy = await center(c, sid, "document.querySelector('#t-name-box')")
            await click(c, sid, *xy); await asyncio.sleep(0.4)
            await key(c, sid, "a", "KeyA", 4, 65)
            await c.call("Input.insertText", sid, text=sys.argv[2])
            await key(c, sid, "Enter", "Enter", 0, 13); await asyncio.sleep(1)
            print(await ev(c, sid, "document.querySelector('#t-name-box').value"))
        elif cmd == "del":
            await key(c, sid, "Delete", "Delete", 0, 46); await asyncio.sleep(1.5); print("deleted")
        elif cmd == "paste":
            tsv = open(sys.argv[2], encoding="utf-8").read().rstrip("\n")
            await ev(c, sid, "(()=>{const dt=new DataTransfer();dt.setData('text/plain',%s);const t=document.querySelector('.cell-input')||document.activeElement;t.dispatchEvent(new ClipboardEvent('paste',{clipboardData:dt,bubbles:true,cancelable:true}));})()" % json.dumps(tsv))
            await asyncio.sleep(3)
            print(await ev(c, sid, "document.querySelector('#t-name-box').value"))
        elif cmd == "js":
            print(await ev(c, sid, sys.argv[2]))
        elif cmd == "key":
            await key(c, sid, sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None, int(sys.argv[4]) if len(sys.argv) > 4 else 0, int(sys.argv[5]) if len(sys.argv) > 5 else 0)
        elif cmd == "clicktext":
            xy = await center(c, sid, f"[...document.querySelectorAll({json.dumps(sys.argv[3])})].find(e=>e.innerText&&e.innerText.trim().startsWith({json.dumps(sys.argv[2])}))")
            print(xy)
            if xy:
                await click(c, sid, *xy)
        elif cmd == "type":
            await c.call("Input.insertText", sid, text=sys.argv[2])
        elif cmd == "close":
            await c.call("Target.closeTarget", targetId=tid); os.remove(TF); print("closed")


asyncio.run(main())
