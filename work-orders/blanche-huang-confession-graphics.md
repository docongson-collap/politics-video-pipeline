# WO — blanche-huang-confession / graphics (captures + template renders) / 2026-11-25
Run: tools/role.sh visual work-orders/blanche-huang-confession-graphics.md

## Inputs (on disk)
- cases/blanche-huang-confession/edit/shotmap_v1.tsv (approved: QC block all PASS) + edit/shotmap_v1_build.py
- cases/blanche-huang-confession/audio_full_v1/words.json (markers land ON the spoken word ±0.3 s)
- tools/fx/quote_capture.py, tall_capture.py (inside browser_exec), capture_pass.py, post_pass.py, press_pass.py, num_pass.py,
  doc_pass.py, gfx_gate.py, proof_frames.py; skills/politics-news-pipeline/references/edit-v2-toolkit.md
- Last film's working pipeline to reuse: cases/trump-nvidia-huang/edit/build_graphics.py, make_index.py, spec/*, graphics_index.tsv
  (same tools; but the LOOK of SPLIT/NUM/DOC/POST must not copy yesterday's film frame-for-frame: different paper/backing,
  different push direction)

## Task
1. Capture the 26 pages named in the shot-map (edit/cap/<ID>.png + .json DOM rects of the marked phrases, DPR 2). Use your own
   browser tab, close it after; never touch owner's open tabs. No proxy of any kind (never ShardBrowser). Bot-walled page -> Wayback
   copy -> else alternative mainstream URL for the same verbatim words (ledger) and log in edit/graphics_log.md.
   Phrase not verbatim on the page -> never fake; log it and pick the nearest verbatim line that the voice says.
   No Alice Huang photo and no "spy" word visible in any crop (CNBC Nov 9 headline contains it -> crop below the headline).
2. Render every WEBHEAD / POST / SPLIT / NUM / DOC row -> edit/seg/<seg>_<t0>.mp4, 1920x1080 30 fps, duration = row t1-t0
   (+0.2 s tail), yellow highlighter strip on the exact words as voiced, one strip per real line, coordinates from DOM rects at
   original resolution. Numbers inside evidence = yellow. No typed text, no labels, no circles/red rings/arrows.
   Schumer POST = real x.com capture (or a mainstream outlet embed of the same post if X blocks). Encode h264_videotoolbox
   -q:v 72; run independent renders in parallel (<= 6).
3. edit/graphics_index.tsv: seg | t0 | t1 | file | capture ID | phrase marked | marker time (segment s).
4. edit/qc/graphics_sheet.jpg (one frame per graphic after the marker lands) and LOOK at it: text readable at phone size,
   marker on the right words, no half lines at frame edges, no blank/placeholder frames, no cookie/paywall banners.

## DONE-WHEN (countable)
- graphics_index.tsv has one row per graphic row of the shot-map (WEBHEAD+POST+SPLIT+NUM+DOC = 62) with an existing mp4 whose
  duration >= t1-t0; 0 retyped cards; exceptions logged.

OUTPUT: cases/blanche-huang-confession/edit/graphics_index.tsv
OUTPUT: cases/blanche-huang-confession/edit/qc/graphics_sheet.jpg
