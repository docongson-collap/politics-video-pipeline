"""Resumable vidIQ search scan. Run inside browser_exec:
    exec(open('/Volumes/WORK/Auto Film Factory/Politics/tools/vidiq_search_batch.py').read())
    run(queries, out_dir, max_runs=8)   # call again until it prints ALL DONE
Each (query, mode) is saved as its own JSON in out_dir/raw/; finished runs are skipped, so a timeout loses nothing.
Lesson 2026-10-17: scout pasted '&sp=...' into the query text (garbage results) and ran 42 searches in one 300 s call.
"""
import json, os, re, sys, time
sys.path.insert(0, "/Volumes/WORK/Auto Film Factory/Politics/tools")
import vidiq_scan as _vs
_vs.cdp = cdp  # noqa: F821  (provided by browser_exec)

MODES = [("default", ""), ("this_month", "EgIIBA%3D%3D")]


def _slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def run(queries, out_dir, max_runs=8, wait=6):
    raw = os.path.join(out_dir, "raw"); os.makedirs(raw, exist_ok=True)
    done = 0
    for q in queries:
        for mode, sp in MODES:
            p = os.path.join(raw, f"search_{_slug(q)}_{mode}.json")
            if os.path.exists(p):
                continue
            if done >= max_runs:
                left = sum(not os.path.exists(os.path.join(raw, f"search_{_slug(x)}_{m}.json")) for x in queries for m, _ in MODES)
                print(f"PAUSED, {left} runs left: call run() again"); return
            rows = _vs.scan(None, q, wait=wait, sp=sp)
            for r in rows:
                r.update(query=q, mode=mode, read_at=time.strftime("%Y-%m-%d %H:%M"))
            json.dump(rows, open(p, "w"), indent=1)
            top = max((r["vph_n"] for r in rows), default=0)
            print(f"{q!r} [{mode}] {len(rows)} rows, top VPH {top:.0f}")
            done += 1
    print("ALL DONE")
