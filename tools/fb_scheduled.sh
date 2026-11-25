#!/usr/bin/env bash
# List scheduled posts (Creator Dashboard > Content Library > Scheduled).
cd "/Volumes/WORK/Auto Film Factory/Politics"
PY=~/.hermes/hermes-agent/venv/bin/python; T="timeout 90 $PY tools/shard_fb_cdp.py"
$T nav "https://www.facebook.com/professional_dashboard/content/content_library/" 12 >/dev/null 2>&1
$T eval '(()=>{const t=[...document.querySelectorAll("a,[role=tab],[role=button]")].find(e=>(e.innerText||"").trim()=="Scheduled");t.click();return 1})()' >/dev/null 2>&1
sleep 6
$T eval '(()=>{const m=document.body.innerText.split("Publish date")[1]||"";return m.replace(/\n+/g," | ").slice(0,3000)})()' 2>&1 | grep -v '^health'
