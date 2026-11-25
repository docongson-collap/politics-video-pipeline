#!/usr/bin/env python3
"""blanche-huang-confession graphics (WO graphics 2026-11-25): shot-map WEBHEAD / POST / SPLIT / NUM / DOC rows
-> edit/seg/<seg>_<t0>.mp4 (1920x1080, 30 fps, duration = t1 - t0 + 0.2 s tail).

Plan (rows, captures, verbatim marks, spoken word times) lives in work/plan.py; captures in edit/cap/<key>.png + .json
(DOM / PDF text-layer rects in CSS px, DPR in the json). Every frame is the capture's own pixels: no typed text, no labels.

Look (must differ from trump-nvidia-huang, which used a left->right horizontal drift and a light-grey split backing):
  * WEBHEAD (page frames, tools/fx/capture_pass.py): slow PUSH-IN (frame 3.5 % wider -> 100 %) with a small upward rise;
  * POST / NUM / DOC: the real crop is laid as a paper card on a deep-navy backing ("world" png) and the camera rises
    onto it from below (card enters upward), then pushes in; consecutive rows on the same card continue the camera and
    keep earlier markers on;
  * SPLIT: navy backing, left pane (CNBC transcript, its marker already on) shifts left and dims to 60 % while the
    Bloomberg Law pane slides in from the right (as approved in the shot-map), whole composite pushes in slowly.
Markers = yellow multiply sweep, one strip per real text line, starting ON the first voiced word, ending on the last.
Frames never show the word "spy" (capture json 'avoid' rects): page frames are constrained away from them and every
rendered camera path is re-checked.
usage: build_graphics.py [--only B6_3.67,...] [--jobs 6] [--plan]
"""
import json, re, subprocess, sys, threading, traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

EDIT = Path(__file__).resolve().parent
CASE = EDIT.parent
ROOT = CASE.parents[1]
CAP, WORK = EDIT / "cap", EDIT / "work"
CROP = WORK / "crop"; CROP.mkdir(parents=True, exist_ok=True)
SPEC, SEG = EDIT / "spec", EDIT / "seg"
SPEC.mkdir(exist_ok=True); SEG.mkdir(exist_ok=True)
sys.path.insert(0, str(WORK))
import plan  # noqa: E402

CASE_ID = "blanche-huang-confession"
AUDIO = "audio_full_v1"
WORDS = json.load(open(CASE / AUDIO / "words.json"))
TAIL, FPS, W, H = 0.2, 30, 1920, 1080
YEL = np.array([1.0, 0.86, 0.2], np.float32)
NAVY0, NAVY1 = np.array([0.055, 0.075, 0.115], np.float32), np.array([0.105, 0.135, 0.19], np.float32)
INK_PX = 38                              # min output glyph-ink height (px) of a marked text line
GROUP_MAX_H = 560                        # marks further apart than this (CSS px) get their own frame + a camera move
PUSH, RISE = 1.035, 10.0                 # WEBHEAD camera: start frame width factor, start cy offset (CSS px, below)
MAX_PX = 20.0                            # max camera move per frame (output px) -> gfx_gate max_px <= 24


def nw(s):
    return re.sub(r"[^a-z0-9']", "", s.lower().replace("\u2019", "'"))


def row_name(r):
    return f"{r['seg']}_{r['t0']:.2f}"


def word_lead(seg, a):
    """word whose start is the closest at/before a (+ nth occurrence for capture_pass) and the lead a - start."""
    ws = WORDS[seg]
    c = [k for k in range(len(ws)) if ws[k]["s"] <= a + 0.03]
    i = max(c, key=lambda k: ws[k]["s"]) if c else 0
    w = ws[i]
    nth = sum(1 for x in ws[:i] if nw(x["w"]) == nw(w["w"]))
    return w, nth, round(a - w["s"], 3)


def lum(img):
    return np.asarray(img.convert("L"), np.float32)


PLAN_LOCK = threading.RLock()


def blank_rows(L, x0, x1, dpr=2):
    x0 = max(0, x0); x1 = min(L.shape[1] / dpr, x1)
    a = L[:, int(x0 * dpr):int(x1 * dpr)]
    dark = (a < 140).mean(1)
    return ((a.max(1) - a.min(1)) < 18) | (a.min(1) > 175) | (dark < 0.004) | (dark > 0.8)


def edge_ok(blank, y, dpr):
    a = int(y * dpr) - 6
    return 0 <= a and a + 12 <= len(blank) and blank[a:a + 12].all()


def column(L, rects, dpr=2, win=60):
    y0 = max(0, int((min(q[1] for q in rects) - win) * dpr)); y1 = int((max(q[3] for q in rects) + win) * dpr)
    a = L[y0:y1]
    xs = np.where((a.max(0) - a.min(0)) > 60)[0]
    l, r = int(min(q[0] for q in rects) * dpr), int(max(q[2] for q in rects) * dpr)
    while True:
        c = xs[(xs < l) & (xs >= l - 140)]
        if len(c) == 0: break
        l = c.min()
    while True:
        c = xs[(xs > r) & (xs <= r + 140)]
        if len(c) == 0: break
        r = c.max()
    return l / dpr, r / dpr


_CAPS = {}


def load_cap(key):
    if key not in _CAPS:
        j = json.load(open(CAP / f"{key}.json")); img = Image.open(CAP / f"{key}.png").convert("RGB")
        _CAPS[key] = (j, img, lum(img))
    return _CAPS[key]


def rects_of(j, phrase):
    for p, m in zip(j["phrases"], j["marks"]):
        if p == phrase or p.split("||")[-1] == phrase:
            if m:
                return m
    raise SystemExit(f"{j['key']}: phrase not on capture: {phrase!r}")


def bbox(rs):
    return [min(q[0] for q in rs), min(q[1] for q in rs), max(q[2] for q in rs), max(q[3] for q in rs)]


def ink_h(L, q, dpr=2):
    a = L[int(q[1] * dpr):int(q[3] * dpr), int(q[0] * dpr):int(q[2] * dpr)]
    if a.size == 0:
        return q[3] - q[1]
    d = np.abs(a - np.median(a)) > 60; r = np.where(d.mean(1) > 0.01)[0]
    return (r.max() - r.min()) / dpr if len(r) else q[3] - q[1]


def lum_mode(L, rs, dpr=2):
    v = float(np.mean([L[int(q[1] * dpr):int(q[3] * dpr), int(q[0] * dpr):int(q[2] * dpr)].mean() for q in rs])) / 255
    return "invert" if v < 0.45 else "multiply"


def avoid_of(j):
    return [a[:4] for a in j.get("avoid", [])]


def hits_avoid(j, x0, y0, x1, y1):
    return [a for a in avoid_of(j) if a[2] > x0 and a[0] < x1 and a[3] > y0 and a[1] < y1]


# ---------------------------------------------------------------- page frames (WEBHEAD) -> capture_pass
def frame_for(L, img, rs, dpr, read_rs, avoid, ylim=None):
    """readable 16:9 frame (CSS) around rects rs, edges in blank rows, never reaching an avoid rect (incl. push + rise)."""
    iw, ih = img.width / dpr, img.height / dpr
    bx = bbox(rs)
    c0, c1 = column(L, rs, dpr)
    w = min(max(c1 - c0 + 140, 640), 1180)
    hmin = min(ink_h(L, q, dpr) for q in read_rs)
    w = min(w, max(420, 1920 * hmin / INK_PX))
    w = max(w, c1 - c0 + 48)
    w = max(w, (bx[3] - bx[1] + 160) * 16 / 9, bx[2] - bx[0] + 80)
    w = min(w, iw)
    cx = (c0 + c1) / 2
    if bx[0] < cx - w / 2 + 20 or bx[2] > cx + w / 2 - 20:
        cx = (bx[0] + bx[2]) / 2
    cx = min(max(cx, w / 2), iw - w / 2)
    # vertical limits: page ends + avoid words inside the (pushed) x range
    lo, hi = 0.0, ih
    for a in avoid:
        if a[2] > cx - w * PUSH / 2 and a[0] < cx + w * PUSH / 2:
            if a[3] <= bx[1]: lo = max(lo, a[3] + 4)
            elif a[1] >= bx[3]: hi = min(hi, a[1] - 4)
            else: raise SystemExit(f"avoid word on the marked line band: {a}")
    if ylim:
        lo, hi = max(lo, ylim[0]), min(hi, ylim[1])
    # the start frame is PUSH x larger and RISE lower: keep both inside [lo, hi]
    def span(cy, w_):
        h_ = w_ * 9 / 16
        return min(cy - h_ / 2, cy + RISE - h_ * PUSH / 2), max(cy + h_ / 2, cy + RISE + h_ * PUSH / 2)
    wmin = max(bx[2] - bx[0] + 40, (bx[3] - bx[1] + 40) * 16 / 9)
    while w > wmin and span(0, w)[1] - span(0, w)[0] > hi - lo:
        w *= 0.98
    w = max(w, wmin)
    h = w * 9 / 16
    s0, s1 = span(0, w)
    cmin, cmax = lo - s0, hi - s1
    cy0 = (bx[1] + bx[3]) / 2
    if cmin > cmax:
        raise SystemExit(f"no room between avoid words: lo={lo} hi={hi} need={s1 - s0}")
    bl = blank_rows(L, cx - w / 2, cx + w / 2, dpr)
    blc = blank_rows(L, max(cx - w / 2, min(c0, bx[0]) - 8), min(cx + w / 2, max(c1, bx[2]) + 8), dpr)
    best, ok = min(max(cy0, cmin), cmax), False
    R = int(max(60, min(240, (h - (bx[3] - bx[1])) / 2 - 30)))
    for blank in (bl, blc):
        for d in sorted(range(-R, R + 1), key=abs):
            cy = cy0 + d
            if cy < cmin or cy > cmax: continue
            if cy - h / 2 < 0 or cy + h / 2 > ih: continue
            if edge_ok(blank, cy - h / 2, dpr) and edge_ok(blank, cy + h / 2, dpr):
                best, ok = cy, True; break
        if ok: break
    cy = best
    if ih >= h:
        cy = min(max(cy, h / 2), ih - h / 2)
    return {"cx": cx, "cy": cy, "w": w}, ok


def plan_capture(name, r):
    with PLAN_LOCK:
        return _plan_capture(name, r)


def _plan_capture(name, r):
    seg, t0, T1, key = r["seg"], r["t0"], r["t1"] + TAIL, r["cap"]
    j, img, L = load_cap(key); dpr = j.get("dpr", 2); av = avoid_of(j)
    mk = []
    for phrase, a, b in r["mk"]:
        rs = rects_of(j, phrase)
        a = max(a, t0 + 0.05)            # marker can't start before the row's first frame
        w0, nth, lead = word_lead(seg, a)
        mk.append({"phrase": phrase, "rects": rs, "word": w0["w"], "nth": nth, "lead": lead, "ta": a, "te": b})
    groups = []
    for m in mk:
        if groups and bbox(groups[-1]["rs"] + m["rects"])[3] - bbox(groups[-1]["rs"] + m["rects"])[1] <= GROUP_MAX_H:
            groups[-1]["rs"] += m["rects"]; groups[-1]["m"].append(m)
        else:
            groups.append({"rs": list(m["rects"]), "m": [m]})
    frames = []
    for g in groups:
        f, ok = frame_for(L, img, g["rs"], dpr, [q for m in g["m"] for q in m["rects"]], av, plan.YLIM.get(name))
        f["ok"] = ok; frames.append(f)
    # camera: push-in + small rise on every frame; a move between groups lands 0.1 s before the next marker
    shots = []
    f = frames[0]
    shots.append({"t": t0, "cx": f["cx"], "cy": f["cy"] + RISE, "w": f["w"] * PUSH})
    for gi in range(1, len(groups)):
        pf, f = frames[gi - 1], frames[gi]
        m1 = groups[gi]["m"][0]["ta"] - 0.1
        dist = max(abs(f["cy"] - pf["cy"]), abs(f["cx"] - pf["cx"])) * W / f["w"]
        mv = max(0.6, dist / (MAX_PX * FPS) * 1.9)           # smootherstep peak = 1.875 x mean speed
        m0 = max(shots[-1]["t"] + 0.3, m1 - mv)
        shots.append({"t": m0, "cx": pf["cx"], "cy": pf["cy"] + RISE * 0.3, "w": pf["w"] * (1 + (PUSH - 1) * 0.3)})
        shots.append({"t": m1, "cx": f["cx"], "cy": f["cy"] + RISE * 0.6, "w": f["w"] * (1 + (PUSH - 1) * 0.6), "lin": 1})
    shots[0]["lin"] = 1
    lf = frames[-1]
    shots.append({"t": T1, "cx": lf["cx"], "cy": lf["cy"], "w": lf["w"]})
    iw, ih = img.width / dpr, img.height / dpr
    X0 = int(max(0, min(s["cx"] - s["w"] / 2 for s in shots) - 40)); X1 = int(np.ceil(min(iw, max(s["cx"] + s["w"] / 2 for s in shots) + 40)))
    Y0 = int(max(0, min(s["cy"] - s["w"] * 9 / 32 for s in shots) - 40)); Y1 = int(np.ceil(min(ih, max(s["cy"] + s["w"] * 9 / 32 for s in shots) + 40)))
    # 'spy' rects that fall inside the crop band are painted over with the page ground; the camera never shows them
    crop = img.crop((X0 * dpr, Y0 * dpr, X1 * dpr, Y1 * dpr))
    cp = CROP / f"{name}.png"; crop.save(cp)
    cj = {"dpr": dpr, "src_png": str(CAP / f"{key}.png"), "offset_css": [X0, Y0], "phrases": [m["phrase"] for m in mk],
          "marks": [[[q[0] - X0, q[1] - Y0, q[2] - X0, q[3] - Y0] for q in m["rects"]] for m in mk]}
    json.dump(cj, open(CROP / f"{name}.json", "w"), indent=1)
    for s in shots:
        s["cx"] = round(s["cx"] - X0, 2); s["cy"] = round(s["cy"] - Y0, 2); s["w"] = round(s["w"], 2)
    smarks = []
    for i, m in enumerate(mk):
        dur = min(max(m["te"] - m["ta"], 0.3), max(0.25, T1 - m["ta"] - 0.1))
        smarks.append({"i": i, "word": m["word"], "nth": m["nth"], "lead": m["lead"], "dur": round(dur, 3),
                       "mode": lum_mode(L, m["rects"], dpr)})
    spec = {"name": name, "case": CASE_ID, "audio": AUDIO, "beat": seg, "t0": t0, "t1": round(T1, 3),
            "png": str(cp), "json": str(CROP / f"{name}.json"), "url": j["url"], "cap": key, "origin": j.get("origin", key),
            "via": j.get("via", "live"), "shotmap_line": r["line"], "kind": r["treat"], "pad": [5, 2], "shots": shots, "marks": smarks,
            "mark_times": [[round(m["ta"] - t0, 3), round(m["ta"] - t0 + d["dur"], 3)] for m, d in zip(mk, smarks)],
            "phrases": [m["phrase"].split("||")[-1].split("##")[0] for m in mk], "edges_snapped": all(f["ok"] for f in frames),
            "frames": len(frames), "frame_css_w": [round(f["w"], 1) for f in frames],
            "avoid_in_view": path_avoid(shots, av, X0, Y0, t0, T1)}
    json.dump(spec, open(SPEC / f"{name}.json", "w"), indent=1)
    return spec


def cam(shots, t):
    def ease(u):
        u = min(1.0, max(0.0, u)); return u * u * u * (u * (6 * u - 15) + 10)
    if t <= shots[0]["t"]: return shots[0]
    for a, b in zip(shots, shots[1:]):
        if t <= b["t"]:
            u = (t - a["t"]) / max(1e-6, b["t"] - a["t"]); e = u if a.get("lin") else ease(u)
            return {k: a[k] + (b[k] - a[k]) * e for k in ("cx", "cy", "w")}
    return shots[-1]


def path_avoid(shots, av, X0, Y0, t0, T1):
    """avoid rects (page CSS) visible at any frame of the camera path (shots in crop CSS)."""
    bad = []
    n = int(round((T1 - t0) * FPS))
    for f in range(n):
        c = cam(shots, t0 + f / FPS)
        x0, x1 = c["cx"] - c["w"] / 2 + X0, c["cx"] + c["w"] / 2 + X0
        y0, y1 = c["cy"] - c["w"] * 9 / 32 + Y0, c["cy"] + c["w"] * 9 / 32 + Y0
        for a in av:
            if a[2] > x0 and a[0] < x1 and a[3] > y0 and a[1] < y1 and a not in bad:
                bad.append(a)
    return bad


def run_capture_pass(spec):
    p = subprocess.run(["python3", str(ROOT / "tools/fx/capture_pass.py"), str(SPEC / f"{spec['name']}.json")], capture_output=True, text=True)
    return p.returncode, (p.stdout + p.stderr).strip()[-300:]


# ---------------------------------------------------------------- composites
def ease(u):
    u = min(1.0, max(0.0, u))
    return u * u * u * (u * (6 * u - 15) + 10)


def navy(w, h):
    g = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    return np.broadcast_to(NAVY0 * (1 - g) + NAVY1 * g, (h, w, 3)).copy()


def para_box(key, rs, gap=14, pad=22, x_pad=26):
    """paragraph around rects rs: expand up/down until a blank band >= gap CSS px; x = the text column."""
    j, img, L = load_cap(key); dpr = j.get("dpr", 2)
    c0, c1 = column(L, rs, dpr)
    b = bbox(rs)
    bl = blank_rows(L, c0 - x_pad, c1 + x_pad, dpr)     # whole card width: nothing half-cut at its top/bottom
    g, p = int(gap * dpr), int(pad * dpr)
    y = int(b[1] * dpr)
    while y > g and not bl[y - g:y].all(): y -= 1
    k = 0                                       # pad only through blank rows (never into the line above)
    while k < p and y - k - 1 >= 0 and bl[y - k - 1]: k += 1
    top = (y - max(0, k - 2 * dpr)) / dpr
    y = int(b[3] * dpr)
    while y + g < len(bl) and not bl[y:y + g].all(): y += 1
    k = 0
    while k < p and y + k < len(bl) and bl[y + k]: k += 1
    bot = (y + max(0, k - 2 * dpr)) / dpr
    return [max(0, c0 - x_pad), max(0, top), min(img.width / dpr, c1 + x_pad), min(img.height / dpr, bot)]


def snap_box(key, box):
    j, img, L = load_cap(key); dpr = j.get("dpr", 2); bl = blank_rows(L, box[0], box[2], dpr)
    def snap(y, d):
        for k in range(0, 60):
            if edge_ok(bl, y + d * k, dpr):
                return y + d * k
        return y
    return [box[0], snap(box[1], -1), box[2], snap(box[3], 1)]


class World:
    """navy backing + paper cards (real crops at the capture's native pixel scale); world px, dpr 1 for capture_pass."""

    def __init__(self, cards, gap=0.22, margin=0.75):
        self.cards = []
        dprs = set()
        for key, box in cards:
            j, img, L = load_cap(key); d = j.get("dpr", 2); dprs.add(d)
            assert not hits_avoid(j, *box), (key, box, hits_avoid(j, *box))
            c = img.crop((int(box[0] * d), int(box[1] * d), int(np.ceil(box[2] * d)), int(np.ceil(box[3] * d))))
            self.cards.append({"key": key, "box": box, "d": d, "img": c, "j": j})
        assert len(dprs) == 1
        cw = max(c["img"].width for c in self.cards); g = int(cw * gap)
        ch = sum(c["img"].height for c in self.cards) + g * (len(self.cards) - 1)
        mx, my = int(cw * margin), int(cw * margin * 0.75)
        self.w, self.h = cw + 2 * mx, ch + 2 * my
        base = navy(self.w, self.h)
        y = my
        sh = Image.new("L", (self.w, self.h), 0); dr = ImageDraw.Draw(sh)
        for c in self.cards:
            c["ox"], c["oy"] = (self.w - c["img"].width) // 2, y
            dr.rectangle([c["ox"] + 6, c["oy"] + 18, c["ox"] + c["img"].width + 6, c["oy"] + c["img"].height + 18], fill=255)
            y += c["img"].height + g
        m = np.asarray(sh.filter(ImageFilter.GaussianBlur(28)), np.float32)[..., None] / 255 * 0.55
        base *= (1 - m)
        for c in self.cards:
            a = np.asarray(c["img"], np.float32) / 255
            base[c["oy"]:c["oy"] + a.shape[0], c["ox"]:c["ox"] + a.shape[1]] = a
        self.base = base

    def card(self, key, i=None):
        cs = [c for c in self.cards if c["key"] == key]
        return cs[i or 0]

    def rects(self, key, phrase, ci=0):
        c = [x for x in self.cards if x["key"] == key][ci]
        rs = rects_of(c["j"], phrase); d = c["d"]; b = c["box"]
        out = [[(q[0] - b[0]) * d + c["ox"], (q[1] - b[1]) * d + c["oy"], (q[2] - b[0]) * d + c["ox"], (q[3] - b[1]) * d + c["oy"]] for q in rs]
        for q in out:
            assert c["ox"] <= q[0] and q[2] <= c["ox"] + c["img"].width and c["oy"] <= q[1] and q[3] <= c["oy"] + c["img"].height, (key, phrase)
        return out

    def bake(self, rects, pad=(5, 2)):
        """earlier rows' markers: fully on (multiply)."""
        d = self.cards[0]["d"] / 2
        for q in rects:
            x0, y0 = int((q[0] - pad[0] * d)), int((q[1] - pad[1] * d)); x1, y1 = int(np.ceil(q[2] + pad[0] * d)), int(np.ceil(q[3] + pad[1] * d))
            self.base[y0:y1, x0:x1] *= YEL

    def card_rect(self, i=0):
        c = self.cards[i]
        return [c["ox"], c["oy"], c["ox"] + c["img"].width, c["oy"] + c["img"].height]


def view_w(roi, fill=0.86):
    """world-px view width so the roi fills `fill` of the frame width (or 80 % of the height)."""
    return max((roi[2] - roi[0]) / fill, (roi[3] - roi[1]) / 0.8 * 16 / 9)


def world_spec(name, r, world, marks, shots, extra=None):
    """write world png/json and a capture_pass spec (dpr 1 = world px). marks: [(phrase, key, rects, a, b)]"""
    seg, t0, T1 = r["seg"], r["t0"], r["t1"] + TAIL
    cp = CROP / f"{name}.png"
    Image.fromarray((np.clip(world.base, 0, 1) * 255).astype(np.uint8)).save(cp)
    cj = {"dpr": 1, "world": True, "phrases": [m[0] for m in marks], "marks": [m[2] for m in marks]}
    json.dump(cj, open(CROP / f"{name}.json", "w"), indent=1)
    smarks = []
    for i, (ph, key, rs, a, b) in enumerate(marks):
        a = max(a, t0 + 0.05)
        w0, nth, lead = word_lead(seg, a)
        dur = min(max(b - a, 0.3), max(0.25, T1 - a - 0.1))
        smarks.append({"i": i, "word": w0["w"], "nth": nth, "lead": lead, "dur": round(dur, 3), "mode": "multiply", "_a": a})
    # every view must stay inside the world (no white fill)
    for f in range(int(round((T1 - t0) * FPS))):
        c = cam(shots, t0 + f / FPS)
        assert c["cx"] - c["w"] / 2 >= 0 and c["cx"] + c["w"] / 2 <= world.w and c["cy"] - c["w"] * 9 / 32 >= 0 and c["cy"] + c["w"] * 9 / 32 <= world.h, (name, f, c, world.w, world.h)
    caps = []
    for c in world.cards:
        if c["key"] not in [x["cap"] for x in caps]:
            caps.append({"cap": c["key"], "url": c["j"]["url"], "box_css": [round(v, 1) for v in c["box"]], "origin": c["j"].get("origin", c["key"]), "via": c["j"].get("via", "live")})
    spec = {"name": name, "case": CASE_ID, "audio": AUDIO, "beat": seg, "t0": t0, "t1": round(T1, 3), "png": str(cp),
            "json": str(CROP / f"{name}.json"), "cap": "+".join(dict.fromkeys(c["key"] for c in world.cards)), "cards": caps,
            "url": caps[0]["url"], "shotmap_line": r["line"], "kind": r["treat"], "pad": [5 * world.cards[0]["d"] / 2, 2 * world.cards[0]["d"] / 2],
            "shots": [{k: (round(v, 2) if isinstance(v, float) else v) for k, v in s.items()} for s in shots],
            "marks": [{k: v for k, v in m.items() if not k.startswith("_")} for m in smarks],
            "mark_times": [[round(m["_a"] - t0, 3), round(m["_a"] - t0 + m["dur"], 3)] for m in smarks],
            "phrases": [m[0].split("||")[-1].split("##")[0] for m in marks], "edges_snapped": True}
    if extra: spec.update(extra)
    json.dump(spec, open(SPEC / f"{name}.json", "w"), indent=1)
    return spec


def rise_shots(t0, T1, roi, w_end_f=0.965, enter=True, start=None, ta=None):
    """camera onto roi: enters rising from below (card moves up into frame) then pushes in to w*w_end_f."""
    w = view_w(roi); cx, cy = (roi[0] + roi[2]) / 2, (roi[1] + roi[3]) / 2
    if start:
        s0 = dict(start, t=t0)
    elif enter:
        s0 = {"t": t0, "cx": cx, "cy": cy - 0.085 * w * 9 / 16, "w": w * 1.03, "lin": 1}   # constant-speed rise (cut-in)
    else:
        s0 = {"t": t0, "cx": cx, "cy": cy, "w": w * 1.03}
    shots = [s0]
    t_in = t0 + min(1.0, max(0.4, (T1 - t0) * 0.75))           # visible move >= 0.6 s unless the row is very short
    if s0["cy"] != cy or s0["cx"] != cx or abs(s0["w"] - w) > 1:
        shots.append({"t": t_in, "cx": cx, "cy": cy, "w": w, "lin": 1})
    else:
        shots[0]["lin"] = 1
    shots.append({"t": T1, "cx": cx, "cy": cy, "w": w * w_end_f})
    return shots


# per-card row builders ------------------------------------------------------
def T(r):
    return r["t0"], r["t1"] + TAIL


def mk_of(r):
    return r["mk"]


JS_BOX = [128, 56, 1096, 0]       # JSPDF_p1 card (CSS); bottom snapped below the 'update ...' paragraph


def doc_world():
    j, img, L = load_cap("JSPDF_p1")
    rs = rects_of(j, "update on the investigation of the Singaporean company Megaspeed")
    pb = para_box("JSPDF_p1", rs, gap=10)
    box = snap_box("JSPDF_p1", [JS_BOX[0], JS_BOX[1], JS_BOX[2], pb[3]])
    return World([("JSPDF_p1", box)])


def build_doc(r, rows_same):
    name = row_name(r); t0, T1 = T(r)
    wd = doc_world()
    idx = [x["t0"] for x in rows_same].index(r["t0"])
    marks = [(ph, "JSPDF_p1", wd.rects("JSPDF_p1", ph), a, b) for ph, a, b in r["mk"]]
    card = wd.card_rect()
    top = [card[0], card[1], card[2], wd.rects("JSPDF_p1", "November 16, 2026")[0][3] + 40]
    para = [card[0], wd.rects("JSPDF_p1", JS_TITLE_PH)[0][1] - 40, card[2], card[3]]
    if idx == 0:
        shots = rise_shots(t0, T1, top, ta=marks[0][3], w_end_f=0.975)
    else:
        for x in rows_same[:idx]:
            for ph, a, b in x["mk"]:
                wd.bake(wd.rects("JSPDF_p1", ph))
        prev = rise_shots(rows_same[idx - 1]["t0"], rows_same[idx - 1]["t1"] + TAIL, top, w_end_f=0.975)[-1]
        ta = marks[0][3]
        w = view_w(para); cx, cy = (para[0] + para[2]) / 2, (para[1] + para[3]) / 2
        m1 = ta - 0.15; m0 = max(t0 + 0.2, m1 - 1.4)
        shots = [dict(prev, t=t0), dict(prev, t=m0, w=prev["w"] * 0.995), {"t": m1, "cx": cx, "cy": cy, "w": w, "lin": 1},
                 {"t": T1, "cx": cx, "cy": cy, "w": w * 0.975}]
    return world_spec(name, r, wd, marks, shots)


JS_TITLE_PH = "JOINT STATEMENT FROM DEPARTMENT OF COMMERCE AND DEPARTMENT OF JUSTICE ON MEGASPEED INVESTIGATION"


def post_world():
    return World([("XSCH", [0, 0, 560, 278])])


def build_post(r, rows_same):
    name = row_name(r); t0, T1 = T(r)
    wd = post_world()
    idx = [x["t0"] for x in rows_same].index(r["t0"])
    for x in rows_same[:idx]:
        for ph, a, b in x["mk"]:
            wd.bake(wd.rects("XSCH", ph))
    marks = [(ph, "XSCH", wd.rects("XSCH", ph), a, b) for ph, a, b in r["mk"]]
    card = wd.card_rect()
    if idx == 0:
        shots = rise_shots(t0, T1, card, ta=marks[0][3], w_end_f=0.975)
    else:
        prev = rise_shots(rows_same[idx - 1]["t0"], rows_same[idx - 1]["t1"] + TAIL, card, w_end_f=0.975)[-1]
        # continue the push toward the quote body (header stays in frame)
        body = [card[0], card[1], card[2], card[3]]
        w = view_w(body) * 0.94; cx, cy = (body[0] + body[2]) / 2, (body[1] + body[3]) / 2 + 20
        shots = [dict(prev, t=t0, lin=1), {"t": T1, "cx": cx, "cy": cy, "w": w}]
    return world_spec(name, r, wd, marks, shots)


def num_cards(phrase):
    j, img, L = load_cap("CNBC1116_N")
    rs = rects_of(j, phrase)
    return para_box("CNBC1116_N", rs, gap=14)


def build_num(r, rows_same):
    """NUM: the real CNBC paragraph that holds the figure, as a card; rows 2+3 share a world of two stacked cards and the
    camera rises from the first card to the second."""
    name = row_name(r); t0, T1 = T(r)
    ph0 = r["mk"][0][0]
    if "103" in ph0:
        wd = World([("CNBC1116_N", num_cards(ph0))])
        marks = [(ph, "CNBC1116_N", wd.rects("CNBC1116_N", ph), a, b) for ph, a, b in r["mk"]]
        shots = rise_shots(t0, T1, wd.card_rect(), ta=marks[0][3], w_end_f=0.96)
        return world_spec(name, r, wd, marks, shots)
    # $12.5M-$58M and 'broad dollar ranges' rows: each its own real paragraph card (stacking both put a half card at the
    # frame edge); the cut between the two clips is the move
    wd = World([("CNBC1116_N", num_cards(ph0))])
    marks = [(ph, "CNBC1116_N", wd.rects("CNBC1116_N", ph), a, b) for ph, a, b in r["mk"]]
    shots = rise_shots(t0, T1, wd.card_rect(), ta=marks[0][3], w_end_f=0.965)
    return world_spec(name, r, wd, marks, shots)


# ---------------------------------------------------------------- SPLIT (custom frames)
def encoder(out):
    return subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                             "-c:v", "h264_videotoolbox", "-q:v", "72", "-allow_sw", "0", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)],
                            stdin=subprocess.PIPE)


class Pane:
    """vertical stack of real crops (CSS boxes of one capture) on its own page ground, native px; marks in pane px."""

    def __init__(self, key, boxes, gap=26):
        j, img, L = load_cap(key); d = j.get("dpr", 2); self.key, self.j, self.d = key, j, d
        for b in boxes:
            assert not hits_avoid(j, *b), (key, b)
        crops = [img.crop((int(b[0] * d), int(b[1] * d), int(np.ceil(b[2] * d)), int(np.ceil(b[3] * d)))) for b in boxes]
        w = max(c.width for c in crops); h = sum(c.height for c in crops) + int(gap * d) * (len(crops) - 1)
        self.base = np.ones((h, w, 3), np.float32)
        self.offs = []; y = 0
        for b, c in zip(boxes, crops):
            a = np.asarray(c, np.float32) / 255
            self.base[y:y + a.shape[0], 0:a.shape[1]] = a; self.offs.append((b, y)); y += a.shape[0] + int(gap * d)
        self.marks = []          # (x0,y0,x1,y1 px, ta, tb)
        self.boxes = boxes

    def rects(self, phrase):
        rs = rects_of(self.j, phrase)
        for b, y in self.offs:
            if all(b[1] <= q[1] and q[3] <= b[3] for q in rs):
                return [[(q[0] - b[0]) * self.d, (q[1] - b[1]) * self.d + y, (q[2] - b[0]) * self.d, (q[3] - b[1]) * self.d + y] for q in rs]
        raise SystemExit(f"{self.key}: {phrase!r} not inside pane boxes")

    def add_mark(self, phrase, ta, tb):
        rs = self.rects(phrase); tot = sum(q[2] - q[0] for q in rs); acc = 0
        px, py = 5 * self.d / 2, 2 * self.d / 2
        for q in rs:
            w = q[2] - q[0]
            self.marks.append((q[0] - px, q[1] - py, q[2] + px, q[3] + py, ta + (tb - ta) * acc / tot, ta + (tb - ta) * (acc + w) / tot)); acc += w

    def at(self, t):
        p = self.base.copy()
        for x0, y0, x1, y1, a, b in self.marks:
            if t <= a: continue
            u = ease((t - a) / max(1e-3, b - a)); xe = x0 + (x1 - x0) * u
            xi0, xi1, yi0, yi1 = int(x0), int(np.ceil(xe)), int(round(y0)), int(round(y1))
            if xi1 > xi0: p[yi0:yi1, xi0:xi1] *= YEL
        return p


def split_panes():
    jl, _, _ = load_cap("CNBCT_S"); jr, _, _ = load_cap("BLAW_S")
    q_ex = "They did a pretty good investigation, and they felt that he himself was was exonerated."
    hl = rects_of(jl, jl["h1"]); ex = rects_of(jl, q_ex)
    lb = [snap_box("CNBCT_S", [6, bbox(hl)[1] - 50, 474, bbox(hl)[3] + 46]), para_box("CNBCT_S", ex, gap=12, pad=14, x_pad=15)]
    lb[1][0], lb[1][2] = 6, 474
    hr = rects_of(jr, jr["h1"]); qt = rects_of(jr, "That assumes there is an investigation that's open, and that's never been discussed publicly")
    fox = rects_of(jr, "when asked if an investigation into Jensen Huang is closed")
    rb = [[6, 120, 474, 152], snap_box("BLAW_S", [6, bbox(hr)[1] - 16, 474, bbox(hr)[3] + 30]),
          snap_box("BLAW_S", [6, bbox(qt)[1] - 14, 474, bbox(fox)[3] + 14])]
    return Pane("CNBCT_S", lb), Pane("BLAW_S", rb), q_ex


def build_split(r, rows_same):
    name = row_name(r); t0, T1 = T(r)
    idx = [x["t0"] for x in rows_same].index(r["t0"])
    L, R, q_ex = split_panes()
    L.add_mark(q_ex, -10, -9.9)                                   # recalled line: marker already on
    for x in rows_same[:idx]:
        for ph, a, b in x["mk"]:
            R.add_mark(ph, -10, -9.9)
    for ph, a, b in r["mk"]:
        R.add_mark(ph, a - t0, b - t0)
    bg = navy(W, H)
    PW = 860                                                        # pane width on screen (split)
    sl, sr = PW / L.base.shape[1], PW / R.base.shape[1]
    s_solo = min(1080 * 0.82 / L.base.shape[0], 1240 / L.base.shape[1])
    def shadow(c, x, y, w, h, a=0.5):
        m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rectangle([x + 4, y + 14, x + w + 4, y + h + 14], fill=255)
        c *= 1 - np.asarray(m.filter(ImageFilter.GaussianBlur(22)), np.float32)[..., None] / 255 * a
    def place(c, arr, s, x, y, dim=1.0):
        im = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))
        w, h = max(1, int(round(arr.shape[1] * s))), max(1, int(round(arr.shape[0] * s)))
        a = np.asarray(im.resize((w, h), Image.LANCZOS), np.float32) / 255 * dim
        shadow(c, x, y, w, h)
        xi, yi = int(round(x)), int(round(y))
        X0, Y0, X1, Y1 = max(0, xi), max(0, yi), min(W, xi + w), min(H, yi + h)
        if X1 > X0 and Y1 > Y0:
            c[Y0:Y1, X0:X1] = a[Y0 - yi:Y1 - yi, X0 - xi:X1 - xi]
    gapx = (W - 2 * PW) / 3
    lx1, rx1 = gapx, 2 * gapx + PW
    def fr(t):
        c = bg.copy()
        tt = t + t0
        if idx == 0:
            u = ease(t / 0.4)                                       # frame divides in 0.4 s
            s = s_solo + (sl - s_solo) * u
            lw = L.base.shape[1] * s; lh = L.base.shape[0] * s
            lx = (W - lw) / 2 + (lx1 - (W - lw) / 2) * u; ly = (H - lh) / 2
            dim = 1 - 0.4 * u
            rx = W + 40 + (rx1 - W - 40) * u
        else:
            u = ease(t / 0.4)
            s = sl; lw, lh = L.base.shape[1] * s, L.base.shape[0] * s; lx, ly = lx1, (H - lh) / 2
            dim = 0.6 + 0.4 * u                                     # END: both panes at 100 %
            rx = rx1
        push = 1 + 0.02 * (tt - rows_same[0]["t0"]) / (rows_same[-1]["t1"] - rows_same[0]["t0"])
        place(c, L.at(t), s * push, lx - (push - 1) * lw / 2, ly - (push - 1) * lh / 2, dim)
        rh = R.base.shape[0] * sr; rw = R.base.shape[1] * sr
        if rx < W:
            place(c, R.at(t), sr * push, rx - (push - 1) * rw / 2, (H - rh) / 2 - (push - 1) * rh / 2)
        return c
    out = SEG / f"{name}.mp4"
    ff = encoder(out)
    n = int(round((T1 - t0) * FPS))
    for f in range(n):
        ff.stdin.write((np.clip(fr(f / FPS), 0, 1) * 255).astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait()
    spec = {"name": name, "kind": "SPLIT", "beat": r["seg"], "t0": t0, "t1": round(T1, 3), "shotmap_line": r["line"],
            "cap": "CNBCT_S+BLAW_S", "url": R.j["url"],
            "panes": [{"cap": "CNBCT_S", "url": L.j["url"], "boxes_css": L.boxes, "marker_on": q_ex},
                      {"cap": "BLAW_S", "url": R.j["url"], "boxes_css": R.boxes}],
            "phrases": [ph for ph, a, b in r["mk"]], "mark_times": [[round(a - t0, 3), round(b - t0, 3)] for ph, a, b in r["mk"]],
            "screen_scale": {"left": round(sl, 3), "right": round(sr, 3)}}
    json.dump(spec, open(SPEC / f"{name}.json", "w"), indent=1)
    return ff.returncode, spec


# ---------------------------------------------------------------- driver
def same_rows(r):
    return [x for x in plan.ROWS if x["treat"] == r["treat"] and x["seg"] == r["seg"] and
            (x["treat"] != "NUM" or ("103" in x["mk"][0][0]) == ("103" in r["mk"][0][0]))]


def build_card(r, key, box):
    """page frame that cannot be a clean 16:9 window of the page ('spy' word, empty ad slot, page end or a black player
    right next to the marked lines): the real page block(s) as card(s) on the navy backing. box = CSS box, None (= the
    paragraph of the first mark) or a list of boxes (page order, stacked); the camera rises onto the card of the first
    mark, then travels to the card of each later mark so it lands 0.15 s before that mark starts."""
    name = row_name(r); t0, T1 = T(r)
    boxes = box if isinstance(box, list) and box and isinstance(box[0], list) else [box]
    boxes = [para_box(key, rects_of(load_cap(key)[0], r["mk"][0][0]), gap=14) if b is None else snap_box(key, b) for b in boxes]
    wd = World([(key, b) for b in boxes], gap=0.06)
    marks, cards = [], []
    for ph, a, b in r["mk"]:
        for ci in range(len(boxes)):
            try:
                rs = wd.rects(key, ph, ci); break
            except (AssertionError, SystemExit):
                continue
        else:
            raise SystemExit(f"{name}: {ph!r} not inside any card")
        marks.append((ph, key, rs, a, b)); cards.append(ci)
    up = any(c < cards[0] for c in cards)            # travelling up to an earlier card: no upward entry (no reversal)
    shots = rise_shots(t0, T1, wd.card_rect(cards[0]), ta=marks[0][3], w_end_f=0.965, enter=not up)
    for i in range(1, len(marks)):
        if cards[i] == cards[i - 1]:
            continue
        C = wd.card_rect(cards[i]); w = view_w(C); cx, cy = (C[0] + C[2]) / 2, (C[1] + C[3]) / 2
        prev = cam(shots, marks[i - 1][4] + 0.15)
        m1 = marks[i][3] - 0.15
        dist = max(abs(cy - prev["cy"]), abs(cx - prev["cx"])) * W / w
        m0 = max(marks[i - 1][4] + 0.15, m1 - max(0.8, dist / (MAX_PX * FPS) * 1.9))
        shots = [s_ for s_ in shots if s_["t"] < m0]
        shots += [dict(prev, t=m0, lin=0), {"t": m1, "cx": cx, "cy": cy, "w": w, "lin": 1}, {"t": T1, "cx": cx, "cy": cy, "w": w * 0.975}]
    return world_spec(name, r, wd, marks, shots, {"card_box_css": boxes})


def make_spec(r):
    name = row_name(r)
    if name in getattr(plan, "CARD", {}): return build_card(r, *plan.CARD[name])
    if r["treat"] == "DOC": return build_doc(r, same_rows(r))
    if r["treat"] == "POST": return build_post(r, same_rows(r))
    if r["treat"] == "NUM": return build_num(r, same_rows(r))
    return plan_capture(name, r)


def job(r):
    name = row_name(r)
    try:
        if r["treat"] == "SPLIT":
            rc, s = build_split(r, same_rows(r)); return name, rc, ""
        s = make_spec(r)
        if s.get("avoid_in_view"):
            return name, 1, f"avoid word in view: {s['avoid_in_view']}"
        rc, msg = run_capture_pass(s)
        return name, rc, msg
    except BaseException:
        return name, 1, traceback.format_exc()[-900:]


def main():
    a = sys.argv[1:]
    only = set(a[a.index("--only") + 1].split(",")) if "--only" in a else None
    jobs = int(a[a.index("--jobs") + 1]) if "--jobs" in a else 6
    rows = [r for r in plan.ROWS if not only or row_name(r) in only]
    if "--plan" in a:
        for r in rows:
            if r["treat"] == "SPLIT":
                print(row_name(r), "SPLIT (custom frames)"); continue
            try:
                s = make_spec(r)
                print(f"{s['name']:10s} {s['cap']:12s} {s.get('kind')} frames={s.get('frames', 1)} w={s.get('frame_css_w', '-')} "
                      f"snap={s['edges_snapped']} marks={s['mark_times']} avoid={s.get('avoid_in_view', [])}")
            except BaseException:
                print(row_name(r), "PLAN FAIL", traceback.format_exc()[-400:])
        return
    with ThreadPoolExecutor(jobs) as ex:
        for name, rc, msg in ex.map(job, rows):
            print(name, "OK" if rc == 0 else "FAIL", "" if rc == 0 else msg, flush=True)


if __name__ == "__main__":
    main()
