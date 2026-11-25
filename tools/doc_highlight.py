#!/usr/bin/env python3
"""Real document capture with highlight: find a phrase in a PDF (pdftotext -bbox-layout), render that page
(pdftoppm), paint a yellow marker under the phrase, and compose a 1920x1080 frame (page crop on a dark desk + source tag).
Usage: python3 tools/doc_highlight.py PDF "exact phrase" OUT.png --tag "Order Dismissing Action, D. Alaska, Nov 1 2026"
       [--page N] [--zoom 1.0]
The phrase must exist verbatim (whitespace/quotes normalised) or the tool exits non-zero: never fake a document line."""
import argparse, html, re, subprocess, sys, tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_R = "/System/Library/Fonts/Supplemental/Arial.ttf"


def norm(w):
    w = html.unescape(w).replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"[^\w']", "", w.lower())


def find(pdf, phrase, page=None):
    xml = subprocess.run(["pdftotext", "-bbox-layout", pdf, "-"], capture_output=True, text=True).stdout
    target = [norm(w) for w in phrase.split() if norm(w)]
    pages = re.findall(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', xml, re.S)
    for pi, (pw, ph, body) in enumerate(pages, 1):
        if page and pi != page:
            continue
        words = [(float(a), float(b), float(c), float(d), norm(t)) for a, b, c, d, t in
                 re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', body)]
        words = [w for w in words if w[4]]
        toks = [w[4] for w in words]
        for i in range(len(toks) - len(target) + 1):
            if toks[i:i + len(target)] == target:
                return pi, float(pw), float(ph), words[i:i + len(target)]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf"); ap.add_argument("phrase"); ap.add_argument("out")
    ap.add_argument("--tag", default=""); ap.add_argument("--page", type=int); ap.add_argument("--zoom", type=float, default=1.0)
    a = ap.parse_args()
    hit = find(a.pdf, a.phrase, a.page)
    if not hit:
        sys.exit(f"PHRASE NOT FOUND in {a.pdf}: {a.phrase!r}")
    pi, pw, ph, ws = hit
    dpi = 220
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["pdftoppm", "-r", str(dpi), "-f", str(pi), "-l", str(pi), "-png", a.pdf, f"{td}/p"], check=True)
        img = Image.open(next(Path(td).glob("p*.png"))).convert("RGB")
    s = img.width / pw
    hl = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(hl)
    lines = {}
    for x0, y0, x1, y1, _ in ws:
        key = round(y0)
        lines.setdefault(key, []).append((x0, y0, x1, y1))
    for ln in lines.values():
        x0 = min(b[0] for b in ln); x1 = max(b[2] for b in ln); y0 = min(b[1] for b in ln); y1 = max(b[3] for b in ln)
        d.rectangle([x0 * s - 6, y0 * s - 4, x1 * s + 6, y1 * s + 6], fill=(255, 221, 0, 120))
    img = Image.alpha_composite(img.convert("RGBA"), hl).convert("RGB")
    # crop: full page width, vertical window centred on the highlight
    cy = (min(w[1] for w in ws) + max(w[3] for w in ws)) / 2 * s
    cw = img.width * 0.86 / a.zoom; chh = cw * 0.62
    cx = img.width / 2
    top = max(0, min(img.height - chh, cy - chh / 2)); left = max(0, cx - cw / 2)
    crop = img.crop((int(left), int(top), int(left + cw), int(top + chh)))
    W, H = 1920, 1080
    bg = Image.new("RGB", (W, H), (18, 22, 30))
    g = ImageDraw.Draw(bg)
    for y in range(H):
        c = int(18 + 14 * y / H); g.line([(0, y), (W, y)], fill=(c, c + 4, c + 12))
    tw = 1500; th = int(crop.height * tw / crop.width)
    if th > 900:
        th = 900; tw = int(crop.width * th / crop.height)
    crop = crop.resize((tw, th), Image.LANCZOS)
    x = (W - tw) // 2; y = (H - th) // 2 - (25 if a.tag else 0)
    sh = Image.new("RGBA", (tw + 60, th + 60), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle([30, 30, tw + 30, th + 30], fill=(0, 0, 0, 170))
    sh = sh.filter(ImageFilter.GaussianBlur(18)); bg.paste(sh, (x - 30, y - 20), sh)
    bg.paste(crop, (x, y))
    if a.tag:
        f = ImageFont.truetype(FONT, 34)
        bw = g.textlength(a.tag, font=f) + 48
        g.rectangle([x, y + th + 18, x + bw, y + th + 74], fill=(200, 16, 46))
        g.text((x + 24, y + th + 28), a.tag, font=f, fill="white")
    bg.save(a.out)
    print(f"OK page {pi} -> {a.out}")


if __name__ == "__main__":
    main()
