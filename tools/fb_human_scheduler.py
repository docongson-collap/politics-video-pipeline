#!/usr/bin/env python3
"""Random daily rhythm for tools/fb_human_session.py so the Politics Facebook account lives like one person in
Los Angeles (profile proxy = LA), not a cron job. Basis (docs/FACEBOOK.md "Persona & habits"): Pew 2025 - 37% of US
adults open Facebook several times a day; engagement peaks weekday late morning/lunch and early evening.
Each local day: morning 06:30-09:30 (p .6), lunch 11:30-13:30 (p .4), evening 17:30-22:30 (p .9), late 22:30-23:40 (p .15);
~8% of days only one session; at least 2 h between sessions; minutes are random.
usage: ~/.hermes/hermes-agent/venv/bin/python tools/fb_human_scheduler.py
Pause: touch control/facebook/human.pause (e.g. while owner or an agent needs the profile for a long job)."""
import datetime as dt, json, os, random, subprocess, time
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
PY = str(Path.home() / ".hermes/hermes-agent/venv/bin/python")
SESSION = str(ROOT / "tools/fb_human_session.py")
PAUSE = ROOT / "control/facebook/human.pause"
STATE = ROOT / "control/facebook/human_schedule.json"
Z = ZoneInfo("America/Los_Angeles")
WINDOWS = [((6.5, 9.5), .6), ((11.5, 13.5), .4), ((17.5, 22.5), .9), ((22.5, 23.67), .15)]


def plan_day(day):
    rnd = random.Random(f"{day}-{time.time()}")
    slots = [rnd.uniform(*w) for w, p in WINDOWS if rnd.random() < p]
    if not slots:
        slots = [rnd.uniform(18, 22)]
    if rnd.random() < 0.08:
        slots = [rnd.choice(slots)]
    slots.sort()
    keep = []
    for h in slots:
        if not keep or h - keep[-1] >= 2:
            keep.append(h)
    return [dt.datetime.combine(day, dt.time(int(h), int(h % 1 * 60), rnd.randint(0, 59)), Z) for h in keep]


while True:
    now = dt.datetime.now(Z)
    today = plan_day(now.date())
    STATE.write_text(json.dumps({"day": str(now.date()), "tz": "America/Los_Angeles",
                                 "slots": [s.isoformat() for s in today]}, indent=1))
    print(now.isoformat(timespec="minutes"), "slots", [s.strftime("%H:%M") for s in today], flush=True)
    for s in today:
        wait = (s - dt.datetime.now(Z)).total_seconds()
        if wait < 0:
            continue
        time.sleep(wait)
        if PAUSE.exists():
            print(s.strftime("%H:%M"), "paused", flush=True); continue
        r = subprocess.run([PY, SESSION], capture_output=True, text=True, timeout=3600, cwd=ROOT,
                           env=dict(os.environ, FB_OWNER="human-session"))
        print(s.strftime("%H:%M"), "exit", r.returncode, (r.stdout or "")[-300:], (r.stderr or "")[-200:], flush=True)
    tomorrow = dt.datetime.combine(now.date() + dt.timedelta(days=1), dt.time(0, 3), Z)
    time.sleep(max(60, (tomorrow - dt.datetime.now(Z)).total_seconds()))
