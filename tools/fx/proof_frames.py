#!/usr/bin/env python3
"""Regenerate the a/b/c proof jpgs for every seg4 row (no re-encode) -- fixes the earlier filename collision."""
import sys
sys.path.insert(0, "/Volumes/WORK/Auto Film Factory/Politics/tools/fx")
import numpy as np
from PIL import Image
import pil_pagepush as R
import build_seg4a as B

for r in B.rows:
    name = r["name"]
    img = Image.open(R.CAP / r["png"]).convert("RGB")
    dpr = r["dpr"]
    src01 = np.asarray(img, np.float32) / 255.0
    marks = []
    for m in r["marks"]:
        rect = R.ink_bbox(src01, m["rect"], dpr)
        marks.append((rect, m["a"], m["b"], dpr, m.get("mode", "multiply")))
    shots = r["shots"]
    extra = r.get("extra")
    for tag, t in r["frames"].items():
        c = R.cam(shots, t)
        x0, y0, x1, y1 = R.viewport_crop(src01, c, dpr)
        page = src01[y0:y1, x0:x1].copy()
        if marks:
            R.sweep_mask(page, marks, t, ox=x0, oy=y0)
        pim = Image.fromarray((np.clip(page, 0, 1) * 255).astype(np.uint8))
        fr = R.affine_frame(pim, c, dpr, ox=x0, oy=y0)
        if extra and extra["kind"] == "kstat_lift":
            fr = R.kstat_overlay(fr, extra, t, c, dpr)
        elif extra and extra["kind"] == "quote_lift":
            fr = R.quote_overlay(fr, src01, extra, t, c, dpr)
        fr.save(R.QC / f"{name}_{tag}.jpg", quality=92)
    print("proof frames:", name)
