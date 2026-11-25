#!/usr/bin/env python3
"""DOCUMENT look — real PDF page + yellow marker sweep, built in EffectCraft from the licensed Envato template
'Document Highlighter v1.1' (093cae66, Politics license).

Why native build: the template's own highlight strokes are expression-driven (rect Size/Position eased from the
dashboard 'Animation Speed' slider); EffectCraft imports them but renders them empty, and the style switch lands on
the negative-photostat look. So this pass builds the template's 'Scanned Pages' look in a fresh comp INSIDE the imported
template project, from the template's own assets: Wood_Background.jpg desk, ScannedPage_0N.jpg paper scan under the
real PDF page (multiply), DustTexture2.jpg, 'Dust Particles - Floating.mp4' overlay, BrushTexture_Wide.png as the marker
body (tinted yellow, multiply), revealed left->right by an animated track matte.

Motion grammar: whole page visible -> ONE slow push (log-zoom, smootherstep) onto the target -> settles (tiny drift)
-> marker sweeps each phrase starting at its spoken word (words.json).

usage: python3 tools/fx/doc_pass.py <BEAT> <spec.json> [--frames t,t,..]
spec (times in seconds from BEAT start, or word anchors {"word":"filing","n":1,"edge":"s","off":0}):
 {"pdf":"assets/docs/doj_brief_9th.pdf" (relative to CASE or absolute), "page":null,
  "from":{"word":"filing"}, "to":"end",
  "push":{"at":<time|anchor>, "dur":2.0, "box":[x0,y0,x1,y1] (PDF points, optional; default = union of marks), "screen_w":1400},
  "marks":[{"phrase":"verbatim text", "at":{"word":"reluctantly"}, "dur":null}],
  "label":"DOJ brief, 9th Cir., Nov 19, 2026", "name":"B2_doc", "case":"cases/alaska-doj-surrender"}
The phrase must exist verbatim in the PDF text layer (pdftotext -bbox-layout) or the pass exits 2: never fake a line.
Output: CASE/edit/seg/<name>.mp4 (voice slice muxed), QC: CASE/edit/qc/<name>_tile.png + <name>_doc.json.
"""
import html, json, math, re, shutil, subprocess, sys
from pathlib import Path

FX = Path(__file__).resolve().parent
ROOT = FX.parents[1]                                  # Politics/
sys.path.insert(0, str(FX))
import ec  # noqa  (lock-aware EffectCraft calls)

EC = ec.EC
TPL = ROOT / "kho/envato_templates/doc_highlighter"
TPL_SRC = TPL / "src/Document Highlighter v1.1"
BASE = TPL / "dh_base.ecproj"
FPS = 30
W, H = 1920, 1080


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


# ---------------------------------------------------------------- template base (import + relink by basename)
def build_base():
    if BASE.exists():
        return
    aep = TPL_SRC / "Document Highlighter Template HD.aep"
    r = run([EC, "--empty", "exec", "file.importAep", json.dumps({"path": str(aep), "allowLosses": True}),
             "--save-as", str(BASE), "--json"])
    if r.returncode:
        sys.exit("import failed: " + r.stderr[-400:])
    idx = {}
    for p in TPL_SRC.rglob("*"):
        if "__MACOSX" not in p.parts and p.is_file():
            idx[p.name] = str(p)
    miss = json.loads(run([EC, "--project", str(BASE), "exec", "footage.missing", "{}", "--json"]).stdout)["missing"]
    for m in miss:
        if m["name"] in idx:
            run([EC, "--project", str(BASE), "run", "footage.relink", json.dumps({"item": m["item"], "path": idx[m["name"]]}), "--save"])
    left = json.loads(run([EC, "--project", str(BASE), "exec", "footage.missing", "{}", "--json"]).stdout)["missing"]
    print("base built, unresolved footage:", [x["name"] for x in left])


# ---------------------------------------------------------------- PDF text layer
def norm(w):
    w = html.unescape(w).replace("\u2019", "'").replace("\u2018", "'").replace("\u201c", '"').replace("\u201d", '"')
    return re.sub(r"[^\w']", "", w.lower())


def pdf_words(pdf):
    xml = run(["pdftotext", "-bbox-layout", str(pdf), "-"]).stdout
    pages = []
    for pw, ph, body in re.findall(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', xml, re.S):
        ws = [(float(a), float(b), float(c), float(d), html.unescape(t)) for a, b, c, d, t in
              re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>', body)]
        pages.append((float(pw), float(ph), [w for w in ws if norm(w[4])]))
    return pages


def find_phrase(pages, phrase, page=None):
    tgt = [norm(w) for w in phrase.split() if norm(w)]
    for pi, (pw, ph, ws) in enumerate(pages, 1):
        if page and pi != page:
            continue
        toks = [norm(w[4]) for w in ws]
        for i in range(len(toks) - len(tgt) + 1):
            if toks[i:i + len(tgt)] == tgt:
                return pi, ws[i:i + len(tgt)]
    return None


def line_boxes(ws):
    """group matched words into visual lines -> [(x0,y0,x1,y1,text)] in PDF points"""
    lines = []
    for w in ws:
        if lines and abs(w[1] - lines[-1][1]) < 3 and w[0] > lines[-1][2] - 1:
            l = lines[-1]; lines[-1] = (l[0], min(l[1], w[1]), w[2], max(l[3], w[3]), l[4] + " " + w[4])
        else:
            lines.append(w)
    return lines


# ---------------------------------------------------------------- timing
def resolve(t, words, beat_dur):
    if t is None:
        return None
    if isinstance(t, (int, float)):
        return float(t)
    if t == "end":
        return beat_dur
    want, n, k = norm(t["word"]), t.get("n", 1), 0
    for w in words:
        if norm(w["w"]) == want and w["s"] >= t.get("after", -1):
            k += 1
            if k == n:
                return (w["e"] if t.get("edge") == "e" else w["s"]) + t.get("off", 0.0)
    sys.exit(f"word anchor not found: {t}")


def smoother(x):
    x = min(1.0, max(0.0, x))
    return x * x * x * (x * (6 * x - 15) + 10)


JSX = r"""
var P=%(p)s;
function comp(n){for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name==n) return it;}}
function foot(n){for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(!(it instanceof CompItem) && it.name==n) return it;}}
function tr(l,n){return l.property("ADBE Transform Group").property(n);}
function imp(path){ return app.project.importFile(new ImportOptions(new File(path))); }
var D=P.dur;
// ---- PAGE comp (page pixels): white -> scanned paper texture -> real PDF page (multiply) -> markers
var PG=app.project.items.addComp("DOC PAGE",P.pw,P.ph,1,D,30);
var wh=PG.layers.addSolid([1,1,1],"paper white",P.pw,P.ph,1,D);
var scan=PG.layers.add(foot(P.scan)); tr(scan,"ADBE Anchor Point").setValue([1240,1754]); tr(scan,"ADBE Position").setValue([P.pw/2,P.ph/2]);
tr(scan,"ADBE Scale").setValue([P.pw/2480*100,P.ph/3508*100]); tr(scan,"ADBE Opacity").setValue(P.scan_op);
var pg=PG.layers.add(imp(P.png)); tr(pg,"ADBE Position").setValue([P.pw/2,P.ph/2]); pg.blendingMode=BlendingMode.MULTIPLY;
var dust=PG.layers.add(imp(P.dusttex)); tr(dust,"ADBE Position").setValue([P.pw/2,P.ph/2]);
tr(dust,"ADBE Scale").setValue([P.pw/800*100,P.ph/600*100]); dust.blendingMode=BlendingMode.SCREEN; tr(dust,"ADBE Opacity").setValue(P.dust_op);
for(var m=0;m<P.marks.length;m++){ var M=P.marks[m];
  var b=PG.layers.add(foot("BrushTexture_Wide.png")); b.name="marker "+m;
  tr(b,"ADBE Anchor Point").setValue([607,107]); tr(b,"ADBE Position").setValue([M.cx,M.cy]);
  tr(b,"ADBE Scale").setValue([M.w/1214*100*1.04,M.h/150*100]);
  var f=b.property("ADBE Effect Parade").addProperty("ADBE Fill"); f.property("ADBE Fill-0002").setValue(P.yellow);
  b.blendingMode=BlendingMode.MULTIPLY; tr(b,"ADBE Opacity").setValue(P.mark_op);
  var mt=PG.layers.addShape(); mt.name="marker matte "+m; mt.moveBefore(b);
  tr(mt,"ADBE Anchor Point").setValue([0,0]); tr(mt,"ADBE Position").setValue([0,0]);
  var g=mt.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group"); var cn=g.property("ADBE Vectors Group");
  var r=cn.addProperty("ADBE Vector Shape - Rect"); var fl=cn.addProperty("ADBE Vector Graphic - Fill"); fl.property("ADBE Vector Fill Color").setValue([1,1,1,1]);
  var sz=r.property("ADBE Vector Rect Size"), ps=r.property("ADBE Vector Rect Position");
  var x0=M.cx-M.w*0.56, hh=M.h*1.6;
  for(var i=0;i<M.sweep.length;i++){ var k=M.sweep[i]; var ww=Math.max(0.5,M.w*1.12*k[1]); sz.setValueAtTime(k[0],[ww,hh]); ps.setValueAtTime(k[0],[x0+ww/2,M.cy]); }
  b.trackMatteType=TrackMatteType.ALPHA;
}
// ---- DOC comp 1920x1080: desk -> page (camera keys) -> dust overlay -> vignette -> source label
var C=app.project.items.addComp(P.name,1920,1080,1,D,30);
var blk=C.layers.addSolid([0.05,0.05,0.06],"desk dark",1920,1080,1,D);
var wd=C.layers.add(imp(P.wood)); tr(wd,"ADBE Position").setValue([960,540]); tr(wd,"ADBE Opacity").setValue(P.wood_op);
var shd=C.layers.addSolid([0,0,0],"page shadow",P.pw,P.ph,1,D); tr(shd,"ADBE Anchor Point").setValue([0,0]);
var sfx=shd.property("ADBE Effect Parade").addProperty("ADBE Gaussian Blur 2"); sfx.property(1).setValue(P.shadow_blur);
tr(shd,"ADBE Opacity").setValue(55);
var pl=C.layers.add(PG); tr(pl,"ADBE Anchor Point").setValue([0,0]);
var pp=tr(pl,"ADBE Position"), psc=tr(pl,"ADBE Scale"), wsc=tr(wd,"ADBE Scale"), sp=tr(shd,"ADBE Position"), ss=tr(shd,"ADBE Scale");
for(var i=0;i<P.cam.length;i++){ var c=P.cam[i]; pp.setValueAtTime(c[0],[c[1],c[2]]); psc.setValueAtTime(c[0],[c[3]*100,c[3]*100]);
  sp.setValueAtTime(c[0],[c[1]+P.shadow_off*c[3],c[2]+P.shadow_off*c[3]]); ss.setValueAtTime(c[0],[c[3]*100,c[3]*100]); wsc.setValueAtTime(c[0],[c[4]*100,c[4]*100]); }
var df=C.layers.add(imp(P.float_mp4)); tr(df,"ADBE Position").setValue([960,540]); df.blendingMode=BlendingMode.MULTIPLY; tr(df,"ADBE Opacity").setValue(P.float_op);
var vg=C.layers.addSolid([0,0,0],"vignette",1920,1080,1,D);
var ms=vg.property("ADBE Mask Parade").addProperty("ADBE Mask Atom"); var shp=new Shape(); shp.vertices=[[-200,-120],[2120,-120],[2120,1200],[-200,1200]]; shp.closed=true;
ms.property("ADBE Mask Shape").setValue(shp); ms.property("ADBE Mask Feather").setValue([420,420]); ms.inverted=true; ms.property("ADBE Mask Offset").setValue(-60);
tr(vg,"ADBE Opacity").setValue(P.vig_op);
var out={};
if(P.label){
  var tl=C.layers.addText(P.label); var sd=tl.property("ADBE Text Properties").property("ADBE Text Document"); var d=sd.value;
  d.font=P.font; d.fontSize=34; d.fillColor=[1,1,1]; d.applyFill=true; d.justification=ParagraphJustification.LEFT_JUSTIFY; sd.setValue(d);
  var rc=tl.sourceRectAtTime(1,false); out.label=[rc.left,rc.top,rc.width,rc.height];
  var bx=C.layers.addShape(); bx.name="label box"; bx.moveAfter(tl); tr(bx,"ADBE Anchor Point").setValue([0,0]); tr(bx,"ADBE Position").setValue([0,0]);
  var g2=bx.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group"); var c2=g2.property("ADBE Vectors Group");
  var r2=c2.addProperty("ADBE Vector Shape - Rect"); var f2=c2.addProperty("ADBE Vector Graphic - Fill"); f2.property("ADBE Vector Fill Color").setValue(P.label_col);
  var bw=rc.width+56, bh=58, bxl=70, byt=1080-70-bh;
  r2.property("ADBE Vector Rect Size").setValue([bw,bh]); r2.property("ADBE Vector Rect Position").setValue([bxl+bw/2,byt+bh/2]);
  tr(tl,"ADBE Position").setValue([bxl+28-rc.left, byt+bh/2-(rc.top+rc.height/2)]);
  var lays=[tl,bx]; for(var q=0;q<2;q++){ var o=tr(lays[q],"ADBE Opacity"); o.setValueAtTime(P.label_in,0); o.setValueAtTime(P.label_in+0.35,100);
    var po=tr(lays[q],"ADBE Position"); var v=po.value; po.setValueAtTime(P.label_in,[v[0]-30,v[1]]); po.setValueAtTime(P.label_in+0.35,[v[0],v[1]]); }
}
writeLn("ok "+JSON.stringify(out));
"""


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        sys.exit(__doc__)
    beat, spec_path = a[0], Path(a[1])
    frames = a[a.index("--frames") + 1].split(",") if "--frames" in a else None
    S = json.load(open(spec_path))
    case = ROOT / S.get("case", "cases/alaska-doj-surrender")
    name = S.get("name", f"{beat}_doc")
    pdf = Path(S["pdf"]) if Path(S["pdf"]).is_absolute() else case / S["pdf"]
    wav = case / f"audio_full_v1/{beat}.wav"
    words = json.load(open(case / "audio_full_v1/words.json"))[beat]
    beat_dur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(wav)]).stdout.strip())

    # -------- find every phrase verbatim (all on one page)
    pages = pdf_words(pdf)
    page, marks = S.get("page"), []
    for mk in S["marks"]:
        hit = find_phrase(pages, mk["phrase"], page)
        if not hit:
            print(f"PHRASE NOT FOUND verbatim in {pdf.name}" + (f" p.{page}" if page else "") + f": {mk['phrase']!r}", file=sys.stderr)
            sys.exit(2)
        page = hit[0]
        marks.append((mk, line_boxes(hit[1])))
    pw_pt, ph_pt, _ = pages[page - 1]

    t0 = resolve(S.get("from", 0.0), words, beat_dur)
    t1 = min(resolve(S.get("to", "end"), words, beat_dur), beat_dur)
    D = round(t1 - t0, 3)
    push = S.get("push", {})
    p_at = resolve(push.get("at"), words, beat_dur)
    p_at = (t0 + 0.5) if p_at is None else p_at
    p_at -= t0
    first_mark = min(resolve(mk["at"], words, beat_dur) for mk, _ in marks) - t0
    p_dur = push.get("dur", 2.0)
    if p_at + p_dur > first_mark - 0.15:                     # camera must settle before the first sweep
        p_dur = round(first_mark - 0.15 - p_at, 3)
    if p_dur < 0.8:
        sys.exit(f"push window too short ({p_dur:.2f}s) between push start and first marker")

    # -------- target box (PDF points) and page pixel size so the settled zoom stays <= 1.0 (sharp text)
    if push.get("box"):
        bx = push["box"]
    else:
        # default: the full text column (so lines are never cut mid-word) x the marked lines +-40 pt
        allb = [b for _, ls in marks for b in ls]
        pws = pages[page - 1][2]
        xs0 = sorted(w[0] for w in pws); xs1 = sorted(w[2] for w in pws)
        cx0 = min(xs0[int(len(xs0) * 0.03)], min(b[0] for b in allb)); cx1 = max(xs1[int(len(xs1) * 0.97) - 1], max(b[2] for b in allb))
        bx = [cx0 - 14, min(b[1] for b in allb) - 40, cx1 + 14, max(b[3] for b in allb) + 40]
    sw = push.get("screen_w", 1400)
    k_pt = min(sw / (bx[2] - bx[0]), 860 / (bx[3] - bx[1]))   # screen px per PDF point when settled
    pw = int(min(5600, max(2480, math.ceil(pw_pt * k_pt * 1.02))))
    pw += pw % 2
    s = pw / pw_pt
    ph = int(round(ph_pt * s)); ph += ph % 2
    k1 = k_pt / s
    k0 = min(1000 / ph, 1800 / pw)
    T = ((bx[0] + bx[2]) / 2 * s, (bx[1] + bx[3]) / 2 * s)
    p0 = (960 + k0 * (T[0] - pw / 2), 540 + k0 * (T[1] - ph / 2))
    drift = S.get("drift", 0.012)
    cam = []
    n = int(round(D * FPS))
    for i in range(n + 2):
        t = i / FPS
        e = smoother((t - p_at) / p_dur)
        k = k0 * (k1 / k0) ** e
        if t > p_at + p_dur:
            k *= 1 + drift * (t - p_at - p_dur) / max(1.0, D - p_at - p_dur)
        px, py = p0[0] + (960 - p0[0]) * e, p0[1] + (540 - p0[1]) * e
        wood = 0.5 * (k / k0) ** 0.35
        cam.append([round(t, 4), round(px - k * T[0], 3), round(py - k * T[1], 3), round(k, 6), round(wood, 5)])

    # -------- markers (page px), sweep keys per frame (gentle ease in/out = hand speed)
    MK, ev = [], []
    for mk, lines in marks:
        ts = resolve(mk["at"], words, beat_dur) - t0
        tot = sum(b[2] - b[0] for b in lines) * s * k1          # on-screen length of the stroke
        dur = mk.get("dur") or max(0.55, min(1.5, tot / 1150))
        acc = 0.0
        for b in lines:
            seg = dur * ((b[2] - b[0]) * s * k1) / tot
            pad = 4 * s / 4.05
            w_ = (b[2] - b[0]) * s + 2 * pad
            h_ = (b[3] - b[1]) * s * 1.18
            sweep = [[0, 0.0], [round(ts + acc, 4), 0.0]]
            m = max(2, int(round(seg * FPS)))
            for j in range(1, m + 1):
                x = j / m                                       # mostly linear hand speed, soft start/stop
                sweep.append([round(ts + acc + seg * x, 4), round(0.6 * x + 0.4 * (0.5 - 0.5 * math.cos(math.pi * x)), 5)])
            MK.append(dict(cx=round((b[0] + b[2]) / 2 * s, 2), cy=round((b[1] + b[3]) / 2 * s + 0.04 * (b[3] - b[1]) * s, 2), w=round(w_, 2), h=round(h_, 2), sweep=sweep))
            acc += seg
        ev.append(dict(phrase=mk["phrase"], page=page, lines_pt=[[round(v, 1) for v in b[:4]] + [b[4]] for b in lines],
                       sweep_start_clip=round(ts, 3), sweep_start_beat=round(ts + t0, 3), sweep_dur=round(dur, 3)))

    work = FX / "work" / name
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    png = work / f"page{page}.png"
    run(["pdftoppm", "-f", str(page), "-l", str(page), "-scale-to-x", str(pw), "-scale-to-y", str(ph), "-png", "-singlefile", str(pdf), str(png.with_suffix(""))])
    if not png.exists():
        sys.exit("pdftoppm failed")

    build_base()
    proj = work / f"{name}.ecproj"
    shutil.copy(BASE, proj)
    P = dict(name=name, dur=D, pw=pw, ph=ph, png=str(png), scan=S.get("scan", "ScannedPage_02.jpg"), scan_op=S.get("scan_op", 100),
             wood=str(TPL_SRC / "(Footage)/0. Assets/Images/General/Wood_Background.jpg"), dusttex=str(TPL_SRC / "(Footage)/0. Assets/Images/General/DustTexture2.jpg"), float_mp4=str(TPL_SRC / "(Footage)/0. Assets/Video/Dust Particles - Floating.mp4"), dust_op=S.get("dust_op", 0), float_op=S.get("float_op", 45), wood_op=70, vig_op=55, mark_op=95, yellow=[1.0, 0.84, 0.0, 1],
             shadow_blur=40 / k0 * 0.25, shadow_off=14 * s / 4.05, cam=cam, marks=MK, label=S.get("label", ""),
             font=S.get("font", "Arial-BoldMT"), label_col=[0.78, 0.06, 0.18, 1], label_in=S.get("label_in", 0.3))
    (work / f"{name}.jsx").write_text(JSX % dict(p=json.dumps(P)))
    r = run([EC, "script", str(work / f"{name}.jsx"), str(proj), "--save"])
    print(r.stdout.strip()[-500:], r.stderr.strip()[-600:])
    if r.returncode or "ok" not in r.stdout:
        sys.exit("jsx failed")

    case_qc = case / "edit/qc"; case_qc.mkdir(parents=True, exist_ok=True)
    seg = case / "edit/seg"; seg.mkdir(parents=True, exist_ok=True)
    meta = dict(beat=beat, pdf=str(pdf.relative_to(ROOT)) if str(pdf).startswith(str(ROOT)) else str(pdf), page=page,
                from_beat=round(t0, 3), to_beat=round(t1, 3), dur=D, push_start=round(p_at, 3), push_dur=round(p_dur, 3),
                page_px=[pw, ph], zoom_full=round(k0, 4), zoom_settled=round(k1, 4), target_box_pt=[round(v, 1) for v in bx],
                marks=ev, label=S.get("label", ""))
    (case_qc / f"{name}_doc.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta, indent=1))

    if frames:
        ec.frames(str(proj), [(name, float(t), str(work / f"f_{t}.png")) for t in frames], ms=1920)
        print("frames in", work)
        return

    raw = work / f"{name}_raw.mp4"
    ec.render(str(proj), name, str(raw))
    out = seg / f"{name}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-ss", f"{t0:.3f}", "-t", f"{D:.3f}", "-i", str(wav),
                    "-filter_complex", f"[0:v]scale=1920:1080,fps=30,format=yuv420p[v];[1:a]afade=t=in:d=0.02,afade=t=out:st={max(0, D - 0.12):.3f}:d=0.12[a]",
                    "-map", "[v]", "-map", "[a]", "-c:v", "h264_videotoolbox", "-q:v", "72", "-allow_sw", "0", "-c:a", "aac", "-b:a", "192k",
                    "-t", f"{D:.3f}", "-movflags", "+faststart", str(out)], check=True)
    j = run(["python3", str(FX / "judder_check.py"), str(out)]).stdout.strip()
    print("JUDDER", j)
    tf = []
    for i in range(8):
        t = D * (i + 0.5) / 8
        f = work / f"tile_{i}.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(out), "-frames:v", "1", "-vf", "scale=960:540", str(f)])
        tf.append(str(f))
    ec.tile(str(case_qc / f"{name}_tile.png"), tf, cols=2, w=960, h=540)
    meta["judder"] = j; meta["tile_times"] = [round(D * (i + 0.5) / 8, 2) for i in range(8)]
    (case_qc / f"{name}_doc.json").write_text(json.dumps(meta, indent=1))
    print("wrote", out, case_qc / f"{name}_tile.png")


if __name__ == "__main__":
    main()
