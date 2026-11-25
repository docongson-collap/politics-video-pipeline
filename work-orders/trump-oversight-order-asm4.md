# WO — trump-oversight-order / assembly v4 (footage + audio + captions) / 2026-11-23
Run: tools/role.sh builder work-orders/trump-oversight-order-asm4.md

## Inputs (on disk)
- cases/trump-oversight-order/edit/shotmap_v4.tsv, edit_plan_v4.json, audio_full_v4/B*.wav + words.json, script-full-v4.md
- edit/full.py (v3 assembler, already GPU: h264_videotoolbox, -hwaccel videotoolbox, ThreadPool JOBS=6, no cards/labels)
- assets/clips/*, assets/envato/*, kho/stock/*; graphics arrive in parallel as edit/seg4/index_{A,B,C,D}.tsv + mp4s

## Task
1. cp edit/full.py edit/full_v4.py; drive it from shotmap_v4.tsv / edit_plan_v4.json / audio_full_v4 (column names may differ
   from v3 — read the header). Footage rows (FOOT-EVT/LOC/SCN) and CLIP rows render into the existing fseg cache.
   Graphic rows: look up edit/seg4/index_*.tsv by seg+t0; missing -> black placeholder (count them in the summary line).
   Output output/trump-oversight-order-v2_nocap.mp4 + edit/full_shots_v4.tsv. Do not --force.
2. edit/words_abs_v4.json: VO words shifted to absolute time and realigned to script-full-v4 text (difflib per segment:
   equal-length replace runs take the script word); clip words from the clip .srt (whisper -ml 1 -sow -oj on the clip window
   if needed); Trump K4 says "donors"; strip quote chars; drop duplicates.
3. python3 tools/fx/captions.py edit/words_abs_v4.json edit/caps_v4.ass --hot "100,000,258,56,4712"
4. Write edit/finish_v4.sh: rerun full_v4.py (picks up graphics), then burn:
   /opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -y -i output/trump-oversight-order-v2_nocap.mp4 -vf "ass=cases/trump-oversight-order/edit/caps_v4.ass:fontsdir=kho/fonts/Inter" -c:v h264_videotoolbox -b:v 14M -c:a copy -movflags +faststart output/trump-oversight-order-v2.mp4
   Run it once at the end only if the placeholder count is 0; otherwise report the count.

## DONE-WHEN
- full_v4.py runs; summary line printed (placeholders N, footage %, cuts/min); words_abs_v4.json + caps_v4.ass exist.

OUTPUT: cases/trump-oversight-order/edit/full_v4.py
OUTPUT: cases/trump-oversight-order/edit/caps_v4.ass
