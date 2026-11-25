#!/usr/bin/env python3
"""Profile rival channels: catalog + recent-15 VPH (yt-dlp, free).
Usage: tools/comp_profile.py <outdir> <handle> [<handle> ...]"""
import json, subprocess, sys, time, statistics as s
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
handles = sys.argv[2:]

def fetch(h):
    url = f"https://www.youtube.com/@{h}/videos"
    cat = subprocess.run(["yt-dlp", "--flat-playlist", "-J", url], capture_output=True, text=True).stdout
    rec = subprocess.run(["yt-dlp", "--flat-playlist", "--extractor-args", "youtubetab:approximate_date",
                          "--playlist-items", "1-15", "--print",
                          "%(timestamp)s|%(view_count)s|%(duration)s|%(id)s|%(title)s", url],
                         capture_output=True, text=True).stdout
    return h, cat, rec

with ThreadPoolExecutor(6) as ex:
    res = list(ex.map(fetch, handles))

for h, cat, rec in res:
    d = json.loads(cat)
    (out / f"{h}.json").write_text(cat)
    with open(out / f"{h}_catalog.tsv", "w") as f:
        for x in d["entries"]:
            f.write(f"{x['id']}\t{x.get('view_count')}\t{x.get('duration')}\t{x['title']}\n")
    e = [x for x in d["entries"] if x.get("view_count") and (x.get("duration") or 0) > 180]
    v = [x["view_count"] for x in e]
    print(f"\n#### {h} subs={d.get('channel_follower_count')} videos={len(d['entries'])} long={len(e)} "
          f"median={s.median(v):.0f} medlen={s.median([x['duration'] for x in e])/60:.1f}m")
    print("top8:")
    for x in sorted(e, key=lambda x: -x["view_count"])[:8]:
        print(f"  {x['view_count']:>9} {round(x['duration']/60):3}m {x['id']} {x['title']}")
    print("recent VPH:")
    (out / f"recent_{h}.txt").write_text(rec)
    for l in rec.splitlines():
        t, vv, du, i, ti = l.split("|", 4)
        if "NA" in (t, vv):
            continue
        hr = (time.time() - int(t)) / 3600
        print(f"  {int(vv)/hr:6.0f} {int(vv):>9} {hr/24:4.0f}d {int(float(du))//60:3}m {i} {ti}")
