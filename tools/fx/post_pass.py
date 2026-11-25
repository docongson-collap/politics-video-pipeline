#!/usr/bin/env python3
"""L-POST: real Truth Social capture (trumpstruth.org .status card PNG) floating over blurred, darkened real footage.
Slow push on the card, yellow multiply marker sweeps verbatim phrases ON the spoken words (words.json), small source tag
bottom-left (PIL text). Phrases are located in the PNG with tesseract (word boxes); exit 2 if a phrase is not found verbatim.
Sub-pixel affine every frame + moving footage -> judder 0. Footage retimed N/30 (29.97 -> 30, no dup frames).

usage: post_pass.py <spec.json>
spec: {"name":"P19_post","case":..,"beat":"B19","t0":1.7,"t1":14.3005,"png":"..T1.png",
       "bg":"..clip.mp4","bg_ss":27.0,
       "card":{"w0":1440,"w1":1560,"cx0":960,"cy0":505,"cx1":960,"cy1":495},
       "marks":[{"phrase":"Fake Dan Sullivan, ...","word":"fake","dur":6.2,"nth":0,"lead":0}],
       "tag":"Donald Trump, Truth Social, Nov 5, 2026 (via trumpstruth.org)"}
"""
import json, re, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FX = Path(__file__).resolve().parent
ROOT = FX.parents[1]
W, H, FPS = 1920, 1080, 30
YEL = np.array([1.0, 0.86, 0.2], np.float32)
FONT = ROOT / "kho/fonts/Inter/Inter-Medium.otf"
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower().replace("\u2019", "'"))


def ease(u):
    u = min(1.0, max(0.0, u)); return u * u * u * (u * (6 * u - 15) + 10)


def word_t(ws, w, nth=0):
    return [x["s"] for x in ws if norm(x["w"]) == norm(w)][nth]


def ocr_words(png):
    tsv = subprocess.run(["tesseract", str(png), "-", "tsv"], capture_output=True, text=True).stdout.splitlines()
    out = []
    for ln in tsv[1:]:
        c = ln.split("\t")
        if len(c) >= 12 and c[0] == "5" and c[11].strip():
            out.append({"t": c[11], "x": int(c[6]), "y": int(c[7]), "w": int(c[8]), "h": int(c[9]),
                        "line": (int(c[2]), int(c[3]), int(c[4]))})
    return out


def phrase_lines(words, phrase, pad=None):
    toks = [norm(t) for t in phrase.split() if norm(t)]
    nw = [norm(w["t"]) for w in words]
    for i in range(len(nw) - len(toks) + 1):
        if nw[i:i + len(toks)] == toks:
            seq = words[i:i + len(toks)]; lines = {}
            for w in seq:
                lines.setdefault(w["line"], []).append(w)
            rects = []
            for k in sorted(lines, key=lambda k: lines[k][0]["y"]):
                L = lines[k]; top = int(np.median([w["y"] for w in L]))
                if pad is None:
                    rects.append([L[0]["x"] - 10, top - 14, L[-1]["x"] + L[-1]["w"] + 10, top + 54 + 16])
                else:                                   # spec "mark_pad": [px, top, bottom] around the median word box height
                    hm = int(np.median([w["h"] for w in L]))
                    rects.append([L[0]["x"] - pad[0], top - pad[1], L[-1]["x"] + L[-1]["w"] + pad[0], top + hm + pad[2]])
            return rects
    return None


def main():
    s = json.load(open(sys.argv[1])); case = s["case"]
    ws = json.load(open(ROOT / f"cases/{case}/{s.get('audio', 'audio_full_v1')}/words.json"))[s["beat"]]
    t0, t1 = s["t0"], s["t1"]; n = int(round((t1 - t0) * FPS))
    card = Image.open(s["png"]).convert("RGB"); src = np.asarray(card, np.float32) / 255.0
    cw, ch = card.size
    words = ocr_words(s["png"]); marks = []
    for m in s["marks"]:
        rects = phrase_lines(words, m["phrase"], s.get("mark_pad"))
        if not rects:
            print("PHRASE NOT FOUND VERBATIM:", m["phrase"]); sys.exit(2)
        ts = word_t(ws, m["word"], m.get("nth", 0)) - t0 + m.get("lead", 0.0)
        tot = sum(r[2] - r[0] for r in rects); acc = 0.0
        for r in rects:
            w = r[2] - r[0]; marks.append((r, ts + m["dur"] * acc / tot, ts + m["dur"] * (acc + w) / tot)); acc += w
        print("mark", m["phrase"][:40], "@", m["word"], round(ts + t0, 2), rects)
    # rounded card alpha + soft shadow on a padded canvas
    M = 160; R = 28
    amask = Image.new("L", (cw, ch), 0); ImageDraw.Draw(amask).rounded_rectangle([0, 0, cw - 1, ch - 1], R, fill=255)
    shadow = Image.new("RGBA", (cw + 2 * M, ch + 2 * M), (0, 0, 0, 0))
    sh = Image.new("L", shadow.size, 0); ImageDraw.Draw(sh).rounded_rectangle([M, M + 30, M + cw, M + ch + 30], R, fill=170)
    shadow.putalpha(sh.filter(ImageFilter.GaussianBlur(48)))
    # background footage: blurred + darkened, retimed to exact 30 fps
    bg = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(s["bg_ss"]), "-i", s["bg"], "-t", f"{(n + 2) / FPS:.3f}",
                           "-vf", "setpts=N/30/TB," + s.get("bg_crop", "crop=iw:ih:0:0") + ",scale=1920:1080:flags=lanczos,gblur=sigma=30,eq=saturation=0.75",
                           "-r", "30", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    out = ROOT / f"cases/{case}/edit/seg/{s['name']}.mp4"
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "h264_videotoolbox", "-q:v", "72", "-allow_sw", "0", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)],
                          stdin=subprocess.PIPE)
    # source tag layer (static)
    tag = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(tag); f = ImageFont.truetype(str(FONT), 26)
    d.text((64, H - 64), s["tag"], font=f, fill=(255, 255, 255, 215), anchor="ls")
    c = s["card"]; prev = None
    for i in range(n):
        t = i / FPS; u = i / max(1, n - 1)
        raw = bg.stdout.read(W * H * 3)
        if len(raw) < W * H * 3:
            raw = prev
        prev = raw
        fr = (np.frombuffer(raw, np.uint8).reshape(H, W, 3).astype(np.float32) / 255.0) * 0.42
        y = np.linspace(-1, 1, H)[:, None, None]; x = np.linspace(-1, 1, W)[None, :, None]
        fr *= 1 - 0.35 * np.clip(x * x + y * y - 0.3, 0, 1)                       # vignette
        frame = Image.fromarray((np.clip(fr, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
        page = src.copy() if any(t > a for _, a, _ in marks) else src
        for q, a, b in marks:
            if t <= a:
                continue
            e = ease((t - a) / max(1e-3, b - a)); x0 = q[0]; x1 = x0 + (q[2] - q[0]) * e
            xi0, xi1 = int(np.floor(x0)), int(np.ceil(x1))
            if xi1 <= xi0:
                continue
            cov = np.ones(xi1 - xi0, np.float32); cov[-1] = 1 - (xi1 - x1)
            blk = page[q[1]:q[3], xi0:xi1]
            page[q[1]:q[3], xi0:xi1] = blk * (1 - cov[None, :, None]) + blk * YEL * cov[None, :, None]
        cim = Image.fromarray((np.clip(page, 0, 1) * 255).astype(np.uint8)).convert("RGBA"); cim.putalpha(amask)
        pad = shadow.copy(); pad.alpha_composite(cim, (M, M))
        k = ease(u) * 0.35 + u * 0.65                                                 # gentle accelerating-free push
        wd = c["w0"] + (c["w1"] - c["w0"]) * k; cx = c["cx0"] + (c["cx1"] - c["cx0"]) * k; cy = c["cy0"] + (c["cy1"] - c["cy0"]) * k
        intro = ease(t / 0.35); cy += 26 * (1 - intro)
        sc = wd / cw; a_ = 1 / sc
        # output (X,Y) -> padded source: x = (X - (cx - wd/2)) / sc + M
        lay = pad.transform((W, H), Image.AFFINE, (a_, 0, M - a_ * (cx - wd / 2), 0, a_, M - a_ * (cy - ch * sc / 2)),
                            resample=Image.BICUBIC, fillcolor=(0, 0, 0, 0))
        if intro < 1:
            lay.putalpha(lay.getchannel("A").point(lambda v: int(v * intro)))
        frame.alpha_composite(lay); frame.alpha_composite(tag)
        ff.stdin.write(frame.convert("RGB").tobytes())
    ff.stdin.close(); ff.wait(); bg.kill()
    wav = ROOT / f"cases/{case}/{s.get('audio', 'audio_full_v1')}/{s['beat']}.wav"; vo = out.with_name(f"{s['name']}_vo.mp4"); dur = n / FPS
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out), "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", str(wav), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{dur:.3f}", str(vo)], check=True)
    print("wrote", out, n, "frames; marks", [(round(a + t0, 2), round(b + t0, 2)) for _, a, b in marks])


if __name__ == "__main__":
    main()
