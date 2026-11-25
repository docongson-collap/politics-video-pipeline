# WO — trump-nvidia-huang / builder v1 (assembly + captions) / 2026-11-24
Run: tools/role.sh builder work-orders/trump-nvidia-huang-builder.md

## Inputs (on disk)
- cases/trump-nvidia-huang/edit/shotmap_v1.tsv (approved, QC PASS) + edit/graphics_index.tsv (57 rendered graphic segs in
  edit/seg/, durations verified; use <seg>_<t0>.mp4, NOT the *_vo.mp4 previews)
- cases/trump-nvidia-huang/edit_plan_v1.json (B1 K1 B2 B3 B4 B5 K2 B6 K3 B7 B8 K4 B9 B10 B11 K5 B12 B13 B14 B15),
  audio_full_v2/B*.wav + words.json (durations from ffprobe), script-full-v2.md
- assets/clips/*.mp4 + *.srt (K1-K5 windows in assets/clips/clips.tsv), assets/envato/<uuid>.mov|.mp4 (45, licensed — the
  shot-map says .mov; resolve by uuid stem), kho/stock/*
- Last film's working assembler: cases/trump-oversight-order/edit/full_v4.py, build_words_abs_v4.py, finish_v4.sh
  (GPU h264_videotoolbox, -hwaccel videotoolbox, JOBS=6, fseg cache) — copy and adapt, don't rewrite.
- assets/brand/corner_1920.png (Proof Politics corner logo, whole film: -loop 1 -framerate 30 + overlay shortest=1)

## Task
1. edit/full_v1.py driven by shotmap_v1.tsv / edit_plan_v1.json / audio_full_v2 -> output/trump-nvidia-huang-v1_nocap.mp4,
   1920x1080 30 fps. Footage rows: exact src window, scale/crop to fill, no stretch; keep outlet bugs. K clips: original audio,
   VO rows: VO audio only (footage muted). Ken Burns on stills only.
2. Sound: no music (same as trump-oversight-order v2, which was delivered); VO + clip audio, loudnorm to -16 LUFS ±1, clip audio matched to VO level.
3. edit/words_abs_v1.json: VO words realigned to script-full-v2 text with difflib per segment (fix ASR spellings: Nvidia,
   Huang, Ingle, Megaspeed, Faber, Lutnick), clip words from the clip SRTs ("fellas", "him"); strip quote chars.
4. Captions: python3 tools/fx/captions.py edit/words_abs_v1.json edit/caps_v1.ass --hot "25,30,$25" then
   /opt/homebrew/opt/ffmpeg-full/bin/ffmpeg ... "ass=edit/caps_v1.ass:fontsdir=kho/fonts/Inter" -c:v h264_videotoolbox -b:v 14M
   -c:a copy -movflags +faststart output/trump-nvidia-huang-v1.mp4 (logo overlay in the same pass if not done in step 1).
5. QC: edit/qc/sheet_*.jpg (1 frame / 3 s), placeholders/black frames 0, logo present on 100 % of frames (diff the corner
   region over the whole film), duration = sum of parts ±0.1 s, LUFS, footage %, cuts/min. Print the counts.

## DONE-WHEN (countable)
- output/trump-nvidia-huang-v1.mp4 exists; placeholders 0; logo frames 100 %; LUFS -16 ±1; duration check PASS.

OUTPUT: cases/trump-nvidia-huang/edit/full_v1.py
OUTPUT: output/trump-nvidia-huang-v1.mp4
