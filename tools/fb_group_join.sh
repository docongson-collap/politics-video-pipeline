#!/usr/bin/env bash
# Join FB groups (Politics profile). usage: tools/fb_group_join.sh URL...
# Prints: joined | pending | questions | member | fail
cd "/Volumes/WORK/Auto Film Factory/Politics"
PY=~/.hermes/hermes-agent/venv/bin/python
T="timeout 60 $PY tools/shard_fb_cdp.py"
for u in "$@"; do
  $T nav "$u" 10 >/dev/null 2>&1; sleep 2
  r=$($T eval '(()=>{const b=[...document.querySelectorAll("[role=button]")].find(e=>/^Join group$|^Join$/.test((e.getAttribute("aria-label")||e.innerText||"").trim()));if(!b){return /Joined|Invite/.test(document.body.innerText.slice(0,4000))?"member":"nojoin"}b.click();return "clicked"})()' 2>&1 | grep -v '^health' | tr -d '"')
  sleep 5
  if [ "$r" = "clicked" ]; then
    r=$($T eval '(()=>{const d=[...document.querySelectorAll("[role=dialog]")].find(d=>/question|Answer|rules/i.test(d.innerText));if(d)return "questions";const t=document.body.innerText.slice(0,5000);return /Cancel request|Pending/.test(t)?"pending":/Joined/.test(t)?"joined":"clicked?"})()' 2>&1 | grep -v '^health' | tr -d '"')
  fi
  echo "$r | $u"
done
