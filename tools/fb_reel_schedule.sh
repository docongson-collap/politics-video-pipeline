#!/usr/bin/env bash
# Schedule one FB reel from the Politics profile (ShardBrowser "Facebook", started via shard_fb_cdp.py start).
# usage: tools/fb_reel_schedule.sh REEL.mp4 CAPTION_FILE "Nov 24, 2026" "9:00 AM"
# Date/time are in the BROWSER timezone (profile = America/Los_Angeles).
set -e
cd "/Volumes/WORK/Auto Film Factory/Politics"
PY=~/.hermes/hermes-agent/venv/bin/python
T="timeout 90 $PY tools/shard_fb_cdp.py"
q() { "$@" 2>&1 | grep -v '^health' || true; }
btn() { # click a dialog button whose aria-label/text matches regex $1
  local xy
  xy=$($T eval "(()=>{const b=[...document.querySelectorAll('[role=dialog] [role=button]')].filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&r.x>=0}).find(e=>new RegExp('$1').test((e.getAttribute('aria-label')||e.innerText||'').trim()));if(!b)return 'none';const r=b.getBoundingClientRect();return Math.round(r.x+r.width/2)+' '+Math.round(r.y+r.height/2)})()" 2>&1 | grep -v '^health' | tr -d '"')
  [ "$xy" = "none" ] && { echo "NO BUTTON $1"; exit 3; }
  q $T click $xy; sleep "${2:-4}"
}
q $T fresh
q $T nav https://www.facebook.com/me 12
q $T files 'input[type=file][accept^="image/*,image/heif,image/heic,video"]' "$1"
sleep 15
# FB keeps an unsent composer as a draft: clear the box before typing. NEVER press Escape here, it closes the composer.
q $T eval '(()=>{const d=[...document.querySelectorAll("[role=dialog][aria-label=\"Create post\"]")].find(d=>d.querySelector("[role=textbox]"));const x=d.querySelector("[role=textbox]");x.focus();document.execCommand("selectAll");document.execCommand("delete");return x.innerText.trim().length})()'
CAP=$(python3 -c "import sys;print(open(sys.argv[1]).read().strip().replace(chr(10),'\\\\n'))" "$2")
q $T paste "$CAP "
sleep 2
GOT=$($T eval '(()=>{const d=[...document.querySelectorAll("[role=dialog][aria-label=\"Create post\"]")].find(d=>d.querySelector("[role=textbox]"));return d.querySelector("[role=textbox]").innerText.trim().slice(-50)})()' 2>&1 | grep -v '^health')
echo "caption tail: $GOT"
btn '^Next$' 6
btn '^Next$' 5
btn '^Scheduling options' 4
q $T eval '(()=>{const i=[...document.querySelectorAll("[role=dialog] input[role=combobox]")][0];i.focus();i.select();return 1})()'
q $T type "$3"; q $T key Tab; sleep 1
q $T eval '(()=>{const i=[...document.querySelectorAll("[role=dialog] input[role=combobox]")][1];i.focus();i.select();return 1})()'
q $T type "$4"; q $T key Tab; sleep 1
q $T eval '(()=>[...document.querySelectorAll("[role=dialog] input[role=combobox]")].map(i=>i.value).join(" "))()'
btn '^Schedule for later$' 3
q $T eval '(()=>[...document.querySelectorAll("[role=dialog] [role=button]")].map(e=>(e.getAttribute("aria-label")||"")).filter(s=>/^Scheduling options/.test(s)))()'
btn '^Schedule$' 3
for i in 1 2 3 4 5 6 7 8 9 10; do
  s=$($T eval '[...document.querySelectorAll("[role=dialog]")].map(d=>d.getAttribute("aria-label")).join(",")' 2>&1 | grep -v '^health')
  echo "$s" | grep -q "Reel settings\|Create post" || { echo "DONE (dialogs: $s)"; exit 0; }
  sleep 8
done
echo "STILL OPEN: $s"; exit 4
