#!/usr/bin/env python3
"""Real-page-capture renderer for WO trump-oversight-order-gfx4a (DOC/HLGT/KSTAT/QUOTELIFT/WEBHEAD).
Pure PIL + numpy + ffmpeg (no EffectCraft/AE dependency) -- "keep it simple and correct" per the WO.
Method = capture_pass.py's camera (affine push on the real page capture) + marker sweep (yellow multiply),
extended with: (a) a KSTAT "glyphs lift and count up" overlay, (b) a QUOTELIFT "line lifts forward, page
blurs behind" focus-pull after the sweep.

Each row is an independent clip: edit/seg4/<seg>_<t0cs>.mp4, 1920x1080 30fps, duration = t1-t0 exactly.
h264_videotoolbox -q:v 72 -allow_sw 0. Voice is muxed from audio_full_v4/<beat>.wav sliced [t0,t1].
"""
import json, re, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

CASE = Path("/Volumes/WORK/Auto Film Factory/Politics/cases/trump-oversight-order")
CAP = CASE / "edit/cap"
SEG = CASE / "edit/seg4"
QC = CASE / "edit/qc4"
SEG.mkdir(parents=True, exist_ok=True)
QC.mkdir(parents=True, exist_ok=True)
W, H, FPS = 1920, 1080, 30
YEL = np.array([1.0, 0.86, 0.2], np.float32)


def ease(u):
    u = min(1.0, max(0.0, u))
    return u * u * u * (u * (6 * u - 15) + 10)


def cam(shots, t):
    if t <= shots[0]["t"]:
        return shots[0]
    for a, b in zip(shots, shots[1:]):
        if t <= b["t"]:
            u = (t - a["t"]) / (b["t"] - a["t"])
            e = u if a.get("lin") else ease(u)
            return {k: a[k] + (b[k] - a[k]) * e for k in ("cx", "cy", "w")}
    return shots[-1]


def ink_bbox(src01, r, dpr, thresh=140):
    """tighten a CSS-px rect to the ink columns actually present (0..1 RGB array)."""
    x0, y0, x1, y1 = [int(round(v * dpr)) for v in r]
    a = (np.asarray(src01[y0:y1, x0:x1]).mean(2) * 255)
    cols = np.where((a < thresh).sum(0) > 0)[0]
    if len(cols) == 0:
        return r
    return [(x0 + cols[0]) / dpr, r[1], (x0 + cols[-1] + 1) / dpr, r[3]]


def word_box(src01, line_css, dpr, word_idx, n_words, min_gap=10, thresh=140):
    """split a line rect into word clusters by column ink-gaps; return the word_idx'th word's CSS rect."""
    x0, y0, x1, y1 = [v * dpr for v in line_css]
    pad = (4, 6)
    bx = (int(x0 - pad[0]), int(y0 - pad[1]), int(x1 + pad[0]), int(y1 + pad[1]))
    a = (np.asarray(src01[bx[1]:bx[3], bx[0]:bx[2]]).mean(2) * 255)
    cols = (a < thresh).sum(0)
    gap = cols == 0
    runs, in_run, start = [], False, 0
    for i, v in enumerate(gap):
        if not v and not in_run:
            start, in_run = i, True
        if v and in_run:
            runs.append((start, i)); in_run = False
    if in_run:
        runs.append((start, len(gap)))
    merged = [runs[0]]
    for s, e in runs[1:]:
        ps, pe = merged[-1]
        if s - pe <= min_gap:
            merged[-1] = (ps, e)
        else:
            merged.append((s, e))
    assert len(merged) == n_words, f"word split got {len(merged)} clusters, expected {n_words}: {merged}"
    s, e = merged[word_idx]
    return [(bx[0] + s) / dpr, bx[1] / dpr, (bx[0] + e) / dpr, bx[3] / dpr]


def sweep_mask(page01, marks, t, pad_x=5, pad_y=3, ox=0, oy=0):
    """apply yellow-highlight sweep for every (rect_css,a,b) active at time t; in-place on page01 (0..1).
    rect coords are in CSS px (full-image space); ox,oy = device-px crop origin to subtract."""
    for rect, a, b, dpr_, mode_ in marks:
        if t <= a:
            continue
        u = ease((t - a) / max(1e-3, b - a))
        x0 = (rect[0] - pad_x) * dpr_ - ox
        x1 = x0 + ((rect[2] + pad_x) * dpr_ - (rect[0] - pad_x) * dpr_) * u
        y0 = int(round((rect[1] - pad_y) * dpr_ - oy)); y1 = int(round((rect[3] + pad_y) * dpr_ - oy))
        y0 = max(0, y0); y1 = min(page01.shape[0], y1)
        xi0 = int(np.floor(max(0, x0))); xi1 = int(np.ceil(min(page01.shape[1], x1)))
        if xi1 <= xi0 or y1 <= y0:
            continue
        cov = np.ones(xi1 - xi0, np.float32)
        if x1 < page01.shape[1]:
            cov[-1] = 1 - (xi1 - x1)
        blk = page01[y0:y1, xi0:xi1]
        if mode_ == "invert":
            hi = YEL * (1 - blk.mean(2, keepdims=True))
        else:
            hi = blk * YEL
        page01[y0:y1, xi0:xi1] = blk * (1 - cov[None, :, None]) + hi * cov[None, :, None]


def affine_frame(page_img, c, dpr, ox=0, oy=0):
    sc = W / (c["w"] * dpr)
    cx, cy = c["cx"] * dpr - ox, c["cy"] * dpr - oy
    a_ = 1 / sc
    return page_img.transform((W, H), Image.AFFINE, (a_, 0, cx - a_ * W / 2, 0, a_, cy - a_ * H / 2),
                               resample=Image.BICUBIC, fillcolor=(255, 255, 255))


def viewport_crop(src01, c, dpr, margin=1.35):
    """device-px bbox of src01 that covers the camera viewport (+margin), clamped to the image."""
    vw = c["w"] * dpr; vh = vw * H / W
    cx, cy = c["cx"] * dpr, c["cy"] * dpr
    mw, mh = vw * margin, vh * margin
    H_img, W_img = src01.shape[:2]
    x0 = int(max(0, cx - mw / 2)); y0 = int(max(0, cy - mh / 2))
    x1 = int(min(W_img, cx + mw / 2)); y1 = int(min(H_img, cy + mh / 2))
    return x0, y0, x1, y1


def count_str(frac, target_digits="100,000"):
    v = int(round(99.0 * frac)) if frac < 1 else None
    if frac >= 1.0:
        return target_digits
    n = int(round(100000 * frac))
    return f"{n:,}"


def render(spec, frames_only=None):
    """spec: dict, see call sites in build_seg4a.py"""
    name = spec["name"]; beat = spec["beat"]; t0 = spec["t0"]; t1 = spec["t1"]
    dur = round(t1 - t0, 3); n = int(round(dur * FPS))
    img = Image.open(CAP / spec["png"]).convert("RGB")
    dpr = spec["dpr"]
    src01 = np.asarray(img, np.float32) / 255.0
    marks = []
    for m in spec["marks"]:
        rect = ink_bbox(src01, m["rect"], dpr) if m.get("tighten", True) else m["rect"]
        marks.append((rect, m["a"], m["b"], dpr, m.get("mode", "multiply")))
    shots = spec["shots"]
    extra = spec.get("extra")

    out = SEG / f"{name}.mp4"
    work = QC / "work"; work.mkdir(exist_ok=True)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "h264_videotoolbox", "-q:v", "72", "-allow_sw", "0",
                            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)],
                           stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    proof = {}
    want = frames_only or {}
    for f in range(n):
        t = f / FPS
        c = cam(shots, t)
        x0, y0, x1, y1 = viewport_crop(src01, c, dpr)
        page = src01[y0:y1, x0:x1].copy()
        if marks:
            sweep_mask(page, marks, t, ox=x0, oy=y0)
        pim = Image.fromarray((np.clip(page, 0, 1) * 255).astype(np.uint8))
        fr = affine_frame(pim, c, dpr, ox=x0, oy=y0)
        if extra and extra["kind"] == "kstat_lift":
            fr = kstat_overlay(fr, extra, t, c, dpr)
        elif extra and extra["kind"] == "quote_lift":
            fr = quote_overlay(fr, src01, extra, t, c, dpr)
        try:
            ff.stdin.write(fr.tobytes())
        except BrokenPipeError:
            break
        for tag, tt in want.items():
            if abs(t - tt) < 1 / (2 * FPS):
                fr.save(QC / f"{name}_{tag}.jpg", quality=92)
    try:
        ff.stdin.close()
    except BrokenPipeError:
        pass
    ff.wait()
    if ff.returncode:
        print("FFMPEG STDERR:", ff.stderr.read().decode()[-3000:])
        sys.exit("ffmpeg render failed")

    wav = CASE / f"audio_full_v4/{beat}.wav"
    vo = out.with_name(out.stem + "_vo.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out), "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}",
                     "-i", str(wav), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                     "-t", f"{dur:.3f}", str(vo)], check=True)
    import shutil
    shutil.move(str(vo), str(out))
    print("wrote", out, "dur", dur, "frames", n)
    return out


def kstat_overlay(fr, extra, t, c, dpr):
    """glyphs '100,000' lift off the line and scale up in place, count 0->100,000 over `dur`."""
    t0, dur = extra["t0"], extra["dur"]
    if t < t0:
        return fr
    u = ease(min(1.0, (t - t0) / dur))
    box = extra["box_css"]  # [x0,y0,x1,y1] css
    cx = (box[0] + box[2]) / 2 * dpr; cy = (box[1] + box[3]) / 2 * dpr
    sc_screen = W / (c["w"] * dpr)
    scx = cx - c["cx"] * dpr + c["w"] * dpr / 2
    scy = cy - c["cy"] * dpr + c["w"] * dpr * H / W / 2
    px, py = scx * sc_screen, scy * sc_screen
    base_h = (box[3] - box[1]) * dpr * sc_screen
    scale = 1 + 1.3 * u
    h = base_h * scale
    text = count_str(u)
    from PIL import ImageDraw, ImageFont
    fr = fr.copy()
    ov = Image.new("RGBA", fr.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", int(h))
    except Exception:
        font = ImageFont.load_default()
    bbox = d.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    op = int(255 * min(1.0, u / 0.15))
    d.text((px - tw / 2 - bbox[0], py - th / 2 - bbox[1]), text, font=font, fill=(10, 10, 10, op))
    fr = Image.alpha_composite(fr.convert("RGBA"), ov).convert("RGB")
    return fr


def quote_overlay(fr, src01, extra, t, c, dpr):
    """after the sweep ends, the highlighted line stays sharp while the rest of the frame blurs (focus pull)."""
    t0, dur = extra["t0"], extra["dur"]
    if t < t0:
        return fr
    u = ease(min(1.0, (t - t0) / dur))
    radius = 10 * u
    if radius < 0.3:
        return fr
    blurred = fr.filter(ImageFilter.GaussianBlur(radius))
    rect = extra["rect_css"]
    sc_screen = W / (c["w"] * dpr)
    x0 = (rect[0] * dpr - c["cx"] * dpr + c["w"] * dpr / 2) * sc_screen - 10
    y0 = (rect[1] * dpr - c["cy"] * dpr + c["w"] * dpr * H / W / 2) * sc_screen - 10
    x1 = (rect[2] * dpr - c["cx"] * dpr + c["w"] * dpr / 2) * sc_screen + 10
    y1 = (rect[3] * dpr - c["cy"] * dpr + c["w"] * dpr * H / W / 2) * sc_screen + 10
    x0, y0, x1, y1 = [int(max(0, min(v, W if i % 2 == 0 else H))) for i, v in enumerate((x0, y0, x1, y1))]
    if x1 <= x0 or y1 <= y0:
        return blurred
    sharp_region = fr.crop((x0, y0, x1, y1))
    grow = 1 + 0.08 * u
    gw, gh = int((x1 - x0) * grow), int((y1 - y0) * grow)
    sharp_region = sharp_region.resize((gw, gh), Image.BICUBIC)
    out = blurred.copy()
    px = (x0 + x1) // 2 - gw // 2
    py = (y0 + y1) // 2 - gh // 2
    out.paste(sharp_region, (px, py))
    return out
