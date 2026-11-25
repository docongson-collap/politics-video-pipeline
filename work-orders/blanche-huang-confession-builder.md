# WO — blanche-huang-confession / builder v1 (assembly + captions) / 2026-11-25
Run: tools/role.sh builder work-orders/blanche-huang-confession-builder.md

## Inputs (on disk)
- cases/blanche-huang-confession/edit/shotmap_v1.tsv (approved, QC PASS) + edit/graphics_index.tsv (rendered graphic segs in
  edit/seg/, durations verified; use <seg>_<t0>.mp4, NOT *_vo.mp4 previews)
- cases/blanche-huang-confession/edit_plan_v1.json (vo B1-B18 + clips K1-K9 with file/in/out/words), audio_full_v1/B*.wav +
  words.json (durations from ffprobe), script-full-v1.md
- assets/clips/*.mp4 + asr/*.srt (K windows; builder word-times each K in/out on the file with whisper so no clipped words —
  pad 0.15 s, never cut mid-word; K1 starts at the reporter's "Mr. Attorney General", not the CBS anchor intro)
- B-roll: cases/trump-nvidia-huang/assets/clips/*, cases/trump-nvidia-huang/assets/envato/<uuid>.mov|.mp4, kho/stock/*
- Working assembler to copy and adapt (don't rewrite): cases/trump-nvidia-huang/edit/full_v1.py, build_words_abs_v1.py
  (GPU h264_videotoolbox, -hwaccel videotoolbox, JOBS=6, fseg cache)
- assets/brand/corner_1920.png (Proof Politics corner logo, whole film)

## Task
1. edit/full_v1.py driven by shotmap_v1.tsv / edit_plan_v1.json / audio_full_v1 -> output/blanche-huang-confession-v1_nocap.mp4,
   1920x1080 30 fps. Footage rows: exact src window, scale/crop to fill, no stretch; keep outlet bugs; crop editorialising chyrons
   (any chyron with "spy" or words not on tape). K clips: original audio; VO rows: VO audio only (footage muted).
   Ken Burns on stills only. No flash/luma spikes at cuts.
2. Sound: no music (same as trump-nvidia-huang, delivered); VO + clip audio, loudnorm -16 LUFS ±1, clip audio matched to VO level.
3. edit/words_abs_v1.json: VO words realigned to script-full-v1 text with difflib per segment (fix ASR spellings: Nvidia, Huang,
   Blanche, Megaspeed, Mediaite, Pod Force One, subpoena, Raskin, Jeffries, Bonta), clip words = the verbatim words in
   edit_plan_v1.json aligned to whisper timing; strip quote chars.
4. Captions: python3 tools/fx/captions.py edit/words_abs_v1.json edit/caps_v1.ass --hot "hundred,million,percent,exonerated,pardon" (numbers are spoken as words) then
   /opt/homebrew/opt/ffmpeg-full/bin/ffmpeg ... "ass=edit/caps_v1.ass:fontsdir=kho/fonts/Inter" -c:v h264_videotoolbox -b:v 14M
   -c:a copy -movflags +faststart output/blanche-huang-confession-v1.mp4 (logo overlay in same pass if not in step 1).
5. QC: edit/qc/sheet_*.jpg (1 frame / 3 s) and LOOK at them; placeholders/black frames 0, logo on 100 % of frames, duration =
   sum of parts ±0.1 s, LUFS, footage %, cuts/min. Print the counts.

## DONE-WHEN (countable)
- output/blanche-huang-confession-v1.mp4 exists; placeholders 0; logo frames 100 %; LUFS -16 ±1; duration check PASS.

OUTPUT: cases/blanche-huang-confession/edit/full_v1.py
OUTPUT: output/blanche-huang-confession-v1.mp4
