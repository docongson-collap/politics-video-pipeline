# WO — trump-oversight-order / graphics (captures) / 2026-11-23
Run: tools/role.sh visual work-orders/trump-oversight-order-graphics.md

## Inputs (must exist on disk before dispatch)
- cases/trump-oversight-order/edit/shotmap_v3.tsv (your shot-map; rows with treatment DOC / PRESS / POST / NUM = 47 rows)
- cases/trump-oversight-order/audio_full_v3/words.json (segment word times; markers land ON the spoken word ±0.3 s)
- tools/fx/quote_capture.py, tools/fx/tall_capture.py (run inside browser_exec), tools/fx/capture_pass.py, tools/fx/post_pass.py,
  tools/fx/num_pass.py; reference specs: cases/alaska-doj-surrender/edit/spec/*.json, edit/specs/num_*.json
- skills/politics-news-pipeline/references/edit-v2-toolkit.md ("PRESS real page", "PRESS tall page", "Real sources that block
  bots": AP via Wayback, The Hill/Politico blocked -> Wayback or skip to the alternative source in the shot-map)

## Task
Render every graphic row of the shot-map as a 1920x1080 30 fps mp4 segment, real page captures only (no retyped cards):
1. Capture each of the 14 URLs once (DPR 2, browser_exec, never touch owner's open tabs — open your own tab, close it after) ->
   cases/trump-oversight-order/edit/cap/<slug>.png + .json (DOM rects of the marked phrases from the shot-map, verbatim).
2. One capture_pass.py spec per shot-map row (or one spec covering consecutive rows of the same page) ->
   edit/spec/<seg>_<n>.json -> edit/seg/<name>.mp4, duration = row t1-t0 (+0.2 s tail), marker on the spoken word.
   whitehouse.gov EO (15 DOC rows): tight crop on the one marked line per row, <= 3 s each, NO full-page view.
   law.cornell.edu 4712 (5 rows): same rule.
3. POST row: tools/fx/post_pass.py with the real X post (screenshot via browser if the page renders logged-out; else the
   Oversight Democrats press release page capture instead, mark "blatant attack").
4. NUM rows: num_pass.py look (Flat DataViz) — 258 House / 56 Senate exactly as AP.
5. If a page is bot-walled and has no Wayback copy, use the alternative mainstream URL from factcheck-v2.md / ledger for the
   same quote and note it in edit/graphics_log.md. If a phrase isn't verbatim on the page -> do not fake it; log it.
6. Write edit/graphics_index.tsv: seg | t0 | t1 | file | origin(from) | phrase marked | marker time (segment s).
7. Contact sheet: edit/qc/graphics_sheet.jpg (one mid frame per graphic, after marker) and look at it yourself:
   text readable at phone size, marker on the right words, no half lines at frame edges.

## DONE-WHEN (countable)
- graphics_index.tsv has one row per DOC/PRESS/POST/NUM shot-map row (47) with an existing mp4 whose duration >= t1-t0.
- 0 retyped cards; every marked phrase verbatim (log exceptions).

OUTPUT: cases/trump-oversight-order/edit/graphics_index.tsv
OUTPUT: cases/trump-oversight-order/edit/qc/graphics_sheet.jpg
