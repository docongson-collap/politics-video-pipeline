#!/usr/bin/env python3
"""Channel name corner (owner 14/11: every finished Politics video carries the channel name TOP-LEFT, whole film).
usage: make_corner_logo.py <out.png> [W H]  -> transparent full-frame PNG to overlay at 0:0 for the whole film
Style = Travel's HT99 corner (tools in Travel/tools/make_corner_logo.py): 2-line heavy sans, white ~75%, soft dark halo so it
stays legible on bright footage. Channel name from docs/CHANNEL.md (channel name line)."""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

out = sys.argv[1]; W, H = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (1920, 1080)
import re as _re, pathlib as _pl
_name = _re.search(r"^Name: (.+?)\s*$", (_pl.Path(__file__).resolve().parents[1] / "docs/CHANNEL.md").read_text(), _re.M).group(1)
L1, L2 = _name.upper().split(" ", 1)
k = W / 1920; TOP = int(48 * k); LEFT = int(62 * k); CAP = int(38 * k); ALPHA = 200
f = None
for size in range(140, 10, -1):
    f = ImageFont.truetype("/Users/doson/Library/Fonts/Montserrat-ExtraBold.otf", size)
    if f.getbbox("H")[3] - f.getbbox("H")[1] <= CAP: break
asc = f.getbbox("H")[3] - f.getbbox("H")[1]; gap = int(asc * 0.5)
txt = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(txt)
for j, t in enumerate((L1, L2)):
    b = f.getbbox(t)
    d.text((LEFT - b[0], TOP + j * (asc + gap) - f.getbbox("H")[1]), t, font=f, fill=(255, 255, 255, ALPHA))
halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
halo.putalpha(txt.getchannel("A").filter(ImageFilter.MaxFilter(11)).filter(ImageFilter.GaussianBlur(10 * k)).point(lambda v: int(v * 0.8)))
im = Image.alpha_composite(halo, txt)
im.save(out); print(out, "font", size, "box", max(f.getbbox(t)[2] for t in (L1, L2)), "x", 2 * asc + gap)
