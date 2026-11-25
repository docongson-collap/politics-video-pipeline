#!/usr/bin/env python3
"""Summarise docs/research/comp/*_recent.tsv: views/day, cadence, subs (yt-dlp public counts, NOT vidIQ VPH)."""
import glob, os, statistics as st
from datetime import date
TODAY = date(2026, 10, 17)
for p in sorted(glob.glob(os.path.join(os.path.dirname(__file__), "../docs/research/comp/*_recent.tsv"))):
    rows = [l.rstrip("\n").split("\t") for l in open(p) if l.strip()]
    out = []
    for vid, up, views, dur, subs, title in rows:
        try:
            d = date(int(up[:4]), int(up[4:6]), int(up[6:8]))
        except ValueError:
            continue
        age = max((TODAY - d).days, 1)
        out.append((vid, d, age, int(views or 0), float(dur or 0), subs, title))
    if not out:
        continue
    vpd = [v / a for _, _, a, v, _, _, _ in out]
    span = (out[0][1] - out[-1][1]).days or 1
    print(f"\n== {os.path.basename(p).replace('_recent.tsv','')}  subs={out[0][5]}  "
          f"{len(out)} uploads in {span} d (1 per {span/len(out):.1f} d)  "
          f"median views={st.median(o[3] for o in out):,.0f}  median views/day={st.median(vpd):,.0f}  "
          f"median dur={st.median(o[4] for o in out)/60:.1f} min")
    for (vid, d, age, v, dur, _, t), r in zip(out, vpd):
        print(f"  {d} {age:>4}d {v:>9,} {r:>8,.0f}/d {dur/60:5.1f}m {t[:70]}")
