#!/usr/bin/env python3
"""One human-like Facebook session on the Politics profile ("Facebook", persona = US politics viewer in Los Angeles).
Passive habits only: scroll the home feed, watch a few reels, check notifications, drop into 1-2 political groups,
sometimes look at our own latest reel, sometimes search a political name. Likes are rare and only on posts that
match the channel's side (anti-Trump / pro-Democrat). NO comments, NO shares, NO posts here (those need judgement:
agent runs do them, see docs/FACEBOOK.md).
usage: FB_OWNER=human-session ~/.hermes/hermes-agent/venv/bin/python tools/fb_human_session.py [--dry]
Log: control/facebook/human_log.jsonl (one line per session)."""
import json, os, random, re, subprocess, sys, time, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = str(Path.home() / ".hermes/hermes-agent/venv/bin/python")
CDP = str(ROOT / "tools/shard_fb_cdp.py")
LOG = ROOT / "control/facebook/human_log.jsonl"
DRY = "--dry" in sys.argv
ENV = dict(os.environ, FB_OWNER="human-session")
GROUPS = ["3056231087863798", "203489800225585", "288544190546353", "337354698750575", "1488340045676130",
          "1166106920440331", "EndlessBlueWaves", "1009555754577418"]
SEARCH = ["Jamie Raskin", "Robert Garcia Oversight", "Hakeem Jeffries", "Heather Cox Richardson", "MeidasTouch",
          "Gavin Newsom", "JB Pritzker", "House Oversight Committee", "Jasmine Crockett", "Chris Murphy"]
# the side we like: anti-Trump / pro-Dem wording or sources. Never like if RIGHT matches.
ALLY = re.compile(r"\b(democrat|dems\b|jeffries|raskin|garcia|newsom|pritzker|crockett|aoc|ocasio|sanders|warren|"
                  r"murphy|meidas|heather cox|resist|blue wave|vote blue|impeach|corrupt|felon|dictator|kakistocracy|"
                  r"accountab|oversight|subpoena|insider trading|grift|epstein files)", re.I)
RIGHT = re.compile(r"(trump 2028|maga strong|god bless president trump|thank you president trump|let'?s go brandon|"
                   r"libtard|demonrat|stop the steal|fjb|america first patriots)", re.I)
MOOD = {"like": random.uniform(0.06, 0.22), "dwell": random.uniform(0.7, 1.6), "reels": random.random() < 0.55,
        "groups": random.choice([0, 1, 1, 2]), "notif": random.random() < 0.7, "own": random.random() < 0.35,
        "search": random.random() < 0.25, "len_min": random.uniform(4, 16)}
rec = {"start": datetime.datetime.now().isoformat(timespec="minutes"), "mood": {k: (round(v, 2) if isinstance(v, float) else v) for k, v in MOOD.items()},
       "steps": [], "likes": []}


def t(*a, timeout=90):
    r = subprocess.run([PY, CDP, *a], capture_output=True, text=True, timeout=timeout, cwd=ROOT, env=ENV)
    return "\n".join(l for l in (r.stdout + r.stderr).splitlines() if not l.startswith("health")).strip()


def ev(js):
    o = t("eval", js)
    try:
        return json.loads(o)
    except Exception:
        return o


def nap(a, b):
    time.sleep(random.uniform(a, b) * MOOD["dwell"])


def over():
    return time.time() > T0 + MOOD["len_min"] * 60


def visible_posts():
    """posts in [role=feed] currently on screen: text + Like button centre + already-liked flag"""
    return ev(r'''(()=>{const f=document.querySelector("[role=feed]");if(!f)return [];const o=[];
[...f.children].forEach((c,i)=>{const r=c.getBoundingClientRect();if(r.bottom<80||r.top>820)return;
const b=[...c.querySelectorAll("[role=button][aria-label]")].find(e=>/^Like$|^React with Like/.test(e.getAttribute("aria-label")));
const liked=[...c.querySelectorAll("[aria-label]")].some(e=>/^Remove Like|^Change .* reaction/.test(e.getAttribute("aria-label")));
const br=b&&b.getBoundingClientRect();o.push({i,txt:(c.innerText||"").replace(/\n+/g," ").slice(0,700),
 like:br&&br.top>60&&br.bottom<880?[Math.round(br.x+br.width/2),Math.round(br.y+br.height/2)]:null,liked})});return o})()''') or []


def maybe_like(p, where):
    txt = p.get("txt", "")
    if re.search(r"^Reels|group suggestions|Suggested for you|Sponsored|People you may know|Join group", txt[:200]):
        return   # cards FB inserts, not someone's post
    if not p.get("like") or p.get("liked") or RIGHT.search(txt) or not ALLY.search(txt):
        return
    if re.search(r"[ãõçáéíóú]{2,}|\b(você|não|obrigad)", txt, re.I):   # Portuguese friends' posts: not this persona
        return
    if random.random() > MOOD["like"] or len(rec["likes"]) >= 4:
        return
    nap(1.5, 5)
    if not DRY:
        t("click", *map(str, p["like"]))
    rec["likes"].append({"where": where, "txt": txt[:90]})


def scroll_feed(where, n):
    for _ in range(n):
        if over():
            return
        posts = visible_posts()
        for p in posts if isinstance(posts, list) else []:
            maybe_like(p, where)
        # read longer when the screen is political, skim otherwise
        pol = any(ALLY.search(p.get("txt", "")) for p in posts) if isinstance(posts, list) else False
        nap(4, 14) if pol else nap(1, 4)
        t("wheel", str(random.choice([1, 1, 1, 2]) * random.randint(350, 850)))
        if random.random() < 0.08:
            t("wheel", str(-random.randint(200, 500)))   # scroll back a bit to re-read
            nap(2, 6)


def home():
    t("nav", "https://www.facebook.com/", str(random.uniform(6, 10)))
    rec["steps"].append("home")
    scroll_feed("home", random.randint(6, 22))


def reels():
    t("nav", "https://www.facebook.com/reel/", str(random.uniform(6, 9)))
    rec["steps"].append("reels")
    for _ in range(random.randint(3, 9)):
        if over():
            return
        r = random.random()
        nap(2, 5) if r < 0.35 else nap(8, 20) if r < 0.8 else nap(25, 50)   # skip / watch some / watch it all
        t("wheel", "700", "720", "450")


def notifications():
    t("nav", "https://www.facebook.com/notifications", str(random.uniform(5, 8)))
    rec["steps"].append("notifications")
    nap(4, 12)
    t("wheel", str(random.randint(300, 900)))
    nap(2, 6)


def group(gid):
    t("nav", f"https://www.facebook.com/groups/{gid}/", str(random.uniform(6, 10)))
    rec["steps"].append(f"group:{gid}")
    scroll_feed(f"group:{gid}", random.randint(4, 12))


def own_reel():
    t("nav", "https://www.facebook.com/me/reels/", str(random.uniform(6, 9)))
    rec["steps"].append("own_reels")
    nap(4, 10)


def search():
    q = random.choice(SEARCH)
    t("nav", "https://www.facebook.com/", "6")
    ok = ev('(()=>{const i=document.querySelector("input[type=search],input[placeholder^=\\"Search\\"]");if(!i)return 0;const r=i.getBoundingClientRect();return Math.round(r.x+r.width/2)+" "+Math.round(r.y+r.height/2)})()')
    if isinstance(ok, str) and " " in ok:
        t("click", *ok.split()); nap(0.8, 2)
        t("type", q, timeout=120); nap(0.5, 1.5); t("key", "Enter")
        time.sleep(random.uniform(5, 8))
        rec["steps"].append(f"search:{q}")
        scroll_feed(f"search:{q}", random.randint(2, 6))


def main():
    global T0
    o = t("start", timeout=120)
    if "started" not in o and "already" not in o:
        rec["skipped"] = o[-120:]
        LOG.open("a").write(json.dumps(rec, ensure_ascii=False) + "\n")
        print("skip:", o[-120:]); return
    T0 = time.time()
    try:
        plan = ["home"]
        if MOOD["notif"]: plan.insert(random.randint(0, 1), "notifications")
        if MOOD["reels"]: plan.append("reels")
        plan += ["group"] * MOOD["groups"]
        if MOOD["own"]: plan.append("own")
        if MOOD["search"]: plan.append("search")
        head, rest = plan[:1], plan[1:]
        random.shuffle(rest)
        gs = random.sample(GROUPS, k=min(len(GROUPS), MOOD["groups"]))
        for step in head + rest:
            if over() and step != "home":
                break
            try:
                {"home": home, "reels": reels, "notifications": notifications, "own": own_reel, "search": search,
                 "group": lambda: group(gs.pop())}[step]()
            except Exception as e:
                rec["steps"].append(f"{step}:ERR {str(e)[:80]}")
                t("fresh")
            nap(1, 4)
        # a real visit fills its time: keep drifting between the feed and a group until the visit length is used
        while not over():
            random.choice([home, lambda: group(random.choice(GROUPS))])()
            nap(1, 4)
    finally:
        rec["end"] = datetime.datetime.now().isoformat(timespec="minutes")
        t("stop")
        LOG.open("a").write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(json.dumps(rec, ensure_ascii=False)[:900])


if __name__ == "__main__":
    main()
