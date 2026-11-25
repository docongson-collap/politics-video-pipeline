#!/usr/bin/env python3
"""Full v1 assembly, driven by edit/shotmap_v1.tsv (film_t0 = absolute time already computed there).
Copied from cases/trump-nvidia-huang/edit/full_v1.py (WO blanche-huang-confession-builder.md) and adapted:
  - audio_full_v1 (not v2), shotmap_v1.tsv / edit_plan_v1.json / graphics_index.tsv for this case.
  - src cells reference three roots: local assets/clips (this case), cross-case footage/envato
    under ../trump-nvidia-huang/assets/..., and shared stock under ../../kho/stock/... -- all resolved
    the same way, relative to CASE, since the shotmap src strings are already written relative to
    edit/../ (i.e. CASE).
  - shotmap_v1.tsv has embedded literal quote characters (burned quotes in several B-rows) so the TSV
    must be read with quoting=csv.QUOTE_NONE, or csv.reader's default quoting silently merges rows
    across the embedded quotes.
  - whole-film corner logo overlay (assets/brand/corner_1920.png, already 1920x1080 with transparency)
    baked in at the final video+audio mux (WO step 1 point: "logo overlay ... if not done in step 1").
  - no lower-third cards / top-left labels (same minimalist look as trump-nvidia-huang).

Row kinds (shotmap 'treatment' column):
  FOOT-EVT / FOOT-LOC / FOOT-SCN / FOOT-GFX -> footage cut from assets/clips (local or
                     ../trump-nvidia-huang/assets/clips), Envato (local or cross-case
                     assets/envato/<uuid>.<ext>), or kho/stock; "FOOT-GFX" rows are footage where the
                     headline/graphic card is already burned into the source clip (outlet on-air
                     graphic), not a built graphic.
  CLIP (seg K1-K9)  -> exact edit_plan window, ORIGINAL audio (not VO), bug kept, no cards/labels.
  anything else (WEBHEAD/DOC/SPLIT/NUM/POST) -> graphic row; looked up by (seg, t0) in
                     edit/graphics_index.tsv -> edit/seg/<seg>_<t0>.mp4 (NOT the *_vo.mp4 previews);
                     missing -> black placeholder labelled with the row id, so footage can still be
                     cached with --partial.

Out: output/blanche-huang-confession-v1_nocap.mp4, edit/full_shots_v1.tsv
"""
import csv, glob, json, os, re, subprocess, sys, tempfile
from pathlib import Path

CASE = Path(__file__).resolve().parents[1]
ROOT = CASE.parents[1]
E = CASE / "edit"; SEG = E / "fseg"; SEG.mkdir(exist_ok=True)
QC = E / "qc"; QC.mkdir(exist_ok=True)
FPS = 30
AUD = CASE / "audio_full_v1"
GRAPHICS_IDX = E / "graphics_index.tsv"
OUT_NOCAP = ROOT / "output/blanche-huang-confession-v1_nocap.mp4"
LOGO = ROOT / "assets/brand/corner_1920.png"

# ---------- shotmap parsing ----------

def load_shotmap():
    rows = []
    with open(E / "shotmap_v1.tsv") as f:
        rd = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)  # embedded quote chars in rights notes
        header = next(rd)
        for r in rd:
            if not r or r[0].startswith("#"):
                continue
            seg, t0, t1, words, treat, src, tos, rights, match, film_t0 = r[:10]
            rows.append({
                "seg": seg, "t0": float(t0), "t1": float(t1), "words": words, "treat": treat,
                "src": src, "tos": tos, "rights": rights, "match": match, "film_t0": float(film_t0),
            })
    return rows


def beat_order(rows):
    order = []
    for r in rows:
        if not order or order[-1] != r["seg"]:
            order.append(r["seg"])
    return order


MMSS = re.compile(r"@(\d+):(\d+(?:\.\d+)?)-(\d+):(\d+(?:\.\d+)?)")


def resolve_foot(src):
    """-> (path:Path, off:float, dur:float, crop:str|None). v1 src cells are '<path> @mm:ss-mm:ss',
    where <path> is written relative to CASE (local assets/clips, cross-case
    ../trump-nvidia-huang/assets/..., or shared ../../kho/stock/...)."""
    m = MMSS.search(src)
    if not m:
        sys.exit(f"cannot parse src window: {src}")
    mm0, ss0, mm1, ss1 = m.groups()
    a = int(mm0) * 60 + float(ss0); b = int(mm1) * 60 + float(ss1)
    path_part = src[: src.index("@")].strip()
    if "assets/envato/" in path_part:
        # shot-map says .mov but some uuids were downloaded as .mp4; resolve by uuid stem, in
        # whichever envato dir the path_part points to (local or cross-case).
        envato_dir = (CASE / path_part).resolve().parent
        stem = Path(path_part).stem
        cands = [c for c in glob.glob(str(envato_dir / f"{stem}.*")) if not c.endswith((".pdf", ".log", ".zip"))]
        if not cands:
            sys.exit(f"envato uuid not found on disk: {stem}")
        p = Path(cands[0])
    else:
        p = (CASE / path_part).resolve()
    return p, a, b - a, None


# shotmap_v1.tsv flags this source's burned Fox chyron as editorializing ("DOJ ON NVIDIA 'SPY'
# SCANDAL...", wording not on tape -- confirmed on screen at this case's own 57-60.4s window, not
# only the 72-132s/240s+ ranges the research note estimated) on every row that uses it; every row's
# rights note says "mask that chyron text line only (bug stays)". Box in final 1920x1080 frame space
# (after scale/crop-to-fill), covers just the white headline text block, not the Fox bug (x<190) or
# the "TODD BLANCHE | ATTORNEY GENERAL" name strap above it (on-tape, not edited).
MASK_SOURCES = {}
# QC 13:30 (orchestrator): black mask box looked broken -> crop the Fox frame above the chyron and below the
# network time bug (which also collided with our corner logo). Source 1280x720: chyron starts y 535, bug ends y 92.
CROP_SOURCES = {"foxnews_6408836632112.mp4": "crop=iw*0.61:ih*0.61:iw*0.17:ih*0.13",
                "TC-axC1IL00.mp4": "crop=1778:1000:71:0"}  # CBS: drop the bottom HEADLINES ticker (unrelated 'spying' story); bug + chyron kept


def resolve_mask(p):
    return MASK_SOURCES.get(p.name)


def resolve_clip(src):
    """CLIP row: 'assets/clips/<id>.mp4 @MM:SS.s-MM:SS.s' -> (path, off, dur)"""
    m = MMSS.search(src)
    path_part = src[: src.index("@")].strip()
    p = CASE / path_part
    mm0, ss0, mm1, ss1 = m.groups()
    a = int(mm0) * 60 + float(ss0); b = int(mm1) * 60 + float(ss1)
    return p, a, b - a


FFMPEG = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"  # has zscale (needed for 10-bit Envato 4K sources)


def fps_of(src):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=r_frame_rate", "-of", "csv=p=0", str(src)],
                       capture_output=True, text=True).stdout.strip().split("/")
    return float(r[0]) / float(r[1] if len(r) > 1 else 1)


def video_filter(src, crop=None, force_pad=False, zscale=False, mask=None):
    norm = "zscale=tin=709:min=709:pin=709:t=709:m=709:r=full,format=yuv420p," if zscale else "format=yuv420p,"
    base = "setpts=PTS-STARTPTS," + norm + (crop + "," if crop else "") + \
        "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
    sfps = fps_of(src)
    base += ("minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,"
             if min(abs(sfps - 30), abs(sfps - 60)) > 0.5 else "fps=30,")
    if force_pad:
        base += "tpad=stop_mode=clone:stop_duration=0.2,"
    if mask:
        x, y, w, h = mask
        base += f"drawbox=x={x}:y={y}:w={w}:h={h}:color=black:t=fill,"
    return base + "setsar=1,format=yuv420p"


from concurrent.futures import ThreadPoolExecutor
POOL = ThreadPoolExecutor(max_workers=int(os.environ.get("JOBS", "6")))  # parallel segs
JOBS = []
# h264_videotoolbox (GPU) crashes with "Unexpected end of SEI NAL Unit" / "Error copying packet
# data" on specific frame content in this case's footage (reproduced on a clean single-codec
# re-encode, not a concat/stream artifact -- e.g. foxnews_6408836632112.mp4 @57s and the same
# absolute position in the final concatenated film); confirmed on this machine's ffmpeg-full build.
# libx264 (software) handles the same frames with no errors, so this case renders sw-only.
VENC = ["-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p"]


def nframes(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=nb_frames",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout.strip()
    return int(r) if r.isdigit() else 0


def render(*a, **k):
    JOBS.append(POOL.submit(_render, *a, **k))


def wait_jobs():
    for f in JOBS:
        f.result()
    JOBS.clear()


def _render(src, off, n, out, crop=None, overlays=(), force=False, mask=None):
    keyf = out.with_suffix(".key")
    key = f"{Path(src).resolve()}|{off:.3f}|{n}|{crop}|{mask}|{[(str(p), a, b) for p, a, b in overlays]}"
    if out.exists() and "--force" not in sys.argv:
        if nframes(out) == n and keyf.exists() and keyf.read_text() == key:
            return
    keyf.unlink(missing_ok=True)

    def build_cmd(hwaccel, zscale):
        base = video_filter(src, crop, force_pad=force, zscale=zscale, mask=mask)
        inputs = (["-hwaccel", "videotoolbox"] if hwaccel else []) + ["-ss", f"{off:.3f}", "-i", str(src)]
        if overlays:
            fc = f"[0:v]{base}[v0]"
            for k, (png, a, b) in enumerate(overlays):
                inputs2 = inputs + ["-i", str(png)]
                fc += f";[v{k}][{k+1}:v]overlay=0:0:format=auto:enable='between(t,{a:.3f},{b:.3f})'[v{k+1}]"
            fc += f";[v{len(overlays)}]format=yuv420p[o]"
            return [FFMPEG, "-y", "-loglevel", "error", *inputs2, "-filter_complex", fc, "-map", "[o]"]
        return [FFMPEG, "-y", "-loglevel", "error", *inputs, "-vf", base, "-map", "0:v:0"]

    last_err = None
    # retries: hwaccel decode first (fast), then sw decode, then sw decode + zscale normalization
    # (needed for a minority of 10-bit Envato sources with an unset transfer function).
    for attempt, (hwaccel, zscale) in enumerate(((True, False), (False, False), (False, True))):
        cmd = build_cmd(hwaccel, zscale) + ["-frames:v", str(n), "-an", *VENC, "-r", "30", str(out)]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            if nframes(out) == n:
                keyf.write_text(key)
                return
            last_err = f"{out.name}: {nframes(out)} frames, wanted {n}"
        except subprocess.CalledProcessError as e:
            last_err = e.stderr[-500:] if e.stderr else str(e)
    sys.exit(f"{out.name}: render failed after retries ({last_err})")


def placeholder_png(label, out):
    from PIL import Image, ImageDraw, ImageFont
    W, H = 1920, 1080
    im = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(im)
    f = ImageFont.truetype(str(ROOT / "kho/fonts/Inter/Inter-Black.otf"), 40)
    txt = f"PLACEHOLDER {label}"
    tw = d.textlength(txt, font=f)
    d.text(((W - tw) / 2, H / 2 - 20), txt, font=f, fill=(255, 255, 255))
    im.save(out)


def render_placeholder(n, out, label):
    if out.exists() and "--force" not in sys.argv:
        got = int(subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
                                   "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(out)],
                                  capture_output=True, text=True).stdout or 0)
        if got == n:
            return
    png = SEG / f"_ph_{out.stem}.png"
    placeholder_png(label, png)
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-loop", "1", "-i", str(png),
           "-vf", "scale=1920:1080,format=yuv420p", "-frames:v", str(n), "-an", *VENC, "-r", "30", str(out)]
    subprocess.run(cmd, check=True)


def load_graphics_index():
    """(seg, round(t0,2)) -> mp4 path, from edit/graphics_index.tsv's own 'file' column
    (<seg>_<t0>.mp4, NOT the *_vo.mp4 previews, per the WO)."""
    idx = {}
    with open(GRAPHICS_IDX) as f:
        rd = csv.reader(f, delimiter="\t")
        header = next(rd)
        for r in rd:
            if not r or r[0].startswith("#"):
                continue
            seg, t0, t1, file_ = r[0], r[1], r[2], r[3]
            idx[(seg, round(float(t0), 2))] = file_
    return idx


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(p)], capture_output=True, text=True).stdout)


def main():
    partial = "--partial" in sys.argv
    rows = load_shotmap()
    order = beat_order(rows)
    gfx_idx = load_graphics_index()

    ALEN = {}
    beat_rows = {}
    for b in order:
        brows = [r for r in rows if r["seg"] == b]
        beat_rows[b] = brows
        if b.startswith("K"):
            ALEN[b] = sum(r["t1"] - r["t0"] for r in brows)
        else:
            ALEN[b] = dur(AUD / f"{b}.wav")

    missing = []
    for b in order:
        for r in beat_rows[b]:
            if r["treat"].startswith("FOOT"):
                p, off, d, crop = resolve_foot(r["src"])
                if not p.exists():
                    missing.append(str(p))
            elif r["treat"] == "CLIP":
                p, off, d = resolve_clip(r["src"])
                if not p.exists():
                    missing.append(str(p))
    if missing:
        print("missing footage:\n" + "\n".join(sorted(set(missing))))
        if not partial:
            sys.exit(1)

    t_abs = 0.0
    parts = []
    log = []  # (t_abs, dur, seg, label)
    beat_start_abs = {}
    gfx_placeholder_count = 0
    gfx_real_count = 0

    for b in order:
        beat_start_abs[b] = t_abs
        if b.startswith("K"):
            r = beat_rows[b][0]
            p, off, d = resolve_clip(r["src"])
            n = round(d * FPS)
            out = SEG / f"{b}_00.mp4"
            render(p, off, n, out, crop=CROP_SOURCES.get(p.name), overlays=[], force=True)
            parts.append(out)
            log.append((round(t_abs, 2), round(d, 3), b, f"CLIP {p.stem} {r['src']}"))
            t_abs += d
        else:
            for i, r in enumerate(beat_rows[b]):
                t0, t1 = r["t0"], r["t1"]
                d = t1 - t0
                n = round(d * FPS)
                out = SEG / f"{b}_{i:02d}.mp4"
                if not r["treat"].startswith("FOOT"):
                    key = (b, round(t0, 2))
                    gfile = gfx_idx.get(key)
                    gpath = None
                    if gfile:
                        for cand in (Path(gfile), CASE / gfile, E / gfile):
                            if cand.exists():
                                gpath = cand.resolve(); break
                    if gpath:
                        gd = dur(gpath)
                        if gd + 0.05 < d:
                            sys.exit(f"{key}: graphic {gpath} too short ({gd:.2f}s < {d:.2f}s)")
                        if out.exists() and out.stat().st_mtime < gpath.stat().st_mtime:
                            out.unlink()
                        render(gpath, 0.0, n, out, force=True)
                        gfx_real_count += 1
                        label = f"{r['treat']} graphics_index:{gpath.name}"
                    else:
                        render_placeholder(n, out, f"{b}_{i} {r['treat']}")
                        gfx_placeholder_count += 1
                        label = f"{r['treat']} PLACEHOLDER {b}_{i}"
                else:
                    p, off, _d, crop = resolve_foot(r["src"])
                    render(p, off, n, out, crop=CROP_SOURCES.get(p.name, crop), overlays=[], force=False, mask=resolve_mask(p))
                    label = f"{r['treat']} {p.name}@{off:.1f}"
                parts.append(out)
                log.append((round(t_abs, 2), round(d, 3), b, label))
                t_abs += d

    if partial:
        print(f"--partial: cached footage/clip segs; graphics placeholders {gfx_placeholder_count}, "
              f"real graphics {gfx_real_count}")
        return

    wait_jobs()
    # ---------- video concat ----------
    (SEG / "list.txt").write_text("".join(f"file '{p}'\n" for p in parts))
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(SEG / "list.txt"),
                    "-c", "copy", str(SEG / "video.mp4")], check=True)

    # ---------- audio: VO beats + clip original audio, each loudnorm'd, exact part lengths, no music ----------
    ain = []; fl = []; k = 0
    for b in order:
        if b.startswith("K"):
            r = beat_rows[b][0]
            p, off, d = resolve_clip(r["src"])
            ain += ["-ss", f"{off:.3f}", "-t", f"{d:.3f}", "-i", str(p)]
        else:
            d = ALEN[b]
            ain += ["-i", str(AUD / f"{b}.wav")]
        fl.append(f"[{k}:a]atrim=0:{d:.4f},aresample=48000,aformat=channel_layouts=stereo,"
                  f"loudnorm=I=-16:TP=-1.5:LRA=11,apad=whole_dur={d:.4f},atrim=0:{d:.4f}[a{k}]")
        k += 1
    fc = ";".join(fl) + ";" + "".join(f"[a{j}]" for j in range(k)) + f"concat=n={k}:v=0:a=1[a]"
    subprocess.run([FFMPEG, "-y", "-loglevel", "error", *ain, "-filter_complex", fc, "-map", "[a]", "-c:a",
                    "pcm_s16le", str(SEG / "audio.wav")], check=True)

    OUT_NOCAP.parent.mkdir(parents=True, exist_ok=True)
    # final mux + whole-film corner logo overlay in the same pass (WO: assets/brand/corner_1920.png,
    # already 1920x1080 with transparency outside the corner mark; loop it as a still over the full length).
    subprocess.run([
        FFMPEG, "-y", "-loglevel", "error",
        "-i", str(SEG / "video.mp4"), "-i", str(SEG / "audio.wav"),
        "-loop", "1", "-framerate", "30", "-i", str(LOGO),
        "-filter_complex", "[0:v][2:v]overlay=0:0:shortest=1,format=yuv420p[v]",
        "-map", "[v]", "-map", "1:a",
        *VENC, "-c:a", "aac", "-b:a", "256k", "-t", f"{t_abs:.3f}",
        "-movflags", "+faststart", str(OUT_NOCAP),
    ], check=True)

    (E / "full_shots_v1.tsv").write_text(
        "t_abs\tdur\tseg\tshot\n" + "".join(f"{a}\t{d}\t{b}\t{l}\n" for a, d, b, l in log))

    isfoot = lambda l: l.startswith("FOOT") or l.startswith("CLIP")
    foot_s = sum(d for a, d, b, l in log if isfoot(l))
    gfx_s = sum(d for a, d, b, l in log if not isfoot(l))
    run = mx = 0
    for a, d, b, l in log:
        run = run + 1 if not isfoot(l) else 0
        mx = max(mx, run)
    print(f"full {t_abs:.2f}s, {len(log)} shots, {len(log)/t_abs*60:.1f} cuts/min, "
          f"footage {foot_s/t_abs:.1%}, max consecutive graphics {mx}, "
          f"graphics placeholders {gfx_placeholder_count}, real graphics {gfx_real_count}")
    print(OUT_NOCAP)


if __name__ == "__main__":
    main()
