#!/usr/bin/env python3
"""Viewer-pace gate for rendered page/graphic segments (owner 23/11: "edit cho người xem, không phải cho máy").

Per mp4 it measures, from the pixels:
  lead_dark  frames at the start darker than 80% of the shot median (fade-from-black / dark flash at the cut)
  hold       seconds the finished highlight stays on screen before the cut (yellow-pixel plateau -> end)
  max_px     largest frame-to-frame vertical page move, in 1080p pixels (scroll whiplash)
  reversals  direction flips of the page move (back-and-forth jitter)
  move_s     total seconds the page is moving
Gate: lead_dark == 0, hold >= 1.5 (if the shot has a highlight), max_px <= 24, reversals == 0, and if it moves,
the move lasts >= 0.6 s (no teleports).

usage: gfx_gate.py file.mp4 [...]   -> one line per file + FAIL reasons; exit 1 if any FAIL
"""
import subprocess
import sys

import numpy as np

W, H = 480, 270


def frames(path):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"scale={W}:{H}", "-f", "rawvideo",
                        "-pix_fmt", "rgb24", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, H, W, 3).astype(np.float32)


def vshift(a, b, maxs=60):
    pa = a.mean(axis=(1, 2)); pb = b.mean(axis=(1, 2))
    pa -= pa.mean(); pb -= pb.mean()
    best, bc = 0, -1e18
    for s in range(-maxs, maxs + 1):
        c = (pa[s:] * pb[:len(pb) - s]).sum() if s >= 0 else (pa[:s] * pb[-s:]).sum()
        if c > bc:
            best, bc = s, c
    return best


def gate(path):
    fr = frames(path)
    n = len(fr)
    Y = fr.mean(axis=(1, 2, 3))
    med = float(np.median(Y))
    lead = 0
    while lead < n and Y[lead] < 0.8 * med:
        lead += 1
    R, G, B = fr[..., 0], fr[..., 1], fr[..., 2]
    yel = ((R > 180) & (G > 160) & (B < 130)).sum(axis=(1, 2)).astype(float)
    hold = None
    if yel.max() > 30:
        tc = int(np.argmax(yel >= 0.95 * yel.max()))
        hold = (n - tc) / 30
    s = [vshift(fr[i], fr[i + 1]) * (1080 / H) for i in range(n - 1)]
    moving = [v for v in s if abs(v) >= 2]
    signs = [np.sign(v) for v in moving]
    rev = sum(1 for a, b in zip(signs, signs[1:]) if a != b)
    max_px = max((abs(v) for v in s), default=0)
    move_s = len(moving) / 30
    fails = []
    if lead:
        fails.append(f"lead_dark {lead}fr")
    if hold is not None and hold < 1.5:
        fails.append(f"hold {hold:.2f}s<1.5")
    if max_px > 24:
        fails.append(f"max_px {max_px:.0f}>24")
    if rev:
        fails.append(f"reversals {rev}")
    if moving and move_s < 0.6:
        fails.append(f"teleport move {move_s:.2f}s")
    return n / 30, lead, hold, max_px, rev, move_s, fails


if __name__ == "__main__":
    bad = 0
    for p in sys.argv[1:]:
        d, lead, hold, mx, rev, mv, fails = gate(p)
        bad += bool(fails)
        h = "-" if hold is None else f"{hold:.2f}"
        print(f"{'FAIL' if fails else 'PASS'} {p.split('/')[-1]} dur {d:.2f} lead {lead} hold {h} max_px {mx:.0f} "
              f"rev {rev} move {mv:.2f}s {'; '.join(fails)}")
    sys.exit(1 if bad else 0)
