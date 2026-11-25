#!/usr/bin/env python3
"""Scene-level scan (owner 06/11: soi từng scene, không soi từng frame).
1) ffmpeg scene-cut detection per master (320px decode, threshold 0.3) -> scenes [t0,t1].
2) Drop scenes < MIN_LEN s; one mid-frame per scene -> assets/scenes/<id>/sNNN.jpg.
3) Haiku (tools/ocr_haiku.py) once per scene -> research/scenes/<id>.json  {scenes:[{t0,t1,dur,frame,scene,text,watermark,...}]}
usage: python3 v1/scan_scenes.py detect   # step 1-2 for all masters, prints scene counts (no model calls)
       python3 v1/scan_scenes.py ocr      # step 3 (resumable)"""
import json, re, subprocess, sys
from pathlib import Path

PROJ = Path(__file__).resolve().parent.parent
SRC, IMG, OUT = PROJ / "assets/src", PROJ / "assets/scenes", PROJ / "research/scenes"
PY = str(Path.home() / ".hermes/hermes-agent/venv/bin/python")
MIN_LEN, THR = 1.2, 0.3


def dur(f):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                                capture_output=True, text=True).stdout.strip() or 0)


def cuts(f):
    r = subprocess.run(["ffmpeg", "-nostdin", "-v", "info", "-i", str(f), "-an", "-vf",
                        f"scale=320:-2,select='gt(scene,{THR})',showinfo", "-f", "null", "-"],
                       capture_output=True, text=True)
    return [float(m) for m in re.findall(r"pts_time:([\d.]+)", r.stderr)]


def detect():
    OUT.mkdir(parents=True, exist_ok=True)
    total = 0
    for f in sorted(SRC.glob("*.mp4")):
        idx = OUT / f"{f.stem}.scenes.json"
        if idx.exists():
            sc = json.loads(idx.read_text())
        else:
            d = dur(f)
            b = [0.0] + [c for c in cuts(f) if 0.5 < c < d - 0.5] + [d]
            sc = []
            for t0, t1 in zip(b, b[1:]):
                if t1 - t0 < MIN_LEN:
                    continue
                (IMG / f.stem).mkdir(parents=True, exist_ok=True)
                fr = IMG / f.stem / f"s{len(sc):03d}.jpg"
                subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{(t0 + t1) / 2:.2f}", "-i", str(f),
                                "-frames:v", "1", "-vf", "scale=640:-2", "-q:v", "4", str(fr)])
                sc.append({"t0": round(t0, 2), "t1": round(t1, 2), "dur": round(t1 - t0, 2), "frame": str(fr.relative_to(PROJ))})
            idx.write_text(json.dumps(sc, indent=1))
        total += len(sc)
        print(f"{f.stem}\t{len(sc)} scenes", flush=True)
    print("TOTAL scenes", total)


def split(maxlen=30.0):
    """Continuous spotter takes come out as one huge 'scene'; cut any scene > maxlen into maxlen pieces (own frame)."""
    for idx in sorted(OUT.glob("*.scenes.json")):
        sc, new, f = json.loads(idx.read_text()), [], SRC / idx.name.replace(".scenes.json", ".mp4")
        if all(s["dur"] <= maxlen for s in sc):
            continue
        for s in sc:
            n = max(1, round(s["dur"] / maxlen))
            step = s["dur"] / n
            for k in range(n):
                t0 = s["t0"] + k * step
                fr = IMG / f.stem / f"s{len(new):03d}.jpg"
                subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-ss", f"{t0 + step / 2:.2f}", "-i", str(f),
                                "-frames:v", "1", "-vf", "scale=640:-2", "-q:v", "4", str(fr)])
                new.append({"t0": round(t0, 2), "t1": round(t0 + step, 2), "dur": round(step, 2),
                            "frame": str(fr.relative_to(PROJ))})
        idx.write_text(json.dumps(new, indent=1))
        print(f"{f.stem}\t{len(sc)} -> {len(new)} scenes", flush=True)


def ocr():
    for idx in sorted(OUT.glob("*.scenes.json")):
        out = OUT / idx.name.replace(".scenes.json", ".json")
        if out.exists():
            continue
        sc = json.loads(idx.read_text())
        if not sc:
            out.write_text(json.dumps({"scenes": []})); continue
        tmp = OUT / (out.stem + ".ocr.json")
        subprocess.run([PY, str(PROJ.parent / "tools/ocr_haiku.py"), *[str(PROJ / s["frame"]) for s in sc],
                        "--out", str(tmp)], capture_output=True, text=True)
        fr = json.loads(tmp.read_text())["frames"] if tmp.exists() else []
        for s, r in zip(sc, fr):
            r.pop("file", None); s.update(r)
        out.write_text(json.dumps({"scenes": sc}, ensure_ascii=False, indent=1)); tmp.unlink(missing_ok=True)
        print(f"{out.stem}\t{len(sc)} scenes OCR", flush=True)
    print("DONE")


if __name__ == "__main__":
    {"detect": detect, "split": split, "ocr": ocr}[sys.argv[1]]()
