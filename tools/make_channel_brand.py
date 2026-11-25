#!/usr/bin/env python3
"""Proof Politics channel brand: logo 800x800 + banner 2560x1440 (+ safe-area preview, 88 px logo check).
usage: python3 tools/make_channel_brand.py  -> assets/brand/{logo.png,banner.png,banner_preview.png,logo_88.png}
Look: flat navy field, heavy sans wordmark (white PROOF, red POLITICS bar), faint ruled-document texture, spaced caps tagline.
No AI art. Name read from docs/CHANNEL.md (line "Name:")."""
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/brand"; OUT.mkdir(parents=True, exist_ok=True)
NAME = re.search(r"^Name: (.+?)\s*$", (ROOT / "docs/CHANNEL.md").read_text(), re.M).group(1)
W1, W2 = NAME.upper().split(" ", 1)
F = "/Users/doson/Library/Fonts/"
HEAVY, SANS = F + "Montserrat-ExtraBold.otf", F + "Inter-SemiBold.otf"
NAVY, RED, WHITE, PAPER = (11, 27, 58), (200, 30, 45), (255, 255, 255), (255, 255, 255, 14)


def fit(path, text, width):
    for s in range(600, 8, -2):
        f = ImageFont.truetype(path, s)
        b = f.getbbox(text)
        if b[2] - b[0] <= width:
            return f
    return f


def ruled(im, step, x0, x1):
    """faint ruled-paper lines = 'the document' motif."""
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for y in range(step, im.height, step):
        d.line([(x0, y), (x1, y)], fill=PAPER, width=max(1, step // 30))
    return Image.alpha_composite(im, ov)


def wordmark(d, cx, top, width, gap):
    """PROOF (white) above a red bar carrying POLITICS (white). Returns bottom y."""
    f1 = fit(HEAVY, W1, width)
    b1 = f1.getbbox(W1)
    d.text((cx - (b1[2] - b1[0]) / 2 - b1[0], top - b1[1]), W1, font=f1, fill=WHITE)
    y = top + (b1[3] - b1[1]) + gap
    f2 = fit(HEAVY, W2, width * 0.80)
    b2 = f2.getbbox(W2); h2 = b2[3] - b2[1]; pad = int(h2 * 0.32)
    d.rectangle([cx - width / 2, y, cx + width / 2, y + h2 + 2 * pad], fill=RED)
    d.text((cx - (b2[2] - b2[0]) / 2 - b2[0], y + pad - b2[1]), W2, font=f2, fill=WHITE)
    return y + h2 + 2 * pad


# logo: YouTube crops a circle, keep everything inside ~70% of the square
L = 800
logo = ruled(Image.new("RGBA", (L, L), NAVY + (255,)), 40, 0, L)
d = ImageDraw.Draw(logo)
LW = 610
f1 = fit(HEAVY, W1, LW); h1 = f1.getbbox(W1)[3] - f1.getbbox(W1)[1]
f2h = fit(HEAVY, W2, LW * 0.8).getbbox(W2); h2 = (f2h[3] - f2h[1]) * 1.64
gap = 26; top = (L - (h1 + gap + h2)) / 2
wordmark(d, L / 2, top, LW, gap)
logo.convert("RGB").save(OUT / "logo.png")
logo.convert("RGB").resize((88, 88), Image.LANCZOS).save(OUT / "logo_88.png")

# banner: all text inside the centre 1546x423 safe area
BW, BH, SW, SH = 2560, 1440, 1546, 423
ban = ruled(Image.new("RGBA", (BW, BH), NAVY + (255,)), 36, 0, BW)
d = ImageDraw.Draw(ban)
sx, sy = (BW - SW) / 2, (BH - SH) / 2
# thin red rules framing the band, full width (no text crossed)
d.rectangle([0, sy - 34, BW, sy - 28], fill=RED); d.rectangle([0, sy + SH + 28, BW, sy + SH + 34], fill=RED)
# wordmark left half of the safe area, tagline right half
wm_w = 600
f1 = fit(HEAVY, W1, wm_w); h1 = f1.getbbox(W1)[3] - f1.getbbox(W1)[1]
f2h = fit(HEAVY, W2, wm_w * 0.8).getbbox(W2); h2 = (f2h[3] - f2h[1]) * 1.64
g = 18; top = BH / 2 - (h1 + g + h2) / 2
wordmark(d, sx + 40 + wm_w / 2, top, wm_w, g)
tx = sx + 40 + wm_w + 90
d.line([(tx - 45, sy + 70), (tx - 45, sy + SH - 70)], fill=(255, 255, 255, 90), width=3)
lines = ["THE CLIP.", "THE DOCUMENT.", "THE NUMBER."]
ft = ImageFont.truetype(HEAVY, 74); fs = ImageFont.truetype(SANS, 34)
lh = 88; ty = BH / 2 - (len(lines) * lh + 60) / 2
for i, t in enumerate(lines):
    d.text((tx, ty + i * lh), t, font=ft, fill=RED if i == 2 else WHITE)
sub = " ".join("US POLITICS, WITH THE PROOF")
while d.textbbox((tx + 2, 0), sub, font=fs)[2] > sx + SW - 30:
    fs = ImageFont.truetype(SANS, fs.size - 1)
d.text((tx + 2, ty + len(lines) * lh + 18), sub, font=fs, fill=(205, 212, 228))
ban.convert("RGB").save(OUT / "banner.png", optimize=True)

pv = ban.convert("RGB").copy(); dim = Image.new("RGBA", (BW, BH), (0, 0, 0, 150))
ImageDraw.Draw(dim).rectangle([sx, sy, sx + SW, sy + SH], fill=(0, 0, 0, 0))
pv = Image.alpha_composite(pv.convert("RGBA"), dim).convert("RGB")
ImageDraw.Draw(pv).rectangle([sx, sy, sx + SW, sy + SH], outline=(0, 255, 0), width=3)
pv.resize((1280, 720)).save(OUT / "banner_preview.png")
print("ok", NAME, [p.name for p in sorted(OUT.glob("*.png"))])
