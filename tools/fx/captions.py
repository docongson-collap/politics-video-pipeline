#!/usr/bin/env python3
"""Burned-in captions for Facebook muted autoplay (plan B, docs/FACEBOOK.md).
Input: JSON list of words with ABSOLUTE film times [{"w","s","e"}...] (narration + verbatim soundbites).
Output: .ass file -> burn with /opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -vf "ass=caps.ass:fontsdir=kho/fonts/Inter".
Style: Inter Black, 2-4 words per card, white with black outline, the word being spoken turns yellow.
Numbers/names listed in --hot are always yellow.
usage: captions.py words_abs.json out.ass [--skip a-b,c-d] [--hot "258,100,000"] [--w 1920 --h 1080]
"""
import argparse, json, re

ap = argparse.ArgumentParser()
ap.add_argument("words"); ap.add_argument("out")
ap.add_argument("--skip", default="", help="time ranges with their own captions (e.g. network subs): 12.0-20.5,40-44")
ap.add_argument("--hot", default="", help="comma list of tokens always yellow")
ap.add_argument("--w", type=int, default=1920); ap.add_argument("--h", type=int, default=1080)
ap.add_argument("--mv", type=float, default=0.27, help="bottom margin as fraction of height (clear lower thirds)")
ap.add_argument("--maxw", type=int, default=4); ap.add_argument("--maxchars", type=int, default=22)
ap.add_argument("--doc", default="", help="film time ranges over page/evidence shots: caption drops to the bottom edge on a "
                "dark box so it never covers the highlighted line (Nvidia v1 QC 2026-11-24): 12.0-15.3,40-44")
ap.add_argument("--docmv", type=float, default=0.035)
a = ap.parse_args()
docs = [tuple(map(float, r.split("-"))) for r in a.doc.split(",") if r]

W = json.load(open(a.words))
skips = [tuple(map(float, r.split("-"))) for r in a.skip.split(",") if r]
hot = {h.strip().lower() for h in a.hot.split(",") if h.strip()}
W = [w for w in W if not any(s0 <= (w["s"] + w["e"]) / 2 < s1 for s0, s1 in skips)]


def ts(t):
    t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def clean(w):
    return w.replace("{", "").replace("}", "").strip()


# group into cards: break on punctuation, pauses > 0.35 s, maxw words or maxchars
cards, cur = [], []
for i, w in enumerate(W):
    cur.append(w)
    txt = " ".join(clean(x["w"]) for x in cur)
    nxt = W[i + 1] if i + 1 < len(W) else None
    brk = (nxt is None or len(cur) >= a.maxw or len(txt) >= a.maxchars or re.search(r"[.,!?;:]$", w["w"])
           or (nxt and nxt["s"] - w["e"] > 0.35))
    if brk:
        cards.append(cur); cur = []

fs = int(a.h * 0.085)  # ~92 px at 1080p
head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {a.w}
PlayResY: {a.h}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter Black,{fs},&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,3,0,1,{max(5, fs // 12)},{max(2, fs // 30)},2,80,80,{int(a.h * a.mv)},1
Style: Doc,Inter Black,{int(fs * 0.8)},&H00FFFFFF,&H00FFFFFF,&H38000000,&H38000000,-1,0,0,0,100,100,2,0,3,{max(10, fs // 6)},0,2,80,80,{int(a.h * a.docmv)},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
YEL, WHT = r"{\c&H00D7FF&}", r"{\c&HFFFFFF&}"
ev = []
for k, c in enumerate(cards):
    end_card = c[-1]["e"] + 0.15
    if k + 1 < len(cards):
        end_card = min(end_card + 0.25, cards[k + 1][0]["s"])
    for j, w in enumerate(c):
        s = w["s"]; e = c[j + 1]["s"] if j + 1 < len(c) else end_card
        parts = []
        for jj, x in enumerate(c):
            t = clean(x["w"]).upper()
            on = jj == j or re.sub(r"[^\w$%,.]", "", t).lower().strip(".,") in hot or re.search(r"\d", t)
            parts.append((YEL if on else WHT) + t)
        pop = r"{\fscx108\fscy108\t(0,90,\fscx100\fscy100)}" if j == 0 else ""
        mid = (c[0]["s"] + c[-1]["e"]) / 2   # whole card keeps one style (no jump mid-card)
        st = "Doc" if any(d0 <= mid < d1 for d0, d1 in docs) else "Cap"
        ev.append(f"Dialogue: 0,{ts(s)},{ts(e)},{st},,0,0,0,,{pop}" + " ".join(parts))
open(a.out, "w").write(head + "\n".join(ev) + "\n")
print(f"{len(cards)} cards, {len(ev)} events -> {a.out}")
