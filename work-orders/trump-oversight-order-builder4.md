# WO — trump-oversight-order / builder v4 (graphics + assembly, GPU) / 2026-11-23
Run: tools/role.sh builder work-orders/trump-oversight-order-builder4.md

## Inputs (on disk)
- cases/trump-oversight-order/edit/shotmap_v4.tsv (approved; QC block at the end all PASS) + edit/shotmap_v4_build.py
- cases/trump-oversight-order/edit_plan_v4.json, audio_full_v4/B*.wav + words.json, script-full-v4.md
- edit/cap/*.png + .json (real page captures with DOM rects), assets/clips/*, assets/envato/*, kho/stock/*
- Graphics tools: tools/fx/doc_pass.py (doc_highlighter), tools/fx/num_pass.py (chart/timeline/election), tools/fx/post_pass.py,
  tools/fx/capture_pass.py, kho/envato_templates/* (.ecproj, licensed), ../Aviation/tools/effectcraft-cli.sh (MECH plate)
- edit/full.py (v3 assembler: GPU h264_videotoolbox encode, -hwaccel videotoolbox, thread pool JOBS=6, no top-left cards)
- ../Aviation/docs/AVIATION_VISUAL_LANGUAGE.md (motion grammar for DOC, WEBSCROLL, SPLIT, TL, MECH, KSTAT, MATCHCUT)

## Task
1. Render each of the 14 template sequences in the shot-map's TEMPLATE LEDGER -> edit/seg4/<seg>_<n>.mp4, 1920x1080 30 fps,
   exact row durations, highlight/marker landing on the spoken word (words.json, ±0.3 s), proof frames start/action/end in
   edit/qc4/. Highlights from the capture .json DOM rects, applied at original resolution, one strip per real line.
   Encode with h264_videotoolbox -q:v 72 (never libx264). Run independent renders in parallel (<= 6).
2. ANNOT (B17, Y0OOeTYQCRo): NO circle, NO red ring (owner bans circling). Use run -> hold -> coordinate zoom to the post text
   -> yellow highlighter strip on the exact words -> release.
3. No typed text anywhere except what is inside real evidence; no lower thirds, no top-left cards, no labels.
4. Copy edit/full.py -> edit/full_v4.py driven by shotmap_v4.tsv / edit_plan_v4.json / audio_full_v4; reuse the fseg cache
   (same src+window+crop = same file; do not --force). Output output/trump-oversight-order-v2_nocap.mp4,
   edit/full_shots_v4.tsv, edit/words_abs_v4.json (VO words realigned to script-full-v4 text with difflib per segment,
   clip words from the clip SRTs; strip quote chars; Trump K4 says "donors").
5. Captions: python3 tools/fx/captions.py edit/words_abs_v4.json edit/caps_v4.ass --hot "100,000,258,56,4712" then
   /opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -i ..._nocap.mp4 -vf "ass=edit/caps_v4.ass:fontsdir=kho/fonts/Inter"
   -c:v h264_videotoolbox -b:v 14M -c:a copy -movflags +faststart output/trump-oversight-order-v2.mp4
6. QC: edit/qc4/sheet_*.jpg (1 frame / 3 s), print placeholders (must be 0), footage %, cuts/min, LUFS (-16 ±1).

## DONE-WHEN
- output/trump-oversight-order-v2.mp4 exists, placeholders 0, duration = sum of parts ±0.1 s, all 14 templates rendered
  (list file per ledger row), 0 circles.

OUTPUT: cases/trump-oversight-order/edit/full_v4.py
OUTPUT: output/trump-oversight-order-v2.mp4
