# WO — blanche-huang-confession / visual shot-map v1 / 2026-11-25
Run: tools/role.sh visual work-orders/blanche-huang-confession-visual.md

## Inputs (on disk)
- cases/blanche-huang-confession/script-full-v1.md (VO B1-B18) + script-v2.md (## ON-SCREEN, ## SCRIPT with {C..} tags) +
  edit_plan_v1.json (vo/clip order; 9 clips K1-K9 with file + window + verbatim words)
- cases/blanche-huang-confession/audio_full_v1/words.json ({Bn:[{w,s,e}], Bn_dur}; segment seconds) — VO 7.0 min, total ~8.5 min
- cases/blanche-huang-confession/assets/clip_index.md + assets/clips/*.mp4 + assets/clips/asr/*.srt:
  TC-axC1IL00 CBS presser (Blanche + Patel podium, reporters, wides), foxnews_6408836632112 (same presser, Fox angle),
  CNN_me20cb... (Clayton SOTU), CNN_me6ad... (Raskin), foxnews_6408780341112 (Rubio walk-off), podforceone_hVCMk36xo_s_1015
- B-roll pool from yesterday's case (re-use allowed, different timecodes than yesterday's film where possible):
  cases/trump-nvidia-huang/assets/clips/* (CNBC Trump interview, CNN/PBS coverage, Nvidia HQ, stock boards, Huang stage
  footage) + clips.tsv + their .srt; cases/trump-nvidia-huang/assets/envato/* (licensed) ; kho/stock/doj_bldg_a|b, capitol_*,
  courthouse_us, paper_piles, stamp_doc
- cases/blanche-huang-confession/research/ledger.md (URLs for captures: CNBC Nov 24 Blanche article, CNBC Trump-trades analysis,
  CNBC Trump transcript Nov 23, Bloomberg Law Fox quote, NBC administration-official story, NY Post pardon + Rubio "malign
  influence", justice.gov DOJ/Commerce Megaspeed statement + SDNY release, Federal Register Megaspeed, jeffries.house.gov Nov 23,
  oag.ca.gov Bonta subpoena (C27), Schumer X post, Mediaite/New Republic Pod Force One headline)
- Format to copy: cases/trump-nvidia-huang/edit/shotmap_v1.tsv (columns + QC block) and edit/shotmap_v1_build.py
- skills/politics-news-pipeline/references/edit-v2-toolkit.md (looks + capture tools)

## Rules (owner's, measured at QC)
- Talking heads only while that person's own words are heard (K clips). Never anchors/reporters as filler under our VO.
  Exception: presser wides / podium with Blanche NOT lip-visible-speaking are fine under VO lines about the presser.
- Factual sentence = exact evidence: real article/document capture with yellow marker on the words the voice says (±0.3 s),
  or real footage of that event. Generic stock only for scene-setting, never repeated.
- Alice Huang: no photo of her; never "spy" on screen. No AI images.
- LOOK MUST DIFFER from yesterday's film (trump-nvidia-huang): no TIMELINE, no Truth POSTSEQ. Allowed graphics (each ONCE):
  1 SPLIT (B5 Trump "pretty good investigation" CNBC transcript vs Blanche "that assumes there is an investigation" Bloomberg Law),
  1 NUM (B6: 103 trades -> $12.5M–$58M -> NVDA +30%; one template for the whole money run), 1 DOC (justice.gov Megaspeed joint
  statement or oag.ca.gov subpoena), 1 POST (Schumer X). Everything else = real page captures (WEBHEAD) and footage.
  Describe motion start/change/end for each graphic.
- No top-left cards, no lower thirds, no typed labels/sentence cards; on-screen words only inside real evidence + burned captions.
  Numbers inside evidence get the yellow marker. No circles/red rings/arrows.
- Same source video/page <= 2 per 60 s; never the same source timecode twice.
- Footage 65-75 %, 17-22 cuts/min, change visual type every 20-30 s, <= 2 graphics in a row, 90 % shots <= 6 s.
- First 60 s: a real person on screen at least every 10 s.
- Every clip row keeps the outlet bug (CBS/CNN/Fox/NY Post). Check chyrons: editorialising chyron with words not on tape -> crop.

## DONE-WHEN (countable)
- edit/shotmap_v1.tsv covers every VO segment 0 -> Bn_dur and every K clip window, no gaps, 0 NO MATCH rows.
- QC block at file end: max same source per 60 s, template ledger (template -> 1 use), talking-head-under-VO rows (0),
  footage %, cuts/min, longest shot.
- research/SOURCES.md: one line per clip/page/Envato item used.

OUTPUT: cases/blanche-huang-confession/edit/shotmap_v1.tsv
OUTPUT: cases/blanche-huang-confession/research/SOURCES.md
