# WO — trump-oversight-order / builder assembly / 2026-11-23
Run: tools/role.sh builder work-orders/trump-oversight-order-builder.md

## Inputs (must exist on disk before dispatch)
- cases/trump-oversight-order/edit/shotmap_v3.tsv (approved shot-map; film_t0 column = absolute time)
- cases/trump-oversight-order/edit_plan_v3.json (VO segments B1-B19 + clips K1-K6 order and windows)
- cases/trump-oversight-order/audio_full_v3/B*.wav + words.json
- cases/trump-oversight-order/assets/clips/*.mp4 (+ .srt), assets/envato/<itemUuid>.mov|.mp4 (all 20 licensed; resolve the
  "Envato itemUuid <uuid>" rows by globbing assets/envato/<uuid>.*), kho/stock/*
- cases/alaska-doj-surrender/edit/full.py + hook.py (proven assembly pattern: shot tables, 30 fps grid snap, minterpolate for
  24/25 fps sources, setpts before scale, fseg cache, per-part loudnorm, KCLIPS lower thirds) — copy, don't import
- skills/politics-news-pipeline/references/edit-v2-toolkit.md "## Assembly"
- Graphics are being rendered in parallel into edit/seg/*.mp4 + edit/graphics_index.tsv (may not exist yet).

## Task
Write cases/trump-oversight-order/edit/full.py (copied pattern) driven by shotmap_v3.tsv:
1. FOOT rows: cut exact src windows -> fseg cache (1920x1080, 30 fps; 4K Envato scaled; 24/25 fps -> minterpolate).
   Rows with text-on-screen (e.g. "100,000 COMPANIES", "NOTIFY", "FILE") -> small clean Inter Black label, top-left,
   white on a dark translucent bar, <= 6 words, lands on the spoken word (words.json) — NOT at the bottom (captions live there).
2. CLIP rows K1-K6: exact edit_plan windows, original audio, outlet bug kept, lower third (speaker, outlet, date) top-left
   for 3 s. K2 NewsNation window 01:01.2-01:14.1.
3. Graphic rows: from edit/graphics_index.tsv when present; until then a black placeholder of the right length labelled
   with the row id (run `--partial` so footage is cached).
4. Audio: VO segments + clip audio in edit_plan order, loudnorm I=-16 per part, exact part lengths; no music bed.
5. Output output/trump-oversight-order-v1_nocap.mp4 (no burned captions yet) + edit/full_shots.tsv (t_abs, dur, seg, shot)
   + edit/words_abs.json: every spoken word with ABSOLUTE film time [{w,s,e}] = VO words.json shifted by part start, plus clip
   words from each clip's whisper (tools: whisper-cli -ml 1 -sow -oj on the clip window) shifted likewise.
6. Burn captions: python3 tools/fx/captions.py edit/words_abs.json edit/caps.ass --hot "100,000,258,56,4712" then
   /opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -i output/trump-oversight-order-v1_nocap.mp4 -vf "ass=edit/caps.ass:fontsdir=kho/fonts/Inter"
   -c:a copy output/trump-oversight-order-v1.mp4 (only after all graphics are real, not placeholders).
7. QC: edit/qc/full_sheet_*.jpg (1 frame / 5 s), print footage %, cuts/min, max consecutive graphics; judder_check.py.

## DONE-WHEN (countable)
- output/trump-oversight-order-v1_nocap.mp4 exists, duration = sum of parts ±0.1 s, 0 placeholder frames (or list which).
- edit/words_abs.json covers VO + all 6 clips; captions burned into output/trump-oversight-order-v1.mp4 if graphics complete.

OUTPUT: cases/trump-oversight-order/edit/full.py
OUTPUT: cases/trump-oversight-order/edit/full_shots.tsv
