#!/usr/bin/env python3
"""PRESS look (Politics) — Envato 'Editorial News Match Cut' (a8d88afb) rendered natively in EffectCraft.
Adapted from Aviation/737-900er/v1/edit/press_pass.py (style "paper" = comp "Match Cut 1", newspaper front page + yellow marker)
and Economic/russia-economy/studio/fx/F3_pass.py (style "web" = comp "Match Cut 19", clean web-article page).
The template's 0.17 s match-cut comp is extended to the card length, filler texts/rules switched off, fonts swapped to system
fonts EffectCraft has (Tinos/DM Serif missing), marker = template 'Shape 1' wiped left->right by scale X.
Outlet names are PLAIN TEXT (kicker), never a faked logo. Headlines must be verbatim (spec "url" = source).

usage: press_pass.py <spec.json> [--frame t,t,..]       (writes <case>/edit/seg/<name>.mp4 (+ _vo.mp4 with the voice slice))
spec: {"name":"P1_press", "case":"alaska-doj-surrender", "beat":"B2", "t0":0.0, "t1":4.32,      # window in beat seconds
       "style":"paper"|"web", "outlet":"CNN", "kicker":"POLITICS", "date":"OCTOBER 23, 2026",
       "headline":"...", "mark":"Trump DOJ sues to block",   # mark must be a PREFIX of headline
       "lines":["rest line 1","rest line 2"],                    # optional manual wrap of the rest (web: rest of line 1 first)
       "mark_word":"lawsuit", "mark_dur":0.7,                    # marker sweep starts on this spoken word (words.json)
       "dek":"verbatim deck/lead (web)", "byline":"...", "credit":"Source: ...", "url":"https://..."}
Gate: python3 tools/fx/judder_check.py <mp4> -> 0 ; tile 8 frames and look."""
import json, re, shutil, subprocess, sys, textwrap
from pathlib import Path

FX = Path(__file__).resolve().parent
ROOT = FX.parents[1]
sys.path.insert(0, str(FX))
import ec  # noqa  (lock-aware EffectCraft calls; lock dir tools/fx/.eclock)
EC = ec.EC
BASE = ROOT / "kho/envato_templates/editorial_match_cut/em.ecproj"

JSX = r"""
var P=%(p)s;
function comp(n){for (var i=1;i<=app.project.numItems;i++){var it=app.project.item(i); if(it instanceof CompItem && it.name==n) return it;}}
for (var i=1;i<=app.project.numItems;i++){var c=app.project.item(i); if(!(c instanceof CompItem)) continue; c.frameRate=30;
 for(var j=1;j<=c.numLayers;j++){var ef=c.layer(j).property("ADBE Effect Parade"); if(!ef) continue; for(var e=ef.numProperties;e>=1;e--) if(ef.property(e).matchName=="ADBE Posterize Time") ef.property(e).remove(); } }
var T=comp(P.tcomp); var D=P.dur+0.2; T.duration=D;
function L(n){return T.layer(n);}
function tr(l,n){return l.property("ADBE Transform Group").property(n);}
function noexp(p){ try{ p.expressionEnabled=false; }catch(e){} }
for(var j=1;j<=T.numLayers;j++){var l=T.layer(j); l.outPoint=D; if(l.inPoint>0) l.inPoint=0;}
function vr(p,acc){for(var i=1;i<=p.numProperties;i++){var q=p.property(i); if(q.matchName=="ADBE Vector Shape - Rect") acc.push(q); else if(q.numProperties) vr(q,acc);} return acc;}
function recolor(grp,col){ for(var i=1;i<=grp.numProperties;i++){var q=grp.property(i); if(q.matchName=="ADBE Vector Graphic - Fill"){ var c=q.property("ADBE Vector Fill Color"); noexp(c); c.setValue(col);} else if(q.numProperties) recolor(q,col);} }
function fade(l,t0,t1){var o=tr(l,"ADBE Opacity"); noexp(o); o.setValueAtTime(0,0); o.setValueAtTime(t0,0); o.setValueAtTime(t1,100);}
// yellow marker = template 'Shape 1' rect, wiped left->right by scale X over the text rect r of layer tl
function marker(S1,r,tl,padx,pady,t0,t1,col){
  if(col) recolor(S1.property("ADBE Root Vectors Group"),col);
  var rg0=vr(S1.property("ADBE Root Vectors Group"),[])[0]; var mw=r.width+2*padx, mh=r.height+2*pady;
  var rs=rg0.property("ADBE Vector Rect Size"); noexp(rs); rs.setValue([mw,mh]);
  var rp=rg0.property("ADBE Vector Rect Position"); if(rp){ noexp(rp); rp.setValue([0,0]); }
  var grp=rg0.parentProperty.parentProperty; var gt=grp.property("ADBE Vector Transform Group");
  if(gt){ var gp=gt.property("ADBE Vector Position"); noexp(gp); gp.setValue([0,0]); var ga=gt.property("ADBE Vector Anchor"); noexp(ga); ga.setValue([0,0]); var gs=gt.property("ADBE Vector Scale"); noexp(gs); gs.setValue([100,100]); }
  var tp=tr(tl,"ADBE Position").value; var cx=tp[0]+r.left+r.width/2, cy=tp[1]+r.top+r.height/2;
  noexp(tr(S1,"ADBE Anchor Point")); noexp(tr(S1,"ADBE Position")); noexp(tr(S1,"ADBE Scale")); noexp(tr(S1,"ADBE Opacity"));
  tr(S1,"ADBE Anchor Point").setValue([-mw/2,0]); tr(S1,"ADBE Position").setValue([cx-mw/2,cy]);
  var sc=tr(S1,"ADBE Scale"); sc.setValueAtTime(0,[0,100,100]); sc.setValueAtTime(t0,[0,100,100]); sc.setValueAtTime(t1,[100,100,100]);
  tr(S1,"ADBE Opacity").setValue(100);
  return [cx,cy,mw,mh];
}
var out={};
if(P.style=="paper"){
  // Match Cut 1 (newspaper front page). Global Control null = template camera -> centre the page.
  var G=L("Global Control"); noexp(tr(G,"ADBE Position")); noexp(tr(G,"ADBE Scale")); tr(G,"ADBE Position").setValue([1920,1080]); tr(G,"ADBE Scale").setValue([100,100,100]);
  var keep={"Text A":1,"Text B":1,"Text K":1};
  for(var j=1;j<=T.numLayers;j++){var l=T.layer(j); if(/^Text /.test(l.name) && !keep[l.name]) l.enabled=false; if(/^(PLACEHOLDER|Mask PH|Shape 2)/.test(l.name)) l.enabled=false;}
  for(var k=0;k<P.off.length;k++){ try{L(P.off[k]).enabled=false;}catch(e){} }
  // template paper texture: a 1K square in the middle -> stretch it over the whole page (or switch it off via "off")
  try{ var px=L("Paper003_1K-JPG_Color.jpg"); px.parent=null; noexp(tr(px,"ADBE Position")); noexp(tr(px,"ADBE Scale")); noexp(tr(px,"ADBE Anchor Point"));
    tr(px,"ADBE Anchor Point").setValue([px.source.width/2,px.source.height/2]); tr(px,"ADBE Position").setValue([1920,1080]);
    var sx=100*4000/px.source.width; tr(px,"ADBE Scale").setValue([sx,sx,100]); out.tex=[px.source.width,px.source.height,tr(px,"ADBE Opacity").value,px.blendingMode]; }catch(e){ out.tex=String(e); }
  function setT(l,t,font,size,col,just){var sp=l.property("ADBE Text Properties").property("ADBE Text Document"); noexp(sp);
    var an=l.property("ADBE Text Properties").property("ADBE Text Animators"); while(an && an.numProperties>0) an.property(1).remove();
    var d=sp.value; d.text=t; d.font=font; d.fontSize=size; d.fillColor=col||[0.09,0.09,0.09]; d.applyFill=true; if(just) d.justification=just; sp.setValue(d); noexp(tr(l,"ADBE Position")); return l.sourceRectAtTime(0.1,false);}
  function fitT(l,t,font,size,maxW,col){var r=setT(l,t,font,size,col); if(r.width>maxW){ r=setT(l,t,font,size*maxW/r.width,col);} return r;}
  var A=L("Text A"), B=L("Text B"), K=L("Text K");
  // kicker = outlet as plain text + date (no masthead / no logo)
  var rk=fitT(K,P.kicker,"Georgia-Bold",96,3300); tr(K,"ADBE Position").setValue([-rk.left-rk.width/2,-660-rk.top-rk.height/2]);
  var ra=fitT(A,P.hl,"Georgia-Bold",P.hs,3300); var rb=fitT(B,P.rest,"Georgia-Bold",P.rs,3300);
  var yA=0; tr(A,"ADBE Position").setValue([0,yA]); var yB=yA+ra.top+ra.height+P.gap-rb.top; tr(B,"ADBE Position").setValue([0,yB]);
  var topY=yA+ra.top, botY=yB+rb.top+rb.height;
  var dy=((-520+1000)/2)-((topY+botY)/2);
  tr(A,"ADBE Position").setValue([-ra.left-ra.width/2,yA+dy]); tr(B,"ADBE Position").setValue([-rb.left-rb.width/2,yB+dy]);
  // thin ink rules under the kicker (own shapes)
  function rule(y,w,h,name){var q=T.layers.addShape(); q.name=name; q.parent=G; var gr=q.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group"); var ct=gr.property("ADBE Vectors Group");
    var rc=ct.addProperty("ADBE Vector Shape - Rect"); rc.property("ADBE Vector Rect Size").setValue([w,h]); var fl=ct.addProperty("ADBE Vector Graphic - Fill"); fl.property("ADBE Vector Fill Color").setValue([0.09,0.09,0.09,1]);
    tr(q,"ADBE Position").setValue([0,y]); q.outPoint=D; fade(q,0.0,0.3); return q;}
  rule(-540,3400,10,"Rule 1"); rule(-515,3400,3,"Rule 2"); rule(-800,3400,3,"Rule 0");
  fade(K,0.0,0.3); fade(A,0.1,0.45); fade(B,0.2,0.55);
  out.marker=marker(L("Shape 1"),A.sourceRectAtTime(0.1,false),A,60,30,P.mk0,P.mk1,null);
  out.A=[ra.width,ra.height]; out.B=[rb.width,rb.height]; out.dy=dy;
} else {
  // Match Cut 19 (web article). Bake colours, place verbatim headline lines; A = marked prefix, C = rest of line 1.
  L("CRT RGB").enabled=false;
  function setText(l,t,size,col,font){var tp=l.property("ADBE Text Properties"); var an=tp.property("ADBE Text Animators"); while(an && an.numProperties>0) an.property(1).remove();
    var sp=tp.property("ADBE Text Document"); noexp(sp); var d=sp.value; d.text=t; d.font=font||"Inter-Bold"; d.fontSize=size; d.fillColor=col; d.applyFill=true; d.justification=ParagraphJustification.LEFT_JUSTIFY; sp.setValue(d);
    noexp(tr(l,"ADBE Position")); return l.sourceRectAtTime(0.1,false);}
  var X0=P.x0, INK=P.ink, GREY=P.grey;
  recolor(L("Background Color").property("ADBE Root Vectors Group"),P.paper);
  var nav=L("Shape 2"); recolor(nav.property("ADBE Root Vectors Group"),INK); noexp(tr(nav,"ADBE Opacity"));
  var F=L("Text F"); var rf=setText(F,P.bar,66,[0.957,0.965,0.973,1],"Inter-Bold"); tr(F,"ADBE Position").setValue([X0-rf.left,-680]);
  var E=L("Text E"); var re=setText(E,P.kick,64,P.accent,"Inter-Bold");
  var A=L("Text A"), C=L("Text C"), Dd=L("Text D"), B=L("Text B");
  var ra=setText(A,P.hl,P.hs,INK), rc=setText(C,P.l1,P.hs,INK), rd=setText(Dd,P.l2,P.hs,INK);
  var y1=P.y1, y2=y1+P.lh, y3=y2+P.lh;
  var xa=X0-ra.left, xc=xa+ra.left+ra.width+P.gap-rc.left;
  tr(A,"ADBE Position").setValue([xa,y1]); tr(C,"ADBE Position").setValue([xc,y1]); tr(Dd,"ADBE Position").setValue([X0-rd.left,y2]);
  var yl=y2;
  if(P.l3){ var rb3=setText(B,P.l3,P.hs,INK); tr(B,"ADBE Position").setValue([X0-rb3.left,y3]); yl=y3; fade(B,0.4,0.8); out.l3=rb3.width; } else B.enabled=false;
  tr(E,"ADBE Position").setValue([X0-re.left,y1-P.kgap]);
  var H=L("Text H"); var rh=setText(H,P.dek,P.ls,GREY,"Inter-Medium"); tr(H,"ADBE Position").setValue([X0-rh.left,yl+P.lgap]);
  var Gt=L("Text G"); var rg=setText(Gt,P.by,P.bs,GREY,"Inter-Medium"); tr(Gt,"ADBE Position").setValue([X0-rg.left,yl+P.lgap+rh.height+P.bgap]);
  out.w=[ra.width,rc.width,rd.width,rh.width,rh.height, xc+rc.left+rc.width];
  out.marker=marker(L("Shape 1"),ra,A,P.padx,P.pady,P.mk0,P.mk1,P.marker);
  fade(nav,0.0,0.3); fade(F,0.0,0.3); fade(E,0.1,0.45); fade(A,0.2,0.6); fade(C,0.2,0.6); fade(Dd,0.3,0.7); fade(H,0.5,0.9); fade(Gt,0.6,1.0);
}
// wrapper: the 3840x2160 card at 50 %% with a slow push (continuous motion, no holds)
var W=app.project.items.addComp(P.name,1920,1080,1,P.dur,30);
var C2=W.layers.add(T); C2.startTime=0; C2.inPoint=0; C2.outPoint=P.dur;
var S0=tr(C2,"ADBE Scale"); S0.setValueAtTime(0,[50,50,100]); S0.setValueAtTime(P.dur,[50*(1+P.push),50*(1+P.push),100]);
if(P.credit){ var cr=W.layers.addText(P.credit); var sp2=cr.property("ADBE Text Properties").property("ADBE Text Document"); var d2=sp2.value; d2.font="ArialMT"; d2.fontSize=20; d2.fillColor=[0.37,0.37,0.37]; d2.applyFill=true; d2.justification=ParagraphJustification.LEFT_JUSTIFY; sp2.setValue(d2);
  tr(cr,"ADBE Position").setValue([48,1056]); var co=tr(cr,"ADBE Opacity"); co.setValueAtTime(0.4,0); co.setValueAtTime(0.9,85); }
writeLn("ok "+P.name+" "+JSON.stringify(out));
"""


def words(case, beat):
    return json.load(open(ROOT / f"cases/{case}/audio_full_v1/words.json"))[beat]


def word_t(ws, w):
    n = lambda s: re.sub(r"[^a-z0-9']", "", s.lower().replace("\u2019", "'"))
    for x in ws:
        if n(x["w"]) == n(w):
            return x["s"]
    raise KeyError(w)


def main():
    a = sys.argv[1:]
    fr = a[a.index("--frame") + 1].split(",") if "--frame" in a else None
    s = json.load(open(a[0]))
    case, beat = s["case"], s["beat"]
    t0, t1 = s["t0"], s["t1"]
    dur = round(t1 - t0, 3)
    ws = words(case, beat)
    mk0 = round(word_t(ws, s["mark_word"]) - t0, 3)
    mk1 = round(mk0 + s.get("mark_dur", 0.7), 3)
    head, hl = s["headline"], s["mark"]
    assert head.startswith(hl), "mark must be a prefix of the headline"
    rest = head[len(hl):].strip()
    lines = s.get("lines") or textwrap.wrap(rest, width=max(18, (len(rest) + 1) // 2 + 3))
    assert " ".join([hl] + lines) == head, "lines must rebuild the verbatim headline"
    seg = ROOT / f"cases/{case}/edit/seg"; work = seg / "work"; work.mkdir(parents=True, exist_ok=True)
    name = s["name"]
    if s["style"] == "paper":
        P = dict(name=name, style="paper", tcomp="Match Cut 1", dur=dur, push=s.get("push", 0.05), mk0=mk0, mk1=mk1,
                 kicker=s["kicker"], hl=hl, rest="\r".join(lines), hs=s.get("hs", 250), rs=s.get("rs", 200), gap=s.get("gap", 70),
                 off=s.get("off", []), credit=s.get("credit", ""))
    else:
        P = dict(name=name, style="web", tcomp="Match Cut 19", dur=dur, push=s.get("push", 0.04), mk0=mk0, mk1=mk1,
                 bar=s["bar"], kick=s["kicker"], hl=hl, l1=lines[0], l2=lines[1] if len(lines) > 1 else "", l3=lines[2] if len(lines) > 2 else "",
                 dek="\r".join(textwrap.wrap(s["dek"], s.get("dek_wrap", 60))), by=s["byline"],
                 x0=s.get("x0", -873), y1=s.get("y1", -250), lh=s.get("lh", 140), hs=s.get("hs", 112), gap=s.get("gap", 30),
                 ls=58, lgap=s.get("lgap", 175), bs=50, bgap=70, kgap=170, padx=28, pady=14,
                 ink=[0.078, 0.094, 0.114, 1], grey=[0.369, 0.4, 0.439, 1], paper=[0.976, 0.976, 0.969, 1], accent=[0.80, 0.11, 0.11, 1],
                 marker=[1.0, 0.86, 0.2, 1], credit=s.get("credit", ""))
    proj = work / f"{name}.ecproj"; jsx = work / f"{name}.jsx"
    shutil.copy(BASE, proj)
    jsx.write_text(JSX % dict(p=json.dumps(P)))
    with ec.Lock():
        r = subprocess.run([EC, "script", str(jsx), str(proj), "--save"], capture_output=True, text=True)
    print(r.stdout.strip()[-700:], r.stderr.strip()[-400:], "mk", mk0, mk1)
    if r.returncode:
        sys.exit(1)
    if fr:
        ec.frames(str(proj), [(name, t, str(work / f"{name}_{t}.png")) for t in fr], ms=1920)
        return
    raw = work / f"{name}_raw.mp4"; out = seg / f"{name}.mp4"
    ec.render(str(proj), name, str(raw))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-vf", "scale=1920:1080,fps=30,format=yuv420p", "-an", "-c:v", "h264_videotoolbox",
                    "-q:v", "72", "-allow_sw", "0", "-movflags", "+faststart", "-t", f"{dur:.3f}", str(out)], check=True)
    mux(case, beat, t0, dur, out)


def mux(case, beat, t0, dur, out):
    wav = ROOT / f"cases/{case}/audio_full_v1/{beat}.wav"
    vo = out.with_name(out.stem + "_vo.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(out), "-ss", f"{t0:.3f}", "-t", f"{dur:.3f}", "-i", str(wav), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{dur:.3f}", str(vo)], check=True)
    print("wrote", out, vo)


if __name__ == "__main__":
    main()
