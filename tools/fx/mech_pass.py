#!/usr/bin/env python3
"""MECH: mechanism diagram (Congress request -> contractor -> White House review -> answer / penalty).
Icons + real EO penalty crops (edit/cap/wh_eo.png). No typed labels, no circles/rings/arrows as annotation marks.
Nodes appear only when the voice reaches them; a connector draws only after both its endpoints exist;
one accent color marks the active causal path (plus a one-off red flash for the White House "no").

Pure PIL + ffmpeg frame render (h264_videotoolbox). Standalone script for case trump-oversight-order / WO gfx4d.
"""
import json
import math
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path("/Volumes/WORK/Auto Film Factory/Politics")
CASE = ROOT / "cases/trump-oversight-order"
W, H, FPS = 1920, 1080, 30

BG = (14, 15, 19)
GRAY = (118, 122, 132)
GRAY_DIM = (70, 72, 80)
WHITE = (225, 227, 232)
AMBER = (255, 176, 59)      # single accent color = active causal path
RED = (214, 69, 69)         # "the answer is no" flash

# ---- node layout (1920x1080) ----
CAPITOL = (330, 560)
CONTRACTOR = (960, 560)
WHITEHOUSE = (960, 258)
COURT = (1610, 820)
PERSON_HOME = (960, 560)
PERSON_OUT = (1200, 760)

WH_EO = Image.open(CASE / "edit/cap/wh_eo.png").convert("RGB")
DPR = 2


def crop_box(box, padx=14, pady=14):
    x0, y0, x1, y1 = [v * DPR for v in box]
    x0 -= padx; x1 += padx; y0 -= pady; y1 += pady
    return WH_EO.crop((int(x0), int(y0), int(x1), int(y1)))


CROP_TERMINATION = crop_box([464.140625, 3051.6875, 908.6875, 3074.6875])
CROP_DEBARMENT = crop_box([329, 3080.609375, 667.140625, 3103.609375])


def ease(u):
    u = min(1.0, max(0.0, u))
    return u * u * u * (u * (6 * u - 15) + 10)


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_c(c0, c1, t):
    return tuple(int(round(lerp(a, b, t))) for a, b in zip(c0, c1))


def fade(t, t_in, dur=0.3):
    return ease((t - t_in) / dur) if dur > 0 else (1.0 if t >= t_in else 0.0)


# ---------------------------------------------------------------- icon drawing (polygons/lines only)
def draw_capitol(d, cx, cy, s, color, a):
    col = color + (a,)
    base_w, base_h = 140 * s, 26 * s
    d.rectangle([cx - base_w / 2, cy + 34 * s, cx + base_w / 2, cy + 34 * s + base_h], fill=col)
    # stepped dome (no circles): 4 stacked trapezoids narrowing upward
    steps = 5
    for i in range(steps):
        w0 = (92 - i * 15) * s
        y0 = cy - (6 + i * 12) * s
        y1 = y0 + 12 * s
        d.rectangle([cx - w0 / 2, y0, cx + w0 / 2, y1], fill=col)
    # pediment + columns
    d.polygon([(cx - 80 * s, cy + 30 * s), (cx, cy - 2 * s), (cx + 80 * s, cy + 30 * s)], fill=col)
    for i in range(-3, 4):
        x = cx + i * 20 * s
        d.rectangle([x - 4 * s, cy + 6 * s, x + 4 * s, cy + 34 * s], fill=col)


def draw_whitehouse(d, cx, cy, s, color, a):
    col = color + (a,)
    d.rectangle([cx - 100 * s, cy + 6 * s, cx + 100 * s, cy + 40 * s], fill=col)
    d.polygon([(cx - 92 * s, cy + 6 * s), (cx, cy - 34 * s), (cx + 92 * s, cy + 6 * s)], fill=col)
    for i in range(-4, 5):
        x = cx + i * 20 * s
        d.rectangle([x - 4 * s, cy + 10 * s, x + 4 * s, cy + 38 * s], fill=col)


def draw_court(d, cx, cy, s, color, a):
    col = color + (a,)
    d.rectangle([cx - 90 * s, cy + 6 * s, cx + 90 * s, cy + 36 * s], fill=col)
    d.polygon([(cx - 84 * s, cy + 6 * s), (cx, cy - 30 * s), (cx + 84 * s, cy + 6 * s)], fill=col)
    for i in range(-3, 4):
        x = cx + i * 22 * s
        d.rectangle([x - 4 * s, cy + 10 * s, x + 4 * s, cy + 34 * s], fill=col)
    d.rectangle([cx - 96 * s, cy + 36 * s, cx + 96 * s, cy + 44 * s], fill=col)


def draw_contractor(d, cx, cy, s, color, a):
    col = color + (a,)
    d.rectangle([cx - 54 * s, cy - 56 * s, cx + 54 * s, cy + 56 * s], fill=col)
    win = color + (max(0, a - 60),)
    for row in range(-3, 4):
        for c_ in range(-2, 3):
            wx = cx + c_ * 20 * s
            wy = cy + row * 14 * s
            d.rectangle([wx - 5 * s, wy - 5 * s, wx + 5 * s, wy + 5 * s], fill=win)


def draw_envelope(d, cx, cy, s, color, a):
    col = color + (a,)
    w_, h_ = 48 * s, 32 * s
    x0, y0 = cx - w_ / 2, cy - h_ / 2
    x1, y1 = cx + w_ / 2, cy + h_ / 2
    d.rectangle([x0, y0, x1, y1], outline=col, width=max(1, int(3 * s)))
    d.line([(x0, y0), (cx, cy + 4 * s), (x1, y0)], fill=col, width=max(1, int(3 * s)))


def draw_person(d, cx, cy, s, color, a):
    col = color + (a,)
    d.rectangle([cx - 10 * s, cy - 38 * s, cx + 10 * s, cy - 18 * s], fill=col)  # head (square, not a circle)
    d.polygon([(cx - 20 * s, cy + 30 * s), (cx + 20 * s, cy + 30 * s), (cx + 14 * s, cy - 14 * s), (cx - 14 * s, cy - 14 * s)], fill=col)


def draw_shield(d, cx, cy, s, color, a):
    col = color + (a,)
    pts = [(cx, cy - 46 * s), (cx + 30 * s, cy - 34 * s), (cx + 30 * s, cy + 6 * s),
           (cx, cy + 46 * s), (cx - 30 * s, cy + 6 * s), (cx - 30 * s, cy - 34 * s)]
    d.line(pts + [pts[0]], fill=col, width=max(2, int(4 * s)))


# ---------------------------------------------------------------- connector
def draw_connector(d, p0, p1, color, a, progress, width=4):
    progress = max(0.0, min(1.0, progress))
    if progress <= 0:
        return
    x = lerp(p0[0], p1[0], progress)
    y = lerp(p0[1], p1[1], progress)
    d.line([p0, (x, y)], fill=color + (a,), width=width)


def draw_elbow(d, p0, p1, color, a, progress, width=4):
    """down then across, drawn progressively"""
    mid = (p0[0], p1[1])
    seg1 = math.hypot(mid[0] - p0[0], mid[1] - p0[1])
    seg2 = math.hypot(p1[0] - mid[0], p1[1] - mid[1])
    tot = seg1 + seg2
    if tot <= 0 or progress <= 0:
        return
    done = progress * tot
    if done <= seg1:
        t = done / seg1 if seg1 else 1
        d.line([p0, (lerp(p0[0], mid[0], t), lerp(p0[1], mid[1], t))], fill=color + (a,), width=width)
    else:
        d.line([p0, mid], fill=color + (a,), width=width)
        t = (done - seg1) / seg2 if seg2 else 1
        d.line([mid, (lerp(mid[0], p1[0], t), lerp(mid[1], p1[1], t))], fill=color + (a,), width=width)


# ---------------------------------------------------------------- shared background
def base_frame():
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    for i in range(H):
        t = i / H
        c = lerp_c((16, 17, 22), (10, 10, 13), t)
        d.line([(0, i), (W, i)], fill=c)
    return im


def render(name, dur, frame_fn):
    work = ROOT / "tools/fx/work" / name
    work.mkdir(parents=True, exist_ok=True)
    n = int(math.ceil(dur * FPS)) + 1
    raw_path = work / f"{name}_raw.mp4"
    ff = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-frames:v", str(n), "-c:v", "h264_videotoolbox", "-q:v", "72", "-allow_sw", "0",
         "-pix_fmt", "yuv420p", str(raw_path)], stdin=subprocess.PIPE)
    content_frames = int(round(dur * FPS))
    proof_idx = {0: "a", content_frames // 2: "b", max(0, content_frames - 1): "c"}
    proof_frames = {}
    for i in range(n):
        t = i / FPS
        frame = base_frame().convert("RGBA")
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        frame_fn(d, overlay, t)
        frame = Image.alpha_composite(frame, overlay).convert("RGB")
        ff.stdin.write(frame.tobytes())
        if i in proof_idx:
            proof_frames[proof_idx[i]] = frame.copy()
    ff.stdin.close()
    ff.wait()
    return raw_path, proof_frames


def mux(raw_path, out_path, wav, t0, dur):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(raw_path), "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", str(wav),
         "-map", "0:v", "-map", "1:a", "-c:v", "h264_videotoolbox", "-q:v", "72", "-allow_sw", "0",
         "-c:a", "aac", "-b:a", "192k", "-t", f"{dur:.3f}", "-movflags", "+faststart", str(out_path)], check=True)


def main():
    rows = [
        dict(name="B16_412", seg="B16", t0=4.12, t1=6.73),
        dict(name="B16_673", seg="B16", t0=6.73, t1=8.96),
        dict(name="B16_1160", seg="B16", t0=11.60, t1=17.20),
        dict(name="B16_1720", seg="B16", t0=17.20, t1=23.20),
    ]
    wav = CASE / "audio_full_v4/B16.wav"
    seg4 = CASE / "edit/seg4"
    qc4 = CASE / "edit/qc4"
    seg4.mkdir(parents=True, exist_ok=True)
    qc4.mkdir(parents=True, exist_ok=True)
    index_lines = []
    icon_s = 1.0

    # ------------------------------------------------------------ CLIP 1: B16_412 (row 4.12-6.73)
    def f1(d, overlay, t):
        env_t = min(1.0, t / 0.3)
        ex = lerp(CAPITOL[0] + 60, CONTRACTOR[0] - 70, env_t)
        ey = lerp(CAPITOL[1], CONTRACTOR[1], env_t)
        draw_connector(d, (CAPITOL[0] + 70, CAPITOL[1] - 4), (CONTRACTOR[0] - 70, CONTRACTOR[1] - 4), GRAY, 190, 1.0, 3)
        draw_capitol(d, *CAPITOL, icon_s, WHITE, 255)
        draw_contractor(d, *CONTRACTOR, icon_s, WHITE, 255)
        if env_t < 1.0:
            draw_envelope(d, ex, ey - 4, 0.8, AMBER, 255)
        wh_a = int(255 * fade(t, 0.36, 0.3))
        if wh_a > 0:
            draw_whitehouse(d, *WHITEHOUSE, icon_s, WHITE, wh_a)
            line_prog = min(1.0, (t - 0.36) / 0.4) if t > 0.36 else 0
            red_a = int(RED[0] and wh_a)
            draw_connector(d, (WHITEHOUSE[0], WHITEHOUSE[1] + 42), (CONTRACTOR[0], CONTRACTOR[1] - 58), RED, wh_a, line_prog, 4)
        three_t = max(0.0, min(1.0, (t - 1.18) / 0.6))
        if three_t > 0:
            court_a = int(255 * fade(t, 1.18, 0.3))
            draw_court(d, *COURT, icon_s * 0.9, WHITE, court_a)
            draw_connector(d, (CONTRACTOR[0] + 54, CONTRACTOR[1] + 20), (CAPITOL[0] + 60, CAPITOL[1] + 20), GRAY, 200, three_t, 3)
            draw_connector(d, (CONTRACTOR[0], CONTRACTOR[1] - 58), (WHITEHOUSE[0], WHITEHOUSE[1] + 42), GRAY, 160, three_t, 3)
            draw_connector(d, (CONTRACTOR[0] + 54, CONTRACTOR[1] + 10), (COURT[0] - 70, COURT[1] - 10), GRAY, 200, three_t, 3)

    raw1, proof1 = render("B16_412", 6.73 - 4.12, f1)
    out1 = seg4 / "B16_412.mp4"
    mux(raw1, out1, wav, 4.12, 6.73 - 4.12)
    index_lines.append(("B16", "4.12", "6.73", "edit/seg4/B16_412.mp4", "MECH",
                         "and say the answer is no. Three paths follow."))

    # ------------------------------------------------------------ CLIP 2: B16_673 (row 6.73-8.96)
    def f2(d, overlay, t):
        draw_capitol(d, *CAPITOL, icon_s, WHITE, 255)
        draw_contractor(d, *CONTRACTOR, icon_s, WHITE, 255)
        draw_whitehouse(d, *WHITEHOUSE, icon_s, WHITE, 255)
        draw_court(d, *COURT, icon_s * 0.9, WHITE, 255)
        k = ease(min(1.0, t / 0.3))
        active_col = lerp_c(GRAY, AMBER, k)
        dim_col = lerp_c(GRAY, GRAY_DIM, k)
        draw_connector(d, (CONTRACTOR[0] - 54, CONTRACTOR[1] + 20), (CAPITOL[0] + 60, CAPITOL[1] + 20), active_col, 255, 1.0, 5)
        draw_connector(d, (CONTRACTOR[0], CONTRACTOR[1] - 58), (WHITEHOUSE[0], WHITEHOUSE[1] + 42), dim_col, 150, 1.0, 3)
        draw_connector(d, (CONTRACTOR[0] + 54, CONTRACTOR[1] + 10), (COURT[0] - 70, COURT[1] - 10), dim_col, 150, 1.0, 3)

    raw2, proof2 = render("B16_673", 8.96 - 6.73, f2)
    out2 = seg4 / "B16_673.mp4"
    mux(raw2, out2, wav, 6.73, 8.96 - 6.73)
    index_lines.append(("B16", "6.73", "8.96", "edit/seg4/B16_673.mp4", "MECH", "Path one. The company cooperates."))

    # ------------------------------------------------------------ CLIP 3: B16_1160 (row 11.60-17.20)
    panel_top = (1080, 210)
    crop1_scaled = CROP_TERMINATION.resize((int(CROP_TERMINATION.width * 0.52), int(CROP_TERMINATION.height * 0.52)))
    crop2_scaled = CROP_DEBARMENT.resize((int(CROP_DEBARMENT.width * 0.52), int(CROP_DEBARMENT.height * 0.52)))

    def f3(d, overlay, t):
        draw_capitol(d, *CAPITOL, icon_s, WHITE, 255)
        draw_whitehouse(d, *WHITEHOUSE, icon_s, WHITE, 255)
        draw_court(d, *COURT, icon_s * 0.9, WHITE, 255)
        draw_connector(d, (CONTRACTOR[0] - 54, CONTRACTOR[1] + 20), (CAPITOL[0] + 60, CAPITOL[1] + 20), AMBER, 255, 1.0, 5)
        draw_connector(d, (CONTRACTOR[0], CONTRACTOR[1] - 58), (WHITEHOUSE[0], WHITEHOUSE[1] + 42), GRAY_DIM, 150, 1.0, 3)
        draw_connector(d, (CONTRACTOR[0] + 54, CONTRACTOR[1] + 10), (COURT[0] - 70, COURT[1] - 10), GRAY_DIM, 150, 1.0, 3)
        grey_k = ease(min(1.0, max(0.0, (t - 5.03) / 0.5)))
        contractor_col = lerp_c(WHITE, GRAY_DIM, grey_k)
        draw_contractor(d, *CONTRACTOR, icon_s, contractor_col, 255)
        branch_prog = min(1.0, max(0.0, (t - 0.97) / 0.5))
        if branch_prog > 0:
            draw_elbow(d, (WHITEHOUSE[0] + 50, WHITEHOUSE[1] + 10), (panel_top[0] - 20, panel_top[1] + 30), RED, 220, branch_prog, 3)
        a1 = int(255 * fade(t, 2.80, 0.35))
        if a1 > 0:
            img = crop1_scaled.copy()
            if a1 < 255:
                img = Image.blend(Image.new("RGB", img.size, BG), img, a1 / 255)
            overlay.paste(img, (panel_top[0], panel_top[1]))
        a2 = int(255 * fade(t, 4.12, 0.35))
        if a2 > 0:
            img = crop2_scaled.copy()
            if a2 < 255:
                img = Image.blend(Image.new("RGB", img.size, BG), img, a2 / 255)
            overlay.paste(img, (panel_top[0], panel_top[1] + crop1_scaled.height + 18))

    raw3, proof3 = render("B16_1160", 17.20 - 11.60, f3)
    out3 = seg4 / "B16_1160.mp4"
    mux(raw3, out3, wav, 11.60, 17.20 - 11.60)
    index_lines.append(("B16", "11.60", "17.20", "edit/seg4/B16_1160.mp4", "MECH",
                         "The directive says agencies shall consider whether to end the contract or suspend or debar the company."))

    # ------------------------------------------------------------ CLIP 4: B16_1720 (row 17.20-23.20)
    def f4(d, overlay, t):
        draw_capitol(d, *CAPITOL, icon_s, WHITE, 255)
        draw_whitehouse(d, *WHITEHOUSE, icon_s, WHITE, 255)
        draw_court(d, *COURT, icon_s * 0.9, WHITE, 255)
        draw_contractor(d, *CONTRACTOR, icon_s, GRAY_DIM, 255)
        draw_connector(d, (CONTRACTOR[0] - 54, CONTRACTOR[1] + 20), (CAPITOL[0] + 60, CAPITOL[1] + 20), AMBER, 200, 1.0, 4)
        draw_connector(d, (CONTRACTOR[0], CONTRACTOR[1] - 58), (WHITEHOUSE[0], WHITEHOUSE[1] + 42), GRAY_DIM, 120, 1.0, 3)
        draw_connector(d, (CONTRACTOR[0] + 54, CONTRACTOR[1] + 10), (COURT[0] - 70, COURT[1] - 10), GRAY_DIM, 120, 1.0, 3)
        step_t = ease(min(1.0, max(0.0, (t - 0.37) / 0.4)))
        if step_t > 0:
            px = lerp(PERSON_HOME[0], PERSON_OUT[0], step_t)
            py = lerp(PERSON_HOME[1], PERSON_OUT[1], step_t)
            pa = int(255 * fade(t, 0.37, 0.3))
            draw_person(d, px, py, 0.9, WHITE, pa)
            line_prog = min(1.0, max(0.0, (t - 2.99) / 0.5))
            if line_prog > 0:
                draw_connector(d, (px - 14, py - 10), (CAPITOL[0] + 60, CAPITOL[1] - 20), AMBER, 230, line_prog, 3)
            shield_a = int(255 * fade(t, 4.32, 0.35))
            if shield_a > 0:
                draw_shield(d, px, py, 0.9, AMBER, shield_a)

    raw4, proof4 = render("B16_1720", 23.20 - 17.20, f4)
    out4 = seg4 / "B16_1720.mp4"
    mux(raw4, out4, wav, 17.20, 23.20 - 17.20)
    index_lines.append(("B16", "17.20", "23.20", "edit/seg4/B16_1720.mp4", "MECH",
                         "And an employee who reports contract waste or law-breaking to a member of Congress is shielded from reprisal. Trump's"))

    # ------------------------------------------------------------ proof frames (start/action/end) -> edit/qc4/MECH_{a,b,c}.jpg
    for key, im_ in (("a", proof1["a"]), ("b", proof3["b"]), ("c", proof4["c"])):
        im_.convert("RGB").save(qc4 / f"MECH_{key}.jpg", quality=92)

    idx_path = seg4 / "index_D.tsv"
    with open(idx_path, "w") as fh:
        fh.write("seg\tt0\tt1\tfile\ttemplate\tphrase\n")
        for row in index_lines:
            fh.write("\t".join(row) + "\n")
    print("wrote", idx_path)
    for r in index_lines:
        print(r)


if __name__ == "__main__":
    main()
