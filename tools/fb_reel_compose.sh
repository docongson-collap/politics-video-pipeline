#!/usr/bin/env bash
# Open the FB composer with a reel file + caption, then click Next (stops at "Reel settings").
# usage: tools/fb_reel_compose.sh REEL.mp4 CAPTION_FILE
set -e
cd "/Volumes/WORK/Auto Film Factory/Politics"
PY=~/.hermes/hermes-agent/venv/bin/python
T="timeout 90 $PY tools/shard_fb_cdp.py"
q() { "$@" 2>&1 | grep -v '^health' || true; }
q $T fresh
q $T nav https://www.facebook.com/me 12
q $T files 'input[type=file][accept^="image/*,image/heif,image/heic,video"]' "$1"
sleep 12
q $T eval '(()=>{const d=[...document.querySelectorAll("[role=dialog][aria-label=\"Create post\"]")].find(d=>d.querySelector("[role=textbox]"));d.querySelector("[role=textbox]").focus();return 1})()'
CAP=$(python3 -c "import sys;print(open(sys.argv[1]).read().strip().replace(chr(10),'\\\\n'))" "$2")
q $T paste "$CAP"
sleep 2
q $T eval '(()=>{const d=[...document.querySelectorAll("[role=dialog][aria-label=\"Create post\"]")].find(d=>d.querySelector("[role=textbox]"));return d.querySelector("[role=textbox]").innerText.length})()'
q $T key Escape
XY=$($T eval '(()=>{const b=[...document.querySelectorAll("[role=dialog] [role=button]")].find(e=>(e.getAttribute("aria-label")||e.innerText||"").trim()=="Next");const r=b.getBoundingClientRect();return Math.round(r.x+r.width/2)+" "+Math.round(r.y+r.height/2)})()' 2>&1 | grep -v '^health' | tr -d '"')
q $T click $XY
sleep 5
q $T eval '(()=>[...document.querySelectorAll("[role=dialog] [role=button]")].map(e=>{const r=e.getBoundingClientRect();return (e.getAttribute("aria-label")||e.innerText||"").replace(/\n/g," ").slice(0,40)+"@"+Math.round(r.x+r.width/2)+","+Math.round(r.y+r.height/2)}).filter(s=>/Schedul|Post|Edit|audience/i.test(s)))()'
