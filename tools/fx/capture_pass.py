#!/usr/bin/env python3
"""Real web-page capture -> animated PRESS shot (Politics). Method from Aviation/sydney-london/v1/quote_capture.py:
the page is captured live in a browser at DPR 2 (tools/fx/quote_capture.py, browser_exec) and the DOM gives the text rects;
here we animate it: headline framed first with a slow push, yellow marker sweeps the headline phrase ON the spoken word,
then a smooth scroll down to a lead-paragraph phrase that gets a second marker. Marker = multiply blend (text stays black on
yellow, like a real highlighter). Sub-pixel affine sampling every frame -> no held frames (judder 0).

usage: capture_pass.py <spec.json>
spec: {"name":"P2_capture","case":..,"beat":"B2","t0":4.32,"t1":8.62,"png":"..png","json":"..json",   # capture + DOM rects (CSS px)
       "shots":[{"t":0,"cx":720,"cy":330,"w":1240}, ...],     # camera keys (beat-relative s, CSS px centre, CSS width shown)
       "marks":[{"i":0,"word":"surrendered.","dur":0.55}, {"i":1,"word":"filing","nth":0,"dur":0.6}]}
       mark keys: lead (s), mode "multiply" (default, dark text on light) | "invert" (light text on dark ground)   # i = index in json marks"""
import json, re, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image

FX = Path(__file__).resolve().parent
ROOT = FX.parents[1]
W, H, FPS = 1920, 1080, 30
YEL = np.array([1.0, 0.86, 0.2], np.float32)


def word_t(ws, w, nth=0):
    n = lambda s: re.sub(r"[^a-z0-9']", "", s.lower().replace("\u2019", "'"))
    hits = [x["s"] for x in ws if n(x["w"]) == n(w)]
    return hits[nth]


def ease(u):
    u = min(1.0, max(0.0, u))
    return u * u * u * (u * (6 * u - 15) + 10)          # smootherstep


def cam(shots, t):
    if t <= shots[0]["t"]:
        return shots[0]
    for a, b in zip(shots, shots[1:]):
        if t <= b["t"]:
            u = (t - a["t"]) / (b["t"] - a["t"])
            e = u if a.get("lin") else ease(u)
            return {k: a[k] + (b[k] - a[k]) * e for k in ("cx", "cy", "w")}
    return shots[-1]


def ink_bbox(img, r, dpr):
    """tighten a DOM rect (CSS px) to the actual ink columns in the capture (DOM ranges can include trailing spaces)."""
    x0, y0, x1, y1 = [int(round(v * dpr)) for v in r]
    a = np.asarray(img.crop((x0, y0, x1, y1)).convert("L"), np.float32)
    cols = np.where((a < 140).sum(0) > 0)[0]
    if len(cols) == 0:
        return r
    return [(x0 + cols[0]) / dpr, r[1], (x0 + cols[-1] + 1) / dpr, r[3]]


def main():
    s = json.load(open(sys.argv[1]))
    case = s["case"]
    ws = json.load(open(ROOT / f"cases/{case}/{s.get('audio', 'audio_full_v1')}/words.json"))[s["beat"]]
    t0, t1 = s["t0"], s["t1"]; dur = t1 - t0
    img = Image.open(s["png"]).convert("RGB"); info = json.load(open(s["json"])); dpr = info.get("dpr", 2)
    src = np.asarray(img, np.float32) / 255.0
    # marker rects (CSS px) with sweep times (beat-relative -> clip-relative)
    marks = []
    for m in s["marks"]:
        rects = [ink_bbox(img, q, dpr) for q in info["marks"][m["i"]]]
        ts = word_t(ws, m["word"], m.get("nth", 0)) - t0 + m.get("lead", 0.0)
        tot = sum(q[2] - q[0] for q in rects); acc = 0.0
        for q in rects:                                   # multi-line phrase: lines sweep one after another
            w = q[2] - q[0]
            marks.append((q, ts + m["dur"] * acc / tot, ts + m["dur"] * (acc + w) / tot, m.get("mode", "multiply"))); acc += w
    pad_x, pad_y = s.get("pad", [5, 3])
    seg = ROOT / f"cases/{case}/edit/seg"; out = seg / f"{s['name']}.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "h264_videotoolbox", "-q:v", "72", "-allow_sw", "0", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)],
                          stdin=subprocess.PIPE)
    n = int(round(dur * FPS))
    for f in range(n):
        t = f / FPS
        # page with marker (multiply) in source pixels
        page = src.copy() if any(t > a for _, a, _, _ in marks) else src
        for q, a, b, mode in marks:
            if t <= a:
                continue
            u = ease((t - a) / max(1e-3, b - a)) if s.get("ease_mark", True) else min(1, (t - a) / (b - a))
            x0 = (q[0] - pad_x) * dpr; x1 = x0 + ((q[2] + pad_x) * dpr - x0) * u
            y0 = int(round((q[1] - pad_y) * dpr)); y1 = int(round((q[3] + pad_y) * dpr))
            xi0 = int(np.floor(x0)); xi1 = int(np.ceil(x1))
            if xi1 <= xi0:
                continue
            cov = np.ones(xi1 - xi0, np.float32); cov[-1] = 1 - (xi1 - x1)                 # sub-pixel leading edge
            blk = page[y0:y1, xi0:xi1]
            if mode == "invert":                                                           # light text on dark: text -> black, ground -> yellow
                hi = YEL * (1 - blk.mean(2, keepdims=True))
            else:
                hi = blk * YEL
            page[y0:y1, xi0:xi1] = blk * (1 - cov[None, :, None]) + hi * cov[None, :, None]
        c = cam(s["shots"], t + t0)
        sc = W / (c["w"] * dpr)                            # output px per source px
        # affine: output (X,Y) -> source (x,y)
        cx, cy = c["cx"] * dpr, c["cy"] * dpr
        a_ = 1 / sc
        pim = Image.fromarray((np.clip(page, 0, 1) * 255).astype(np.uint8))
        fr = pim.transform((W, H), Image.AFFINE, (a_, 0, cx - a_ * W / 2, 0, a_, cy - a_ * H / 2), resample=Image.BICUBIC, fillcolor=(255, 255, 255))
        ff.stdin.write(fr.tobytes())
    ff.stdin.close(); ff.wait()
    wav = ROOT / f"cases/{case}/{s.get('audio', 'audio_full_v1')}/{s['beat']}.wav"; vo = seg / f"{s['name']}_vo.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out), "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", str(wav), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{dur:.3f}", str(vo)], check=True)
    print("wrote", out, vo, "marks", [(round(float(a), 2), round(float(b), 2)) for _, a, b, _ in marks])


if __name__ == "__main__":
    main()
