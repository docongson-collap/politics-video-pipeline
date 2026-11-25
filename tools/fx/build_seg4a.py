#!/usr/bin/env python3
"""Driver for WO trump-oversight-order-gfx4a. Builds the 8 shotmap_v4 rows of DOC/HLGT/KSTAT/QUOTELIFT/WEBHEAD
using tools/fx/pil_pagepush.py (pure PIL/numpy/ffmpeg, h264_videotoolbox). Times are read straight from
words.json (abs beat-relative) converted to clip-relative by subtracting the row t0, matching shotmap_v4.tsv.
"""
import sys
sys.path.insert(0, "/Volumes/WORK/Auto Film Factory/Politics/tools/fx")
import pil_pagepush as R

CASE = R.CASE

rows = []

# ---------------------------------------------------------------- 1) KSTAT  B1 4.54-8.38  (gma.png)
rows.append(dict(
    name="B1_454", beat="B1", t0=4.54, t1=8.38, png="gma.png", dpr=2,
    marks=[dict(rect=[149, 3314, 677.953125, 3338], a=1.39, b=2.35, mode="multiply")],
    shots=[
        {"t": 0.0, "cx": 720, "cy": 260, "w": 1440},
        {"t": 1.1, "cx": 413.5, "cy": 3326, "w": 620},
        {"t": 3.84, "cx": 413.5, "cy": 3326, "w": 605},
    ],
    extra=dict(kind="kstat_lift", t0=1.78, dur=0.8, box_css=[300.0, 3311.0, 361.5, 3341.0]),
    frames={"a": 0.3, "b": 2.0, "c": 3.6},
    template="KSTAT", phrase="100,000 lifted from GMA page",
))

# ---------------------------------------------------------------- 2) DOC part 1  B4 1.80-10.92 (wh_eo.png)
rows.append(dict(
    name="B4_180", beat="B4", t0=1.80, t1=10.92, png="wh_eo.png", dpr=2,
    marks=[
        dict(rect=[732.046875, 495.734375, 859.03125, 513.734375], a=0.60, b=1.60, mode="invert"),
        dict(rect=[374.21875, 252.34375, 1065.78125, 330.34375], a=3.82, b=5.15, mode="invert"),
        dict(rect=[397.4375, 317.140625, 1042.5625, 395.140625], a=5.15, b=6.70, mode="invert"),
        dict(rect=[267.015625, 381.9375, 1172.96875, 459.9375], a=6.70, b=8.01, mode="invert"),
    ],
    shots=[
        {"t": 0.0, "cx": 720, "cy": 300, "w": 1440},
        {"t": 2.0, "cx": 720, "cy": 300, "w": 1440},
        {"t": 3.7, "cx": 720, "cy": 356, "w": 950},
        {"t": 9.12, "cx": 720, "cy": 356, "w": 928},
    ],
    frames={"a": 0.3, "b": 4.5, "c": 8.9},
    template="DOC", phrase="EO 14438 title block + dateline",
))

# ---------------------------------------------------------------- 3) DOC part 2  B4 10.92-19.68 (wh_eo.png)
rows.append(dict(
    name="B4_1092", beat="B4", t0=10.92, t1=19.68, png="wh_eo.png", dpr=2,
    marks=[
        dict(rect=[359.140625, 2265.40625, 1012.1875, 2288.40625], a=3.70, b=5.42, mode="multiply"),
        dict(rect=[329, 2294.328125, 516.140625, 2317.328125], a=5.42, b=7.08, mode="multiply"),
    ],
    shots=[
        {"t": 0.0, "cx": 720, "cy": 356, "w": 930},
        {"t": 0.37, "cx": 519.28, "cy": 2160.14, "w": 930},
        {"t": 3.5, "cx": 670.6, "cy": 2291.37, "w": 750},
        {"t": 8.76, "cx": 670.6, "cy": 2291.37, "w": 733},
    ],
    frames={"a": 0.25, "b": 4.2, "c": 8.4},
    template="DOC", phrase="Sec.2 notify requirement",
))

# ---------------------------------------------------------------- 4) WEBHEAD  B5 11.84-15.68 (ap_eo.png)
rows.append(dict(
    name="B5_1184", beat="B5", t0=11.84, t1=15.68, png="ap_eo.png", dpr=2,
    marks=[
        dict(rect=[766.421875, 3963.890625, 871.75, 3989.890625], a=1.62, b=2.20, mode="multiply"),
        dict(rect=[170, 3991.78125, 433.53125, 4017.78125], a=2.20, b=2.89, mode="multiply"),
    ],
    shots=[
        {"t": 0.0, "cx": 497, "cy": 433.5, "w": 950},
        {"t": 0.3, "cx": 497, "cy": 433.5, "w": 950},
        {"t": 1.36, "cx": 520.9, "cy": 3990.8, "w": 950, "lin": True},
        {"t": 3.84, "cx": 520.9, "cy": 3990.8, "w": 930},
    ],
    frames={"a": 0.3, "b": 1.5, "c": 3.5},
    template="WEBHEAD", phrase="AP headline -> tens of thousands of businesses",
))

# ---------------------------------------------------------------- 5) DOC part 3  B5 19.44-22.64 (wh_eo.png)
rows.append(dict(
    name="B5_1944", beat="B5", t0=19.44, t1=22.64, png="wh_eo.png", dpr=2,
    marks=[
        dict(rect=[514.65625, 2964.921875, 1043.734375, 2987.921875], a=1.06, b=1.75, mode="multiply"),
        dict(rect=[329, 2993.84375, 619.125, 3016.84375], a=1.75, b=2.67, mode="multiply"),
    ],
    shots=[
        {"t": 0.0, "cx": 670.6, "cy": 2291.37, "w": 733},
        {"t": 0.9, "cx": 686.4, "cy": 2990.88, "w": 780},
        {"t": 3.2, "cx": 686.4, "cy": 2990.88, "w": 765},
    ],
    frames={"a": 0.2, "b": 1.4, "c": 3.0},
    template="DOC", phrase="Sec.4 fails to comply",
))

# ---------------------------------------------------------------- 6) DOC part 4  B5 22.64-27.48 (wh_eo.png)
rows.append(dict(
    name="B5_2264", beat="B5", t0=22.64, t1=27.48, png="wh_eo.png", dpr=2,
    marks=[
        dict(rect=[464.140625, 3051.6875, 908.6875, 3074.6875], a=0.77, b=1.50, mode="multiply"),
        dict(rect=[948.3125, 3051.6875, 1056.21875, 3074.6875], a=2.14, b=2.55, mode="multiply"),
        dict(rect=[329, 3080.609375, 667.140625, 3103.609375], a=2.55, b=3.86, mode="multiply"),
    ],
    shots=[
        {"t": 0.0, "cx": 686.4, "cy": 2990.88, "w": 765},
        {"t": 0.5, "cx": 692.6, "cy": 3077.65, "w": 800},
        {"t": 4.84, "cx": 692.6, "cy": 3077.65, "w": 783},
    ],
    frames={"a": 0.2, "b": 2.0, "c": 4.5},
    template="DOC", phrase="termination/debarment on the menu",
))

# ---------------------------------------------------------------- 7) QUOTELIFT  B10 17.54-20.40 (abc.png)
rows.append(dict(
    name="B10_1754", beat="B10", t0=17.54, t1=20.40, png="abc.png", dpr=2,
    marks=[dict(rect=[227.375, 2178.5625, 571.25, 2200.5625], a=0.34, b=1.04, mode="multiply")],
    shots=[
        {"t": 0.0, "cx": 467.4, "cy": 73.5, "w": 1000},
        {"t": 0.2, "cx": 467.4, "cy": 73.5, "w": 1000},
        {"t": 1.0, "cx": 399.1, "cy": 2189.6, "w": 500},
        {"t": 2.86, "cx": 399.1, "cy": 2189.6, "w": 490},
    ],
    extra=dict(kind="quote_lift", t0=1.04, dur=1.6, rect_css=[227.375, 2178.5625, 571.25, 2200.5625]),
    frames={"a": 0.15, "b": 1.1, "c": 2.6},
    template="QUOTELIFT", phrase="may cross the line into blatant criminality",
))

# ---------------------------------------------------------------- 8) HLGT  B14 24.86-29.01 (nixon_cc.png)
rows.append(dict(
    name="B14_2486", beat="B14", t0=24.86, t1=29.01, png="nixon_cc.png", dpr=2,
    marks=[
        dict(rect=[1094.984375, 1183, 1120.671875, 1209], a=0.50, b=0.62, mode="multiply"),
        dict(rect=[344, 1213, 1143.21875, 1239], a=0.62, b=2.94, mode="multiply"),
    ],
    shots=[
        {"t": 0.0, "cx": 282, "cy": 368.5, "w": 900},
        {"t": 0.35, "cx": 743.5, "cy": 1211, "w": 950},
        {"t": 4.15, "cx": 743.5, "cy": 1211, "w": 930},
    ],
    frames={"a": 0.25, "b": 1.6, "c": 3.8},
    template="HLGT", phrase="Nixon: no absolute privilege",
))

if __name__ == "__main__":
    import json
    idx_path = CASE / "edit/seg4/index_A.tsv"
    idx_lines = ["seg\tt0\tt1\tfile\ttemplate\tphrase"]
    only = sys.argv[1:] if len(sys.argv) > 1 else None
    for r in rows:
        if only and r["name"] not in only:
            continue
        print("=== building", r["name"], "===")
        R.render(r, frames_only=r.pop("frames"))
        rel = f"edit/seg4/{r['name']}.mp4"
        idx_lines.append(f"{r['beat']}\t{r['t0']}\t{r['t1']}\t{rel}\t{r['template']}\t{r['phrase']}")
    if not only or len(only) == len(rows):
        idx_path.write_text("\n".join(idx_lines) + "\n")
        print("wrote", idx_path)
