#!/usr/bin/env python3
"""NUMBERS + WHAT-NEXT look (L-NUM / L-TIME) for alaska-doj-surrender, rendered in EffectCraft from the licensed
Envato templates (project Politics):
  chart    "Bar Charts | Flat Data Visualization" 404f4682  -> kho/envato_templates/chart_flat_dataviz   comp "02 Top Markets 16x9"
  timeline "Timeline | Flat Data Visualization"   1a546449  -> kho/envato_templates/timeline_flat_dataviz comp "01 Company Story 16x9"

How the template is used (EC render, hybrid):
  * N17/N18/N20/N21: the template comp is DUPLICATED inside the imported template project and keeps its own chrome
    and intro animation (cream Background, white rounded Card, Deco block, Label Mark, Label/Title/Subtitle in Inter,
    CONTROLLER palette). Its 5 expression-driven bar rows are switched off (they cannot be keyed to words, and they
    cannot stack blocks), and the data layer is rebuilt natively in the template's own grammar (Track/Bar rects in
    the template's track colour + palette, Inter Bold/ExtraBold values) with every key computed here from words.json.
  * T26: the template's own Year/Title/Node/Rail layers are re-spaced and re-keyed on the spoken words.
  * Every layer except Background is parented to a CAM null: slow continuous push (no frozen frame) and, in N20,
    the eased push onto the bar ends for the 1,651 gap.
  Fonts: Inter (template's font, SIL OFL) copied to kho/fonts/Inter and ~/Library/Fonts.

usage: python3 tools/fx/num_pass.py N17|N18|N20|N21|T26|all [--frames t1,t2,..] [--no-render]
spec: CASE/edit/specs/num_<shot>.json (written by this script = what was built; texts + anchors + pop log)
out : CASE/edit/seg/<shot>.mp4 (video only, round(beat_dur*30) frames), CASE/edit/qc/<shot>_tile.png + <shot>_num.json
"""
import json, math, re, shutil, subprocess, sys
from pathlib import Path

FX = Path(__file__).resolve().parent
ROOT = FX.parents[1]
sys.path.insert(0, str(FX))
import ec  # noqa  (lock-aware EffectCraft calls)

EC = ec.EC
CASE = ROOT / "cases/alaska-doj-surrender"
WORDS = json.load(open(CASE / "audio_full_v1/words.json"))
CHART = ROOT / "kho/envato_templates/chart_flat_dataviz/chart_flat_dataviz.ecproj"
TLINE = ROOT / "kho/envato_templates/timeline_flat_dataviz/timeline_flat_dataviz.ecproj"
FPS = 30
SRC = "Alaska Division of Elections, unofficial results, 401/401 precincts"

# template palette (CONTROLLER of 02 Top Markets), D/R mapped onto it
BG = [0.953, 0.941, 0.910]; CARD = [1, 1, 1]; INK = [0.086, 0.086, 0.114]; MUTED = [0.431, 0.420, 0.471]
BLUE = [0.184, 0.357, 1.0]; RED = [0.898, 0.220, 0.231]; AMBER = [1.0, 0.761, 0.2]; GREEN = [0.098, 0.702, 0.490]
TRACK = [CARD[i] + (MUTED[i] - CARD[i]) * 0.13 for i in range(3)]
G_DJ = [0.431, 0.420, 0.471]; G_HK = [0.60, 0.59, 0.64]; G_WI = [0.76, 0.75, 0.79]
AMBER_INK = [0.62, 0.42, 0.0]


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def beat_dur(b):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                      str(CASE / f"audio_full_v1/{b}.wav")]).stdout.strip())


def norm(w):
    return re.sub(r"[^\w%\-]", "", w.lower())


def W(beat, word, n=1, edge="s"):
    k = 0
    for w in WORDS[beat]:
        if norm(w["w"]) == norm(word):
            k += 1
            if k == n:
                return w[edge]
    sys.exit(f"word {word!r} n={n} not in {beat}")


# ---------------------------------------------------------------- easing
def cl(x): return min(1.0, max(0.0, x))
def eo(x): x = cl(x); return 1 - (1 - x) ** 3
def eio(x): x = cl(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def eback(x, s=1.6): x = cl(x); x -= 1; return 1 + (s + 1) * x ** 3 + s * x ** 2
def lerp(a, b, e): return a + (b - a) * e


# ---------------------------------------------------------------- scene model: props are functions of t
class Scene:
    def __init__(self, name, beat, title=None):
        self.name, self.beat = name, beat
        self.D = beat_dur(beat)
        self.N = round(self.D * FPS)
        self.els, self.pops, self.title = [], [], title
        self.cam = None

    def rect(self, name, cx, cy, w, h, col, op=lambda t: 100, rnd=10, stroke=None):
        """cx,cy,w,h: callables or numbers (centre + size)"""
        self.els.append(dict(kind="rect", name=name, cx=cx, cy=cy, w=w, h=h, col=col, op=op, rnd=rnd, stroke=stroke))

    def bar(self, name, x0, y, h, wfn, col, op=lambda t: 100, rnd=10):
        f = lambda v: v if callable(v) else (lambda t, v=v: v)
        x0, y, wfn = f(x0), f(y), f(wfn)
        self.rect(name, lambda t: x0(t) + max(0.5, wfn(t)) / 2, y, lambda t: max(0.5, wfn(t)), h, col, op, rnd)

    def ellipse(self, name, cx, cy, d, col, sc=lambda t: 100, op=lambda t: 100):
        self.els.append(dict(kind="ell", name=name, cx=cx, cy=cy, d=d, col=col, sc=sc, op=op))

    def text(self, name, s, x, y, size, font="Inter-Bold", col=INK, ax=0.0, op=lambda t: 100, sc=lambda t: 100, track=0):
        """x,y = point at horizontal fraction ax of the text box, vertical centre of the cap height"""
        self.els.append(dict(kind="text", name=name, s=s, x=x, y=y, size=size, font=font, col=col, ax=ax, op=op, sc=sc, track=track))

    def pop(self, name, s, x, y, size, t0, word=None, font="Inter-ExtraBold", col=INK, ax=0.0, rise=16, out=None, track=0):
        """number/label pop: eased opacity + back-eased scale 72->100 + rise, starting at t0 (s in beat)"""
        tt = t0 - 0.06
        def op(t):
            v = 100 * eo((t - tt) / 0.18)
            if out:
                v *= 1 - eio((t - out[0]) / out[1])
            return v
        sc = lambda t: 72 + 28 * eback((t - tt) / 0.42)
        yy = y if callable(y) else (lambda t, y=y: y)
        xx = x if callable(x) else (lambda t, x=x: x)
        self.text(name, s, xx, lambda t: yy(t) + rise * (1 - eo((t - tt) / 0.42)), size, font, col, ax, op, sc, track)
        if word:
            self.pops.append(dict(label=s, pop_start=round(tt, 3), legible=round(tt + 0.12, 3), word=word[0],
                                  word_s=round(word[1], 3), delta=round(tt + 0.12 - word[1], 3)))

    def fade(self, t0, d=0.3, t1=None, d1=0.3):
        return lambda t: 100 * eo((t - t0) / d) * (1 - (eio((t - t1) / d1) if t1 is not None else 0))


def sample(fn, n, r=3):
    """per-frame samples -> sparse key list [[t,v]] (keys only where the value moves; holds collapse)"""
    vals = []
    for i in range(n):
        v = fn(i / FPS)
        v = [round(float(x), r) for x in v] if isinstance(v, (list, tuple)) else round(float(v), r)
        vals.append(v)
    keys = []
    for i, v in enumerate(vals):
        if i == 0 or i == n - 1 or v != vals[i - 1] or v != vals[i + 1]:
            keys.append([round(i / FPS, 4), v])
    if len(keys) > 1 and all(k[1] == keys[0][1] for k in keys):
        keys = [keys[0]]
    return keys


def C(v):
    return v if callable(v) else (lambda t, v=v: v)


def compile_scene(S, n):
    out = []
    for e in S.els:
        d = dict(kind=e["kind"], name=e["name"])
        if e["kind"] == "rect":
            cf = C(e["col"])
            d.update(col=list(cf(0)) + [1], rnd=e["rnd"], stroke=e["stroke"], colk=sample(lambda t: list(cf(t)), n, 3) if callable(e["col"]) else None,
                     pos=sample(lambda t: [C(e["cx"])(t), C(e["cy"])(t)], n, 2),
                     size=sample(lambda t: [C(e["w"])(t), C(e["h"])(t)], n, 2), op=sample(e["op"], n, 2))
        elif e["kind"] == "ell":
            cf = C(e["col"])
            d.update(col=list(cf(0)) + [1], d=e["d"], pos=[[0, [e["cx"], e["cy"]]]], sc=sample(e["sc"], n, 2),
                     op=sample(e["op"], n, 2), colk=sample(lambda t: list(cf(t)), n, 3) if callable(e["col"]) else None)
        else:
            d.update(s=e["s"], size=e["size"], font=e["font"], col=e["col"], ax=e["ax"], track=e["track"],
                     pos=sample(lambda t: [C(e["x"])(t), C(e["y"])(t)], n, 2), op=sample(e["op"], n, 2),
                     sc=sample(e["sc"], n, 2))
        out.append(d)
    return out


# ---------------------------------------------------------------- camera
def drift_cam(D, F=(960, 640), z1=1.06, pan=(-26, -10)):
    """slow continuous push: zoom 1 -> z1 and a small pan; mostly linear so it never stands still at the cut points"""
    def cam(t):
        e = 0.7 * (t / D) + 0.3 * (0.5 - 0.5 * math.cos(math.pi * cl(t / D)))
        return 1 + (z1 - 1) * e, F[0], F[1], F[0] + pan[0] * e, F[1] + pan[1] * e
    return cam


def cam_keys(cam, n):
    """CAM null: anchor fixed (960,540); point F maps to screen S at zoom z -> position = S - z*(F - A)"""
    pos, sc = [], []
    for i in range(n):
        z, fx, fy, sx, sy = cam(i / FPS)
        pos.append([round(i / FPS, 4), [round(sx - z * (fx - 960), 3), round(sy - z * (fy - 540), 3)]])
        sc.append([round(i / FPS, 4), round(z * 100, 4)])
    return pos, sc


# ---------------------------------------------------------------- JSX
JSX_CHART = r"""
var P=%(p)s;
function comp(n){for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name==n) return it;}}
for (var i=1;i<=app.project.numItems;i++){var c=app.project.item(i); if(!(c instanceof CompItem)) continue; c.frameRate=30;
 for(var j=1;j<=c.numLayers;j++){var ef=c.layer(j).property("ADBE Effect Parade"); if(!ef) continue; for(var e=ef.numProperties;e>=1;e--) if(ef.property(e).matchName=="ADBE Posterize Time") ef.property(e).remove(); } }
function setText(l,s){ var sp=l.property("ADBE Text Properties").property("ADBE Text Document"); var td=sp.value; td.text=s; sp.setValue(td); }
function tr(l){return l.property("ADBE Transform Group");}
function K(prop,keys){ if(keys.length==1){ prop.setValue(keys[0][1]); return; } for(var i=0;i<keys.length;i++) prop.setValueAtTime(keys[i][0],keys[i][1]); }
var T0=comp(P.tpl);
var C=T0.duplicate(); C.name=P.name; C.duration=P.dur; C.frameRate=30;
for(var j=1;j<=C.numLayers;j++){ var L0=C.layer(j); L0.locked=false; L0.startTime=-P.pre; L0.inPoint=0; L0.outPoint=P.dur; }
var ctl=C.layer("CONTROLLER").property("ADBE Effect Parade");
try{ ctl.property("Out Animation").property(1).setValue(0); }catch(e){ writeLn("no Out Animation ctl"); }
for(var k in P.ctl){ try{ ctl.property(k).property(1).setValue(P.ctl[k]); }catch(e){ writeLn("ctl "+k+": "+e); } }
C.layer("Out Wipe 1").enabled=false; C.layer("Out Wipe 2").enabled=false;
for(var q=0;q<P.off.length;q++){ try{ C.layer(P.off[q]).enabled=false; }catch(e){ writeLn("off "+P.off[q]+": "+e); } }
setText(C.layer("Label"),P.label); setText(C.layer("Title"),P.title); setText(C.layer("Subtitle"),P.sub);
// ---- native data layer in the template grammar
for(var i=0;i<P.els.length;i++){ var E=P.els[i], L;
  if(E.kind=="rect"||E.kind=="ell"){
    L=C.layers.addShape(); L.name=E.name;
    var g=L.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group"); var cn=g.property("ADBE Vectors Group");
    var r;
    if(E.kind=="rect"){ r=cn.addProperty("ADBE Vector Shape - Rect"); r.property("ADBE Vector Rect Roundness").setValue(E.rnd); K(r.property("ADBE Vector Rect Size"),E.size); }
    else { r=cn.addProperty("ADBE Vector Shape - Ellipse"); r.property("ADBE Vector Ellipse Size").setValue([E.d,E.d]); K(tr(L).property("ADBE Scale"),E.sc.map?E.sc.map(function(k){return [k[0],[k[1],k[1]]];}):E.sc); }
    if(E.stroke){ var st=cn.addProperty("ADBE Vector Graphic - Stroke"); st.property("ADBE Vector Stroke Color").setValue(E.stroke[0]); st.property("ADBE Vector Stroke Width").setValue(E.stroke[1]); }
    var fl=cn.addProperty("ADBE Vector Graphic - Fill"); var fc=fl.property("ADBE Vector Fill Color"); fc.setValue(E.col);
    if(E.colk && E.colk.length>1){ for(var q=0;q<E.colk.length;q++){ var cv=E.colk[q][1]; fc.setValueAtTime(E.colk[q][0],[cv[0],cv[1],cv[2],1]); } }
    tr(L).property("ADBE Anchor Point").setValue([0,0]);
    K(tr(L).property("ADBE Position"),E.pos);
  } else {
    L=C.layers.addText(E.s); L.name=E.name;
    var sd=L.property("ADBE Text Properties").property("ADBE Text Document"); var td=sd.value;
    td.font=E.font; td.fontSize=E.size; td.fillColor=E.col; td.applyFill=true; td.applyStroke=false; td.tracking=E.track;
    td.justification=ParagraphJustification.LEFT_JUSTIFY; sd.setValue(td);
    var rc=L.sourceRectAtTime(0,false);
    // vertical centre = middle of the cap height (Inter cap = 0.727 em) above the baseline
    tr(L).property("ADBE Anchor Point").setValue([rc.left+rc.width*E.ax, -0.3635*E.size]);
    K(tr(L).property("ADBE Position"),E.pos);
    K(tr(L).property("ADBE Scale"),E.sc.map(function(k){return [k[0],[k[1],k[1]]];}));
  }
  K(tr(L).property("ADBE Opacity"),E.op);
}
// ---- CAM null: everything but the flat background rides the camera
var cam=C.layers.addNull(); cam.name="CAM"; tr(cam).property("ADBE Anchor Point").setValue([960,540]); tr(cam).property("ADBE Position").setValue([960,540]);
var skip={"CAM":1,"Background":1,"CONTROLLER":1,"ADVANCED":1,"DATA":1};
for(var j=1;j<=C.numLayers;j++){ var L=C.layer(j); if(skip[L.name]) continue; if(L.parent==null) L.parent=cam; }
K(tr(cam).property("ADBE Position"),P.campos);
K(tr(cam).property("ADBE Scale"),P.camsc.map(function(k){return [k[0],[k[1],k[1]]];}));
%(extra)s
writeLn("ok "+P.name+" layers="+C.numLayers);
"""

# T26: template's own timeline layers re-spaced + re-keyed (adapted from Aviation timeline_pass.py)
JSX_TL_EXTRA = r"""
function off(p){ try{p.expressionEnabled=false;}catch(e){} }
function clr(p){ for(var k=p.numKeys;k>=1;k--) p.removeKey(k); }
function has(n){ try{ return C.layer(n)!=null; }catch(e){ return false; } }
var p=P.tl, S=0; while(has("Node "+(S+1))) S++;
var x1=tr(C.layer("Node 1")).property("ADBE Position").value[0], xS=tr(C.layer("Node "+S)).property("ADBE Position").value[0];
var N=p.nodes.length, fr=[], xa=x1+p.inset, xb=xS-p.inset;
var rl=C.layer("Rail").property("ADBE Root Vectors Group").property(1).property("ADBE Vectors Group").property(1);
var rsz=rl.property("ADBE Vector Rect Size").value, rps=rl.property("ADBE Vector Rect Position").value;
rl.property("ADBE Vector Rect Size").setValue([xb-xa,rsz[1]]); rl.property("ADBE Vector Rect Position").setValue([(xa+xb)/2,rps[1]]);
var fp=C.layer("Rail Fill").property("ADBE Root Vectors Group").property("Path").property("ADBE Vectors Group").property("ADBE Vector Shape - Group").property("ADBE Vector Shape");
var sh=fp.value, yy=sh.vertices[0][1]; sh.vertices=[[xa,yy],[xb,yy]]; fp.setValue(sh);
for(var i=1;i<=S;i++){
  var nm=(i<10?"0":"")+i, Nd=C.layer("Node "+i), Dt=C.layer("Node Dot "+i), AI=C.layer("Anim Item "+i);
  var Y=C.layer("Year "+nm), Tt=C.layer("Title "+nm), No=has("Note "+nm)?C.layer("Note "+nm):null;
  if(i>N){ Nd.enabled=false; Dt.enabled=false; Y.enabled=false; Tt.enabled=false; if(No) No.enabled=false; continue; }
  var nd=p.nodes[i-1], x=xa+(i-1)*(xb-xa)/(N-1), t=nd.at; fr.push((x-xa)/(xb-xa));
  var items=[Nd,Dt,Y,Tt]; if(No) items.push(No);
  for(var q=0;q<items.length;q++){ var pp=tr(items[q]).property("ADBE Position"); var v=pp.value; off(pp); clr(pp); pp.setValue([x,v[1]+(q>=2?p.dy:0),0]); }
  setText(Y,nd.year); setText(Tt,nd.title); if(No){ if(nd.note) setText(No,nd.note); else No.enabled=false; }
  var ys=tr(Y).property("ADBE Scale"); off(ys); ys.setValue([p.zy,p.zy,100]);
  tr(Tt).property("ADBE Scale").setValue([p.zt,p.zt,100]);   // template's width-fit expression stays on (caps at 365 px * zt)
  var s1=tr(Nd).property("ADBE Scale"), s2=tr(Dt).property("ADBE Scale"); clr(s1); clr(s2); off(s1); off(s2);
  for(var f=0;f<=14;f++){ var u=f/14, b=P.back(u); s1.setValueAtTime(Math.max(0,t-0.06)+u*0.42,[b*100,b*100,100]); }
  for(var f=0;f<=14;f++){ var u=f/14, b=P.back(u); s2.setValueAtTime(Math.max(0,t+0.02)+u*0.42,[b*100,b*100,100]); }
  var ap=tr(AI).property("ADBE Position"), a0=ap.numKeys?ap.keyValue(1):ap.value; clr(ap); off(ap);
  for(var f=0;f<=14;f++){ var u=f/14, e=1-Math.pow(1-u,3); ap.setValueAtTime(Math.max(0,t-0.06)+u*0.45,[a0[0]*(1-e),a0[1]*(1-e),0]); }
  var list=[Y,Tt]; if(No) list.push(No);
  for(var q=0;q<list.length;q++){ var op=tr(list[q]).property("ADBE Opacity"); clr(op); off(op);
    for(var f=0;f<=6;f++){ var u=f/6; op.setValueAtTime(Math.max(0,t-0.06)+u*0.2,100*(1-Math.pow(1-u,3))); } }
}
var te=C.layer("Rail Fill").property("ADBE Root Vectors Group").property("Path").property("ADBE Vectors Group").property("ADBE Vector Filter - Trim").property("ADBE Vector Trim End");
clr(te); off(te); te.setValueAtTime(0,0);
for(var i=1;i<N;i++){ var ta=p.nodes[i-1].at+0.1, tb=p.nodes[i].at-0.06; if(tb-ta>1.1) ta=tb-1.1;
  for(var f=0;f<=20;f++){ var u=f/20, e=(u<.5?4*u*u*u:1-Math.pow(-2*u+2,3)/2); te.setValueAtTime(ta+u*(tb-ta),(fr[i-1]+(fr[i]-fr[i-1])*e)*100); } }
"""


def back_js():
    return "function(x){x=Math.max(0,Math.min(1,x));x-=1;return 1+2.6*x*x*x+1.6*x*x;}"


# ---------------------------------------------------------------- shared chart geometry
X0 = 200.0           # bar left edge
VMAX = 144486.0
WMAX = 1300.0        # px for Peltola's 144,486
def px(v): return WMAX * v / VMAX


def chrome(label, title, sub):
    return dict(label=label, title=title, sub=sub)


def source_tag(S, s=SRC, t0=0.9):
    S.text("source", "Source: " + s, 200, 938, 20, "Inter-Medium", MUTED, 0.0, S.fade(t0, 0.5))


def row_name(S, key, s, y, t0, t1=None, col=INK):
    S.text("name " + key, s, X0, y - BH / 2 - 26, 30, "Inter-SemiBold", col, 0.0, S.fade(t0 - 0.06, 0.3, t1))


BH = 84


# ---------------------------------------------------------------- N17
def shot_N17():
    S = Scene("N17", "B17"); b = "B17"
    S.chrome = chrome("THE MATH", "Alaska US Senate, 2026", "Unofficial count, every precinct reporting")
    yP, yS = 560, 760
    tP, tPn, tPc = W(b, "Peltola"), W(b, "144,486"), W(b, "50.1")
    tS, tSn, tG, tGn = W(b, "Sullivan"), W(b, "131,965."), W(b, "gap"), W(b, "12,521")
    for k, y in (("P", yP), ("S", yS)):
        S.bar("track " + k, X0, y, BH, px(VMAX), TRACK, S.fade(0.7 + (0.12 if k == "S" else 0), 0.5))
    # Peltola
    row_name(S, "P", "Mary Peltola (D)", yP, tP)
    S.bar("bar P", X0, yP, BH, lambda t: px(144486) * eo((t - tP + 0.02) / 0.85), BLUE, S.fade(tP - 0.02, 0.08))
    S.pop("val P", "144,486", X0 + px(144486) - 28, yP, 46, tPn, ("144,486", tPn), "Inter-Bold", CARD, 1.0, rise=10)
    S.pop("pct P", "50.1%", X0 + px(144486) + 30, yP, 60, tPc, ("50.1 percent", tPc), "Inter-ExtraBold", BLUE, 0.0)
    # Sullivan
    row_name(S, "S", "Dan S. Sullivan (R)", yS, tS)
    S.bar("bar S", X0, yS, BH, lambda t: px(131965) * eo((t - tS + 0.02) / 0.85), RED, S.fade(tS - 0.02, 0.08))
    S.pop("val S", "131,965", X0 + px(131965) - 28, yS, 46, tSn, ("131,965", tSn), "Inter-Bold", CARD, 1.0, rise=10)
    # gap: amber fills the track remainder, guide from Peltola's bar end, label
    xa, xb = X0 + px(131965), X0 + px(144486)
    S.bar("gap fill", lambda t: xa, yS, BH, lambda t: (xb - xa) * eio((t - tG) / 0.5), AMBER, S.fade(tG, 0.06), rnd=6)
    S.rect("gap guide", xb - 1.5, (yP + yS) / 2, 3, lambda t: (yS - yP) * eio((t - tG) / 0.5), INK, S.fade(tG, 0.15), rnd=0)
    S.pop("gap lbl", "GAP", xb + 30, yS - 26, 24, tGn - 0.08, None, "Inter-Bold", MUTED, 0.0, rise=8, track=120)
    S.pop("gap val", "12,521", xb + 30, yS + 18, 56, tGn, ("12,521", tGn), "Inter-ExtraBold", INK, 0.0)
    source_tag(S)
    S.cam = drift_cam(S.D)
    return S


# ---------------------------------------------------------------- N18 / N20 three-row layout
Y1, Y2, Y3 = 520, 690, 862
BH3 = 74


def base_rows(S, sullivan_extra=0.0, t_in=0.55):
    """Peltola + Sullivan rows established (already shown in N17) with the template intro"""
    for k, y, d in (("P", Y1, 0), ("S", Y2, 0.1)):
        S.bar("track " + k, X0, y, BH3, px(VMAX), TRACK, S.fade(t_in + d, 0.45))
    S.text("name P", "Mary Peltola (D)", X0, Y1 - BH3 / 2 - 24, 30, "Inter-SemiBold", INK, 0.0, S.fade(t_in, 0.4))
    S.bar("bar P", X0, Y1, BH3, lambda t: px(144486) * eo((t - t_in) / 0.9), BLUE, S.fade(t_in, 0.1))
    S.text("val P", "144,486", X0 + px(144486) - 26, Y1, 42, "Inter-Bold", CARD, 1.0, S.fade(t_in + 0.75, 0.3))
    S.bar("bar S", X0, Y2, BH3, lambda t: px(131965) * eo((t - t_in - 0.1) / 0.9), RED, S.fade(t_in + 0.1, 0.1))


def slide(t, t0, dur, a, b):
    return lerp(a, b, eio((t - t0) / dur))


def shot_N18():
    S = Scene("N18", "B18"); b = "B18"
    S.chrome = chrome("THE MATH", "Give him every vote", "Votes, unofficial count")
    base_rows(S)
    S.text("name S", "Dan S. Sullivan (R)", X0, Y2 - BH3 / 2 - 24, 30, "Inter-SemiBold", INK, 0.0, S.fade(0.65, 0.4))
    sval = lambda t: 100 * eo((t - 1.35) / 0.3)
    S.text("val S", "131,965", X0 + px(131965) - 26, Y2, 42, "Inter-Bold", CARD, 1.0, sval)
    tD, tN, tGive, tStill = W(b, "Daniel"), W(b, "4,765"), W(b, "Give"), W(b, "still")
    S.bar("track D", X0, Y3, BH3, px(VMAX), TRACK, S.fade(0.75, 0.45, tGive + 0.2, 0.6))
    S.text("name D", "Daniel J. Sullivan Jr.", X0, Y3 - BH3 / 2 - 24, 30, "Inter-SemiBold", INK, 0.0,
           S.fade(max(0.5, tD), 0.35, tGive + 0.2, 0.6))
    wD = px(4765); xs_end = X0 + px(131965)
    bx = lambda t: slide(t, tGive, 0.85, X0, xs_end)
    by = lambda t: slide(t, tGive + 0.55, 0.6, Y3, Y2)
    S.bar("block D", bx, by, BH3, lambda t: wD * eo((t - tN + 0.06) / 0.35), G_DJ, S.fade(tN - 0.06, 0.06), rnd=4)
    # value: right of the block on its own row -> above the block once it sits on Sullivan's bar
    lx = lambda t: lerp(bx(t) + wD + 22, bx(t) + wD / 2 - 58, eio((t - tGive) / 1.1))
    ly = lambda t: lerp(by(t), Y2 - BH3 / 2 - 30, eio((t - tGive) / 1.1))
    axf = 0.0
    S.pop("val D", "4,765", lx, ly, 40, tN, ("4,765", tN), "Inter-ExtraBold", G_DJ, 0.0)
    # same label re-anchored centre once it docks (crossfade, so the text never jumps)
    xe = X0 + px(VMAX)
    xr = xs_end + wD
    S.bar("short fill", lambda t: xr, Y2, BH3, lambda t: (xe - xr) * eio((t - tStill + 0.06) / 0.45), AMBER, S.fade(tStill - 0.06, 0.06), rnd=4)
    S.rect("short guide", xe - 1.5, (Y1 + Y2) / 2, 3, lambda t: (Y2 - Y1) * eio((t - tStill) / 0.45), INK, S.fade(tStill - 0.06, 0.15), rnd=0)
    S.pop("short lbl", "STILL SHORT", xe + 28, Y2 - 24, 24, tStill, None, "Inter-Bold", MUTED, 0.0, rise=8, track=120)
    S.pop("short val", "7,756", xe + 28, Y2 + 20, 56, tStill + 0.1, ("7,756 (voice: 'still loses' / 'more than 7,700' @%.2f)" % W(b, "7,700."), W(b, "loses")), "Inter-ExtraBold", INK, 0.0)
    source_tag(S)
    S.cam = drift_cam(S.D)
    return S


def shot_N20():
    S = Scene("N20", "B20"); b = "B20"
    S.chrome = chrome("THE MATH", "Hand him every vote", "Votes, unofficial count")
    base_rows(S)
    tAddD, tG, tHand, tShort, tN = W(b, "Add", 1), W(b, "Gerald"), W(b, "Hand"), W(b, "short"), W(b, "1,651")
    tPel, tWon, tEvery, tWI, tComb = W(b, "Peltola"), W(b, "won"), W(b, "every", 1), W(b, "write-in"), W(b, "combined.")
    xs = X0 + px(131965); wD, wH, wW = px(4765), px(6105), px(886)
    xe = X0 + px(VMAX)
    nameS_out = tEvery
    S.text("name S", "Dan S. Sullivan (R)", X0, Y2 - BH3 / 2 - 24, 30, "Inter-SemiBold", INK, 0.0, S.fade(0.65, 0.4, nameS_out, 0.35))
    S.pop("name E", "Everyone else, combined", X0, Y2 - BH3 / 2 - 24, 30, nameS_out + 0.2, None, "Inter-SemiBold", INK, 0.0, rise=6)
    S.text("val S", "131,965", xs - 26, Y2, 42, "Inter-Bold", CARD, 1.0, S.fade(1.35, 0.3, nameS_out, 0.35))
    # "everyone else": Sullivan's red turns neutral when the row stops being one candidate
    for e in S.els:
        if e["name"] == "bar S":
            e["col"] = lambda t: [lerp(RED[j], [0.36, 0.35, 0.40][j], eio((t - nameS_out) / 0.5)) for j in range(3)]
    # Daniel J. block already docked (state from N18), label below the bar
    S.bar("block D", xs, Y2, BH3, lambda t: wD * eo((t - 0.75) / 0.6), G_DJ, S.fade(0.75, 0.06), rnd=4)
    S.text("val D", "+4,765", xs + wD / 2, Y2 + BH3 / 2 + 30, 32, "Inter-ExtraBold", G_DJ, 0.5, S.fade(1.0, 0.35, nameS_out, 0.35))
    # Heikes: appears on his row at "Gerald", slides onto the end at "Hand"
    S.bar("track H", X0, Y3, BH3, px(VMAX), TRACK, S.fade(tAddD + 0.9, 0.4, tHand + 0.3, 0.6))
    S.text("name H", "Gerald Heikes", X0, Y3 - BH3 / 2 - 24, 30, "Inter-SemiBold", INK, 0.0, S.fade(tG - 0.06, 0.3, tHand + 0.3, 0.6))
    hx = lambda t: slide(t, tHand, 0.85, X0, xs + wD)
    hy = lambda t: slide(t, tHand + 0.55, 0.6, Y3, Y2)
    S.bar("block H", hx, hy, BH3, lambda t: wH * eo((t - tG + 0.06) / 0.35), G_HK, S.fade(tG - 0.06, 0.06), rnd=4)
    hlx = lambda t: lerp(hx(t) + wH + 22, hx(t) + wH / 2 - 66, eio((t - tHand) / 1.1))
    hly = lambda t: lerp(hy(t), Y2 - BH3 / 2 - 30, eio((t - tHand) / 1.1))
    S.pop("val H", "+6,105", hlx, hly, 32, tG, ("6,105 (voice: 'Add Gerald Hikes')", tG), "Inter-ExtraBold", G_HK, 0.0,
          out=(nameS_out, 0.35))
    # 1,651 short: camera pushes onto the bar ends
    xr = xs + wD + wH
    S.bar("short fill", lambda t: xr, Y2, BH3, lambda t: (xe - xr) * eio((t - tShort) / 0.4), AMBER, S.fade(tShort - 0.04, 0.05, tPel, 0.4), rnd=3)
    S.rect("short guide", xe - 1.5, (Y1 + Y2) / 2, 3, lambda t: (Y2 - Y1) * eio((t - tShort) / 0.45), INK, S.fade(tShort, 0.15, tPel, 0.4), rnd=0)
    S.pop("short lbl", "SHORT BY", xe + 26, Y2 - 22, 22, tShort, None, "Inter-Bold", MUTED, 0.0, rise=8, track=120, out=(tPel, 0.4))
    S.pop("short val", "1,651", xe + 26, Y2 + 18, 50, tN, ("1,651", tN), "Inter-ExtraBold", INK, 0.0, out=(tPel, 0.4))
    # write-ins dock at "write-in", combined total pops at "combined"
    S.bar("block W", lambda t: xr, Y2, BH3, lambda t: wW * eo((t - tWI) / 0.3), G_WI, S.fade(tWI - 0.04, 0.05), rnd=2)
    S.pop("val W", "+886 write-ins", xr + wW / 2, Y2 + BH3 / 2 + 30, 28, tWI, ("886 write-ins (voice: 'every write-in')", tWI), "Inter-Bold", MUTED, 0.5, rise=8)
    S.pop("val E", "143,721", xe + 26, Y2, 52, tComb, ("143,721 (voice: 'combined')", tComb), "Inter-ExtraBold", INK, 0.0)
    for e in S.els:
        if e["name"] == "val P":
            e["op"] = S.fade(0.55 + 0.75, 0.3, tWon - 0.06, 0.2)
    S.pop("val P2", "144,486", xe + 26, Y1, 52, tWon, ("144,486 emphasis (voice: 'Peltola won more votes')", tWon), "Inter-ExtraBold", BLUE, 0.0)
    source_tag(S)
    # camera: slow drift, push to 1.9x on the bar ends for the 1,651 gap, back out at "Peltola"
    base = drift_cam(S.D)
    F_in, z_in = (1290, 650), 1.9
    def cam(t):
        z0, fx0, fy0, sx0, sy0 = base(t)
        e = eio((t - (tShort - 1.45)) / 1.3) * (1 - eio((t - tPel) / 1.2))
        return z0 * lerp(1, z_in, e), lerp(fx0, F_in[0], e), lerp(fy0, F_in[1], e), lerp(sx0, 900, e), lerp(sy0, 560, e)
    S.cam = cam
    return S


# ---------------------------------------------------------------- N21 Senate seats
def shot_N21():
    S = Scene("N21", "B21"); b = "B21"
    S.chrome = chrome("HISTORIC WIN", "What Peltola's win means", "US Senate, 2026")
    tFirst, t08, tF2, tEl, tDem, t56 = W(b, "first", 1), W(b, "2008,"), W(b, "first", 2), W(b, "elected"), W(b, "Democrats"), W(b, "56-44")
    # left column
    S.rect("mark 1", 209, 500, 18, 18, BLUE, S.fade(tFirst - 0.06, 0.3), rnd=4)
    S.pop("cap 1", "First Democrat since", 236, 500, 32, tFirst, None, "Inter-SemiBold", MUTED, 0.0, rise=8)
    S.pop("yr 1", "2008", 196, 600, 120, t08, ("2008", t08), "Inter-ExtraBold", BLUE, 0.0, rise=20)
    S.rect("rule", 400, 690, 400, 3, TRACK, S.fade(tF2 - 0.3, 0.4), rnd=0)
    S.rect("mark 2", 209, 750, 18, 18, BLUE, S.fade(tF2 - 0.06, 0.3), rnd=4)
    S.pop("cap 2", "First Alaska Native", 236, 750, 44, tF2, ("First Alaska Native", tF2), "Inter-ExtraBold", INK, 0.0, rise=10)
    S.pop("cap 3", "elected to the Senate", 236, 808, 32, tEl, ("elected to the Senate", tEl), "Inter-SemiBold", MUTED, 0.0, rise=8)
    # hemicycle: 100 seats, 5 rows, sorted by angle -> left 56 D, right 44 R
    cx, cy = 1300, 878
    radii = [210, 262, 314, 366, 418]
    per = [14, 17, 20, 23, 26]
    seats = []
    for r, n in zip(radii, per):
        for k in range(n):
            th = math.pi - k * math.pi / (n - 1)
            seats.append((th, r, cx + r * math.cos(th), cy - r * math.sin(th)))
    seats.sort(key=lambda s: (-round(s[0], 6), s[1]))
    for i, (th, r, x, y) in enumerate(seats):
        dem = i < 56
        tin = 0.7 + (math.pi - th) / math.pi * 0.9 + (r - 210) / 208 * 0.12          # template-style intro cascade
        # colour wave from the outside feet toward the boundary, at "Democrats"
        frac = (i / 55.0) if dem else ((99 - i) / 43.0)
        tc = tDem - 0.2 + frac * 0.75
        col = BLUE if dem else RED
        grey = TRACK
        def colf(t, tc=tc, col=col):
            e = eio((t - tc) / 0.25)
            return [lerp(grey[j] * 0.97, col[j], e) for j in range(3)]
        def scf(t, tin=tin, tc=tc):
            return 100 * eback((t - tin) / 0.4) * (1 + 0.18 * math.sin(math.pi * cl((t - tc) / 0.3)))
        S.ellipse(f"seat {i:02d}", round(x, 2), round(y, 2), 36, colf, scf, S.fade(tin, 0.12))
    S.pop("ns lbl", "NEW SENATE", cx, cy - 96, 24, t56 - 0.12, None, "Inter-Bold", MUTED, 0.5, rise=8, track=120)
    S.pop("ns val", "56-44", cx, cy - 26, 86, t56, ("56-44", t56), "Inter-ExtraBold", INK, 0.5)
    S.pop("lg D", "Democrats 56", cx - 314, cy + 54, 26, tDem + 0.1, None, "Inter-Bold", BLUE, 0.5, rise=6)
    S.pop("lg R", "Republicans 44", cx + 314, cy + 54, 26, tDem + 0.3, None, "Inter-Bold", RED, 0.5, rise=6)
    S.text("source", "Seat count per AP race calls", 200, 938, 20, "Inter-Medium", MUTED, 0.0, S.fade(t56, 0.5))
    S.cam = drift_cam(S.D, F=(960, 660))
    return S


# ---------------------------------------------------------------- T26 timeline
def shot_T26():
    S = Scene("T26", "B26"); b = "B26"
    S.chrome = chrome("WHAT NEXT", "What happens next", "Alaska US Senate race, 2026")
    nodes = [dict(year="Nov 25", title="Alaska certifies", at=W(b, "November"), word="November 25"),
             dict(year="Ninth Circuit", title="Erase ruling?", at=W(b, "erase"), word="erase"),
             dict(year="Ninth Circuit", title="Sanctions?", at=W(b, "sanctions."), word="sanctions"),
             dict(year="Separately", title="Criminal probe continues", at=W(b, "criminal"), word="criminal")]
    for n in nodes:
        S.pops.append(dict(label=f"{n['year']} / {n['title']}", pop_start=round(n["at"] - 0.06, 3), legible=round(n["at"] + 0.06, 3),
                           word=n["word"], word_s=round(n["at"], 3), delta=0.06))
    S.tl = dict(nodes=nodes, inset=150, dy=30, zy=115, zt=130)
    S.cam = drift_cam(S.D, F=(960, 640))
    return S


SHOTS = dict(N17=shot_N17, N18=shot_N18, N20=shot_N20, N21=shot_N21, T26=shot_T26)
TL_KEYS = {"T26"}          # shots built on the timeline template (other cases add their keys when they reuse build())

CTL_CHART = {"Background": BG + [1], "Card": CARD + [1], "Title": INK + [1], "Text": INK + [1], "Muted": MUTED + [1],
             "Color 1": BLUE + [1], "Color 2": RED + [1], "Color 3": AMBER + [1], "Color 4": GREEN + [1]}
CTL_TL = {"Background": BG + [1], "Card": CARD + [1], "Title": INK + [1], "Text": INK + [1], "Muted": MUTED + [1],
          "Color 1": BLUE + [1], "Color 2": [0.86, 0.58, 0.0, 1], "Color 3": [0.86, 0.58, 0.0, 1], "Color 4": RED + [1]}
OFF_CHART = [f"{a} 0{i}" for i in range(1, 6) for a in ("Value", "Label", "Bar")] + [f"Track {i}" for i in range(1, 6)]


def tile(out, files, cols=2, w=960, h=540):
    n = len(files)
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for f in files:
        cmd += ["-i", f]
    fc = "".join(f"[{i}:v]scale={w}:{h}[s{i}];" for i in range(n)) + "".join(f"[s{i}]" for i in range(n))
    fc += f"xstack=inputs={n}:layout=" + "|".join(f"{(i % cols) * w}_{(i // cols) * h}" for i in range(n))
    subprocess.run(cmd + ["-filter_complex", fc, out], check=True)


def build(key, frames=None, render=True):
    S = SHOTS[key]()
    n = S.N + 6                                       # comp a few frames long; output trimmed to exactly S.N
    dur = round(n / FPS, 4)
    work = FX / "work" / f"num_{key}"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    is_tl = key in TL_KEYS
    base = TLINE if is_tl else CHART
    proj = work / f"{key}.ecproj"
    shutil.copy(base, proj)
    campos, camsc = cam_keys(S.cam, n)
    P = dict(name=key, dur=dur, pre=0.2, tpl="01 Company Story 16x9" if is_tl else "02 Top Markets 16x9",
             ctl=CTL_TL if is_tl else CTL_CHART, off=[] if is_tl else OFF_CHART,
             label=S.chrome["label"], title=S.chrome["title"], sub=S.chrome["sub"],
             els=[] if is_tl else compile_scene(S, n), campos=campos, camsc=camsc)
    extra = ""
    if is_tl:
        P["tl"] = S.tl
        extra = JSX_TL_EXTRA
    pj = json.dumps(P)
    if is_tl:
        pj = pj[:-1] + ', "back": ' + back_js() + "}"
    (work / f"{key}.jsx").write_text(JSX_CHART % dict(p=pj, extra=extra))
    r = run([EC, "script", str(work / f"{key}.jsx"), str(proj), "--save"])
    print(key, r.stdout.strip()[-400:], r.stderr.strip()[-600:])
    if r.returncode or "ok " not in r.stdout:
        sys.exit("jsx failed")
    specd = CASE / "edit/specs"; specd.mkdir(parents=True, exist_ok=True)
    qc = CASE / "edit/qc"; qc.mkdir(parents=True, exist_ok=True)
    meta = dict(shot=key, beat=S.beat, beat_dur=round(S.D, 4), frames=S.N, template=("timeline_flat_dataviz 1a546449 comp '01 Company Story 16x9'" if is_tl else "chart_flat_dataviz 404f4682 comp '02 Top Markets 16x9'"),
                chrome=S.chrome, pops=S.pops, texts=[e["s"] for e in S.els if e["kind"] == "text"] + ([f"{n['year']} | {n['title']}" for n in S.tl["nodes"]] if is_tl else []),
                source=SRC if key in ("N17", "N18", "N20") else ("per AP race calls" if key == "N21" else ""))
    (specd / f"num_{key}.json").write_text(json.dumps(meta, indent=1))
    if frames:
        ec.frames(str(proj), [(key, float(t), str(work / f"f_{t}.png")) for t in frames], ms=1920)
        fl = [str(work / f"f_{t}.png") for t in frames]
        tile(str(work / "frames_tile.png"), fl)
        print("frames:", work / "frames_tile.png")
        return
    if not render:
        return
    raw = work / f"{key}_raw.mp4"
    ec.render(str(proj), key, str(raw))
    out = CASE / f"edit/seg/{key}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-vf", "scale=1920:1080,fps=30,format=yuv420p",
                    "-frames:v", str(S.N), "-an", "-c:v", "h264_videotoolbox", "-q:v", "72", "-allow_sw", "0", "-movflags", "+faststart", str(out)], check=True)
    nf = int(run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", str(out)]).stdout.strip())
    j = run(["python3", str(FX / "judder_check.py"), str(out)]).stdout.strip()
    # tile: 8 frames at the pop moments + start/end
    ts = sorted(set([0.4] + [min(S.D - 0.05, p["word_s"] + 0.45) for p in S.pops] + [S.D - 0.1]))
    if len(ts) > 8:
        idx = [round(i * (len(ts) - 1) / 7) for i in range(8)]
        ts = [ts[i] for i in idx]
    while len(ts) < 8:
        ts.append(S.D * (len(ts) + 0.5) / 8)
    ts = sorted(ts)
    tf = []
    for i, t in enumerate(ts):
        f = work / f"tile_{i}.png"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(out), "-frames:v", "1", "-vf", "scale=960:540", str(f)])
        tf.append(str(f))
    tile(str(qc / f"{key}_tile.png"), tf)
    meta.update(out=str(out.relative_to(ROOT)), out_frames=nf, judder=j, tile_times=[round(t, 2) for t in ts])
    (qc / f"{key}_num.json").write_text(json.dumps(meta, indent=1))
    (specd / f"num_{key}.json").write_text(json.dumps(meta, indent=1))
    print("wrote", out, "frames", nf, "/", S.N, "|", j)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    fr = a[a.index("--frames") + 1].split(",") if "--frames" in a else None
    keys = list(SHOTS) if a[0] == "all" else a[0].split(",")
    for k in keys:
        build(k, fr, "--no-render" not in a)
