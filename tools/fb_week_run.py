#!/usr/bin/env python3
"""One run of the FB weekly-task plan (cases/<case>/delivery/week/week_plan.json).
Posts 1 story + shares 1 reel into 1 group, reads the weekly task status, logs to control/facebook/week_log.txt.
usage: fb_week_run.py PLAN_JSON RUN_NO        (RUN_NO = 'status' only reads progress)
Never touches the profile if someone has it open (shard_fb_cdp.py start refuses)."""
import json, subprocess, sys, time, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = str(Path.home() / ".hermes/hermes-agent/venv/bin/python")
CDP = str(ROOT / "tools/shard_fb_cdp.py")
LOG = ROOT / "control/facebook/week_log.txt"


def t(*a, timeout=90):
    try:  # a slow nav right after the story upload hit 90s and killed the whole run (2026-11-25): don't crash
        r = subprocess.run([PY, CDP, *a], capture_output=True, text=True, timeout=timeout, cwd=ROOT)
    except subprocess.TimeoutExpired:
        return f"TIMEOUT {a[0]}"
    out = "\n".join(l for l in (r.stdout + r.stderr).splitlines() if not l.startswith("health")).strip()
    return out


def ev(js):
    o = t("eval", js)
    try:
        return json.loads(o)
    except Exception:
        return o


def log(msg):
    line = f"{datetime.datetime.now():%Y-%m-%d %H:%M} {msg}"
    print(line)
    with LOG.open("a") as f:
        f.write(line + "\n")


def click_xy(xy):
    if isinstance(xy, str) and " " in xy:
        x, y = xy.split()
        t("click", x, y)
        return True
    return False


def status():
    t("nav", "https://www.facebook.com/professional_dashboard/status", "12")
    s = ev('(()=>{const m=document.body.innerText.match(/This week.s tasks[\\s\\S]{0,330}/);return m?m[0].replace(/\\n+/g," | "):"?"})()')
    return s


def story(path):
    t("fresh")
    t("nav", "https://www.facebook.com/stories/create", "12")
    o = t("files", "input[type=file]", str(path))
    if "files set" not in o:
        return f"story FAIL upload ({o})"
    time.sleep(8)
    xy = ev('(()=>{const b=[...document.querySelectorAll("[role=button]")].find(e=>(e.getAttribute("aria-label")||e.innerText||"").trim()=="Share to story");if(!b)return "none";const r=b.getBoundingClientRect();return Math.round(r.x+r.width/2)+" "+Math.round(r.y+r.height/2)})()')
    if not click_xy(xy):
        return "story FAIL no share button"
    # do NOT open a fresh tab here: closing this tab mid-upload drops the story
    for _ in range(9):
        time.sleep(10)
        if "create" not in t("eval", "location.href"):
            break
    time.sleep(20)
    t("nav", "https://www.facebook.com/stories/", "10")
    ok = ev('/Your story[\\s\\S]{0,120}· ?(\\d+m|Just now|now)/.test(document.body.innerText.slice(0,600))')
    return "story OK" if ok is True else "story ?? (check stories page)"


def find_reel(caption_start):
    t("nav", "https://www.facebook.com/me/reels/", "12")
    ids = ev('(()=>[...new Set([...document.querySelectorAll("a[href*=\\"/reel/\\"]")].map(a=>(a.href.match(/reel\\/(\\d+)/)||[])[1]).filter(Boolean))].slice(0,10))()')
    for rid in ids if isinstance(ids, list) else []:
        t("nav", f"https://www.facebook.com/reel/{rid}/", "10")
        txt = ev('document.body.innerText.slice(0,4000)')
        if isinstance(txt, str) and caption_start[:30] in txt:
            return rid
    return None


DLG = '[...document.querySelectorAll("[role=dialog]")]'


def share_group(reel, group_name, text):
    t("fresh")
    t("nav", f"https://www.facebook.com/reel/{reel}/", "12")
    # the reel's Share button can sit outside the viewport: click it from JS
    ok = ev('(()=>{const b=[...document.querySelectorAll("[role=button][aria-label]")].find(e=>/^Share(,|$)/.test(e.getAttribute("aria-label"))&&e.getBoundingClientRect().width>0);if(!b)return "none";b.click();return "ok"})()')
    if ok != "ok":
        return "group FAIL no share button"
    time.sleep(4)
    ok = ev('(()=>{const b=%s.flatMap(d=>[...d.querySelectorAll("[role=button],[role=link],[tabindex]")]).find(e=>(e.getAttribute("aria-label")||e.innerText||"").trim()=="Share to a group");if(!b)return "none";b.click();return "ok"})()' % DLG)
    if ok != "ok":
        return "group FAIL no 'Share to a group'"
    time.sleep(4)
    gn = json.dumps(group_name)
    ok = ev('(()=>{const s=%s.flatMap(d=>[...d.querySelectorAll("span")]).filter(e=>e.innerText.trim()==%s).pop();if(!s)return "none";(s.closest("[role=button],[role=listitem],[tabindex]")||s).click();return "ok"})()' % (DLG, gn))
    if ok != "ok":
        return f"group FAIL group not in picker: {group_name}"
    time.sleep(6)
    ok = ev('(()=>{const x=[...document.querySelectorAll("[role=dialog] [role=textbox][contenteditable=true]")].find(e=>/public post|Write something|Create a/i.test(e.getAttribute("aria-label")||""));if(!x)return "none";x.focus();return "ok"})()')
    if ok != "ok":
        return "group FAIL no group composer"
    t("type", text, timeout=300)
    time.sleep(2)
    xy = ev('(()=>{const d=%s.find(d=>[...d.querySelectorAll("[role=textbox]")].some(x=>x.innerText.trim().length>20));if(!d)return "none";const b=[...d.querySelectorAll("[role=button]")].find(e=>(e.getAttribute("aria-label")||e.innerText||"").trim()=="Post");if(!b)return "none";const r=b.getBoundingClientRect();return Math.round(r.x+r.width/2)+" "+Math.round(r.y+r.height/2)})()' % DLG)
    if not click_xy(xy):
        return "group FAIL no Post button"
    time.sleep(10)
    left = ev('[...document.querySelectorAll("[role=textbox]")].some(x=>x.innerText.trim().length>20)')
    return "group OK" if left is not True else "group ?? composer still has text"


def main():
    plan = json.loads(Path(sys.argv[1]).read_text())
    run = sys.argv[2]
    week = Path(sys.argv[1]).parent
    o = t("start", timeout=120)
    if "started" not in o and "already" not in o:
        log(f"run {run}: BLOCKED start: {o[-200:]}")
        sys.exit(2)
    try:
        if run != "status":
            p = [r for r in plan["runs"] if str(r["run"]) == run][0]
            res = [story(week / p["story"])]
            reel = p["reel"] if p["reel"].isdigit() else find_reel(p["reel_caption_start"])
            res.append(share_group(reel, p["group_name"], p["text"]) if reel else f"group SKIP reel {p['reel']} not published yet")
            log(f"run {run}: " + " ; ".join(res) + f" ; reel={reel} group={p['group_name']}")
        log(f"status: {status()}")
    finally:
        t("stop")


if __name__ == "__main__":
    main()
