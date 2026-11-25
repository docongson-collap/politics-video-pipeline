# WO — trump-oversight-order / visual shot-map / 2026-11-23
Run: tools/role.sh visual work-orders/trump-oversight-order-visual.md

## Inputs (must exist on disk before dispatch)
- cases/trump-oversight-order/script-full-v3.md (voice segments B1-B19) + script-v3.md (## ON-SCREEN list per original beat)
- cases/trump-oversight-order/audio_full_v3/words.json ({Bn: [{w,s,e}], Bn_dur}) — all timings in segment seconds
- cases/trump-oversight-order/edit_plan_v3.json (order of VO segments and source clips K1-K6 with in/out)
- cases/trump-oversight-order/assets/clips/*.mp4 + *.srt/*.txt (downloaded sources: suc6XA3Je50 Raskin/Forbes-CNN,
  7q384ildNcs NewsNation, JcDtAVSC7xo Trump gaggle WH channel, 5lvQekhYyd0 Garcia MS NOW, awBaJI5rpHM Garcia FOX 11,
  Y0OOeTYQCRo Garcia The Hill, 6YLUH8zRzgk Trump signing WH channel, hlnFXBQgJaw Scharf Federalist Society/Forbes)
- cases/trump-oversight-order/research/ledger.md, ledger3.md, factcheck-v2.md (URLs for headline/doc captures)
- kho/stock/* (capitol_dc, capitol_east, courthouse_us, doj_bldg_a/b, paper_piles, stamp_doc ...), tools/envato.py (search works;
  research/envato/s_*.json already has: us capitol building, fighter jet factory assembly, aircraft assembly line, corporate lawyers
  meeting, office worker phone call, bank building new york, confidential documents shredding, congress hearing room)
- skills/politics-news-pipeline/references/edit-v2-toolkit.md (treatments + tools), docs/OPERATING.md step 5b, docs/FACEBOOK.md
  ("Rules for FB cuts")

## Task
Produce the shot-map for the whole film (VO B1-B19 + K clips), one row per shot, timed on words.json.
Facebook plan B rules (our last post lost 55% by 0:12 on a muted feed — these are the reason for this film):
- First 60 s: a real person on screen at least every 10 s (K1 Raskin, K4 Trump, K5 Garcia + B-roll of Trump signing
  6YLUH8zRzgk / gaggle JcDtAVSC7xo / Garcia footage). No building/establishing montage in the first 60 s.
- Any document/EO/letter on screen <= 3 s, cropped tight to the highlighted line (whitehouse.gov EO page capture via
  tools/fx/capture_pass.py or tall_capture.py — real page, marker on the words the voice says). No full pages.
- Text on screen <= 6 words, only key facts (100,000 / notify / coordinate / withhold / 258 / January); burned captions run
  the whole film separately (tools/fx/captions.py), so no sentence cards.
- Footage 65-75%, 17-22 cuts/min, no more than 2 graphics in a row, each graphic template used once per film.
- Hypothetical "bank or Boeing" beats: Envato B-roll (aircraft assembly / bank exterior / lawyers / phone call), never a real
  company logo implying wrongdoing.
- Blackwater 2007 (B12-B13): real 2007 press (LA Times archive page capture), Waxman / hearing archival footage if found on
  YouTube (C-SPAN/AP uploads), else Envato contractor/Iraq-era convoy B-roll labelled generic.
- Every clip row keeps the outlet bug; rows for each K clip use exactly the edit_plan window.
Columns: seg | t0 | t1 | words spoken | treatment (CLIP/FOOT/PRESS/DOC/POST/NUM) | source file or URL + src in-time |
text-on-screen (<=6 words or none) | rights note | MATCH/NO MATCH.
For every Envato pick, write itemUuid + title (do NOT license/download — builder does that after the orchestrator approves).
For every page capture, the exact URL + the exact phrase to mark (verbatim on the page).

## DONE-WHEN (countable)
- Rows cover 0 -> end of every segment with no gaps; 0 NO MATCH rows.
- Summary line: footage %, cuts/min, max consecutive graphics, longest shot, real-person count per 10 s window in 0-60 s.
- research/SOURCES.md has one line per clip/page/Envato item used.

OUTPUT: cases/trump-oversight-order/edit/shotmap_v3.tsv
OUTPUT: cases/trump-oversight-order/research/SOURCES.md
