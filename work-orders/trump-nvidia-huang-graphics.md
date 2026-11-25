# WO — trump-nvidia-huang / graphics (captures + template renders) / 2026-11-24
Run: tools/role.sh visual work-orders/trump-nvidia-huang-graphics.md

## Inputs (on disk)
- cases/trump-nvidia-huang/edit/shotmap_v1.tsv (approved: QC block all PASS) + edit/shotmap_v1_build.py
- cases/trump-nvidia-huang/audio_full_v2/words.json (markers land ON the spoken word ±0.3 s)
- tools/fx/quote_capture.py, tall_capture.py (inside browser_exec), capture_pass.py, post_pass.py, press_pass.py, num_pass.py,
  doc_pass.py, gfx_gate.py, proof_frames.py; reference: cases/trump-oversight-order/edit/spec/*, edit/graphics_index.tsv,
  edit/build_graphics.py (last film's working pipeline — reuse it)
- ../Aviation/docs/AVIATION_VISUAL_LANGUAGE.md (DOC, WEBSCROLL, SPLIT, TL motion grammar)

## Task
1. Capture the 34 pages named in the shot-map (edit/cap/<ID>.png + .json DOM rects of the marked phrases, DPR 2). Use your own
   browser tab, close it after; never touch owner's open tabs. No proxy of any kind (never ShardBrowser). Bot-walled page -> Wayback
   copy -> else the alternative mainstream URL for the same verbatim words (ledger-v4) and log it in edit/graphics_log.md.
   Phrase not verbatim on the page -> never fake; log it and pick the nearest verbatim line.
2. Render every WEBHEAD / POST / POSTSEQ / SPLIT / NUM / TIMELINE row -> edit/seg/<seg>_<t0>.mp4, 1920x1080 30 fps, duration =
   row t1-t0 (+0.2 s tail), yellow highlighter strip on the exact words as voiced, one strip per real line, coordinates from
   the DOM rects at original resolution. Numbers inside evidence = yellow. No typed text, no labels, no circles/red rings.
   Truth posts = real trumpstruth.org captures (the red-bra image is never shown — header/text only).
   Encode h264_videotoolbox -q:v 72; run independent renders in parallel (<= 6).
3. edit/graphics_index.tsv: seg | t0 | t1 | file | capture ID | phrase marked | marker time (segment s).
4. edit/qc/graphics_sheet.jpg (one frame per graphic after the marker lands) and LOOK at it: text readable at phone size,
   marker on the right words, no half lines at frame edges, no blank/placeholder frames.

## DONE-WHEN (countable)
- graphics_index.tsv has one row per graphic row of the shot-map (WEBHEAD+POST+POSTSEQ+SPLIT+NUM+TIMELINE = 57) with an existing
  mp4 whose duration >= t1-t0; 0 retyped cards; exceptions logged.

OUTPUT: cases/trump-nvidia-huang/edit/graphics_index.tsv
OUTPUT: cases/trump-nvidia-huang/edit/qc/graphics_sheet.jpg
