# WO — trump-nvidia-huang / visual shot-map v1 / 2026-11-24
Run: tools/role.sh visual work-orders/trump-nvidia-huang-visual.md

## Inputs (on disk)
- cases/trump-nvidia-huang/script-full-v2.md (VO B1-B15), script-v3.md (## ON-SCREEN per beat), edit_plan_v1.json
  (order: B1 K1 B2 B3 B4 B5 K2 B6 K3 B7 B8 K4 B9 B10 B11 K5 B12 B13 B14 B15)
- cases/trump-nvidia-huang/audio_full_v2/words.json ({Bn:[{w,s,e}], Bn_dur}; segment seconds) — total VO 7.9 min
- cases/trump-nvidia-huang/assets/clips/clips.tsv (K1-K5 windows) + *.mp4/*.srt:
  -KzsKuC1AUs CNBC full Trump interview 2026-11-23 (50 min; Trump wide/close, Faber), MIkpSWkoolM Nvidia Q3 call (USA TODAY),
  XPRvHrvNbEI CNBC short, QQNUlpTmHl0 + JzBXDYLUJ8Q CNN coverage (Huang, Nvidia HQ, stock board, Hill reactions — read SRTs
  you make with whisper-cli if you need their timings; model kho/whisper-models/ggml-small.en.bin)
- cases/trump-nvidia-huang/research/ledger-v4.md (URLs for captures: trumpstruth.org/statuses/43709 + the Nov 23 post, Nvidia
  release on nvidianews, CNBC/CBS/Fox/Newsweek/TechCrunch articles, Jeffries/Warren releases, Cornyn X post)
- cases/trump-oversight-order/edit/shotmap_v4.tsv (column format to copy) + edit/shotmap_v4_build.py
- ../Aviation/docs/AVIATION_VISUAL_LANGUAGE.md + ../Aviation/docs/STYLES.md section 14 + "One template, one use"
- tools/envato.py (search only; list itemUuid+title, builder licenses), kho/stock/*

## Rules (owner's, measured at QC)
- Talking heads only while that person's own quote is heard (K clips). Never Faber/CNN anchors as filler under our VO.
- Factual sentence = exact evidence: real Truth post capture, real Nvidia release, real headline/article line with marker on the
  words voiced (±0.3 s), real footage of that event. Generic stock only for scene-setting lines, never repeated.
- Alice Huang: no photo of her unless from a mainstream outlet capture; never caption her "spy".
- Ballroom beat: real coverage page (CNBC/Newsweek) + WH ballroom footage from CNN/official WH channel if found; no implied
  receipt graphics.
- Each graphic template ONCE per film: allowed set = 1 timeline (Nov 8 -> Nov 12 -> Nov 17 -> Nov 18 -> Nov 22 -> Nov 23 ->
  Dec 1 -> Dec 3), 1 stock NUM (NVDA "more than thirty percent"), 1 post sequence (Truth posts), 1 split (Jones "does not intend
  to reinstate" vs release "effective immediately"). Describe motion start/change/end for the builder.
- No top-left cards, no lower thirds, no typed labels; on-screen words only inside real evidence + burned captions.
  Numbers inside evidence get the yellow marker.
- Same source video/page <= 2 per 60 s; never the same source timecode twice; no circles/red rings.
- Footage 65-75 %, 17-22 cuts/min, change visual type every 20-30 s, <= 2 graphics in a row, 90 % shots <= 6 s.
- First 60 s: a real person on screen at least every 10 s.
- Every clip row keeps the outlet bug (CNBC/CNN/USA TODAY).

## DONE-WHEN (countable)
- edit/shotmap_v1.tsv covers every VO segment 0 -> Bn_dur and every K clip window, no gaps, 0 NO MATCH rows.
- QC block at file end: max same source per 60 s, template ledger (template -> 1 use), talking-head-under-VO rows (0),
  footage %, cuts/min, longest shot.
- research/SOURCES.md: one line per clip/page/Envato item used.

OUTPUT: cases/trump-nvidia-huang/edit/shotmap_v1.tsv
OUTPUT: cases/trump-nvidia-huang/research/SOURCES.md
