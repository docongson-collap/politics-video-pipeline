#!/usr/bin/env python3
"""Browse a FB group feed like a person (Politics profile, already started).
  fb_group_act.py list GID [scrolls]      -> tag feed posts data-hx=N, print N|author|reacts|text|img alt
  fb_group_act.py like N [Love|Like|Angry|Haha|Sad|Care|Wow]
  fb_group_act.py comment N "text"        -> opens the post, types, Enter, verifies
  fb_group_act.py read N                  -> full text + top comments
Acts on the tab as left by `list` (no navigation in like/comment)."""
import json, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = str(Path.home() / ".hermes/hermes-agent/venv/bin/python")
CDP = str(ROOT / "tools/shard_fb_cdp.py")


def t(*a, timeout=90):
    r = subprocess.run([PY, CDP, *a], capture_output=True, text=True, timeout=timeout, cwd=ROOT)
    return "\n".join(l for l in (r.stdout + r.stderr).splitlines() if not l.startswith("health")).strip()


def ev(js):
    o = t("eval", js)
    try:
        return json.loads(o)
    except Exception:
        return o


def xy_click(sel_js):
    xy = ev(sel_js)
    if isinstance(xy, str) and " " in xy and xy[0].isdigit():
        t("click", *xy.split())
        return True
    print("not found:", xy)
    return False


POST = 'document.querySelector("[data-hx=\\"%s\\"]")'


LIST_JS = r"""(()=>{const f=document.querySelector("[role=feed]");if(!f)return [];window.__hx=window.__hx||0;const o=[];
[...f.children].forEach(c=>{const tx=c.innerText||"";if(tx.length<30||c.getAttribute("data-hx"))return;
const labs=[...c.querySelectorAll("[aria-label]")].map(e=>e.getAttribute("aria-label"));
const au=(labs.find(l=>/^React with Like to /.test(l))||"").replace(/^React with Like to |'s post$/g,"");if(!au)return;
const n=++window.__hx;c.setAttribute("data-hx",n);
const me=labs.some(l=>/^Remove Like|^Change .* reaction/.test(l));
let msg=[...c.querySelectorAll("[data-ad-preview=message],[data-ad-comet-preview=message]")].map(e=>e.innerText).join(" ");
if(!msg){const ds=[...c.querySelectorAll("div[dir=auto]")].map(e=>e.innerText).filter(x=>x.length>15);msg=ds.slice(0,3).join(" / ")}
const alt=[...c.querySelectorAll("img")].filter(i=>i.width>200).map(i=>i.alt).join(" / ");
const cm=(labs.find(l=>/^Comment on .*comments?$/.test(l))||"").replace(/^.*, /,"");
o.push(n+" | "+au+" | "+cm+(me?" | LIKED":"")+" | "+msg.replace(/\n+/g," ").slice(0,300)+" | IMG: "+alt.slice(0,160))});return o})()"""


def cmd_list(gid, scrolls=5):
    t("nav", f"https://www.facebook.com/groups/{gid}/?sorting_setting=CHRONOLOGICAL", "14")
    time.sleep(4)
    for _ in range(int(scrolls)):
        rows = ev(LIST_JS)
        for r in rows if isinstance(rows, list) else []:
            print(r)
        ev('window.scrollBy(0,1600)')
        time.sleep(2.5)


def show(n):
    for _ in range(4):
        ev('(()=>{const c=%s;if(c)c.scrollIntoView({block:"center"});return 1})()' % (POST % n))
        time.sleep(2.5)
        if (ev('(()=>{const c=%s;return c?c.innerText.length:-1})()' % (POST % n)) or 0) > 30:
            return True
    print("post", n, "not rendered"); return False


def cmd_read(n):
    show(n)
    print(ev(r'(()=>{const c=%s;return c?c.innerText.replace(/\n+/g," | ").slice(0,1800):"none"})()' % (POST % n)))


def cmd_like(n, kind="Like"):
    # scroll the post into view, then click its Like button (long-hover for other reactions)
    if not show(n):
        return
    sel = '(()=>{const c=%s;const b=[...c.querySelectorAll("[role=button][aria-label]")].find(e=>/^Like$|^React with Like/.test(e.getAttribute("aria-label")));if(!b)return "nobtn";const r=b.getBoundingClientRect();return Math.round(r.x+r.width/2)+" "+Math.round(r.y+r.height/2)})()' % (POST % n)
    if kind == "Like":
        if not xy_click(sel):
            return
    else:
        xy = ev(sel)
        if not (isinstance(xy, str) and xy[0].isdigit()):
            print("nobtn"); return
        ev('(()=>{const c=%s;const b=[...c.querySelectorAll("[role=button][aria-label]")].find(e=>/^Like$|^React with Like/.test(e.getAttribute("aria-label")));["pointerover","mouseover","mouseenter"].forEach(k=>b.dispatchEvent(new MouseEvent(k,{bubbles:true})));return 1})()' % (POST % n))
        x, y = xy.split()
        t("cdp_hover", x, y) if False else None
        time.sleep(2.5)
        ok = xy_click('(()=>{const b=document.querySelector("[aria-label=\\"%s\\"][role=button]");if(!b)return "noreact";const r=b.getBoundingClientRect();return Math.round(r.x+r.width/2)+" "+Math.round(r.y+r.height/2)})()' % kind)
        if not ok:
            print("fallback Like"); xy_click(sel)
    time.sleep(2)
    print(ev('(()=>{const c=%s;return [...c.querySelectorAll("[aria-label]")].map(e=>e.getAttribute("aria-label")).filter(l=>/^(Remove|Change) .*reaction|^Remove Like/.test(l)).slice(0,2)})()' % (POST % n)))


def cmd_comment(n, text):
    if not show(n):
        return
    ok = ev('(()=>{const c=%s;const x=c.querySelector("[role=textbox][contenteditable=true][aria-label^=\\"Comment as\\"]");if(!x){const b=[...c.querySelectorAll("[role=button][aria-label]")].find(e=>/^Comment on /.test(e.getAttribute("aria-label")));if(b)b.click();return "dialog"}x.scrollIntoView({block:"center"});x.focus();x.click();return "inline"})()' % (POST % n))
    time.sleep(4)
    if ok == "dialog":
        ok = ev('(()=>{const d=[...document.querySelectorAll("[role=dialog]")].pop();const x=d&&d.querySelector("[role=textbox][contenteditable=true]");if(!x)return "nobox";x.focus();return "ok"})()')
        if ok != "ok":
            print("no box", ok); return
    ev('(()=>{const x=document.activeElement;if(x&&x.isContentEditable){document.execCommand("selectAll");document.execCommand("delete")}return 1})()')
    t("type", text, timeout=300)
    time.sleep(1.5)
    t("key", "Enter")
    time.sleep(7)
    k = json.dumps(text[:40])
    done = ev('[...document.querySelectorAll("[role=article]")].some(a=>/^Comment by Brian/.test(a.getAttribute("aria-label")||"")&&a.innerText.includes(%s))' % k)
    print("posted" if done is True else "UNVERIFIED")
    if ok != "inline":
        t("key", "Escape")  # close post dialog (not a composer)
        time.sleep(2)


if __name__ == "__main__":
    c, *a = sys.argv[1:]
    {"list": cmd_list, "read": cmd_read, "like": cmd_like, "comment": cmd_comment}[c](*a)
