# WO — trump-oversight-order / visual shot-map v4 (Aviation edit rules) / 2026-11-23
Run: tools/role.sh visual work-orders/trump-oversight-order-visual4.md
DISPATCH ONLY AFTER audio_full_v4/words.json exists (script-v4 voiced + ASR-checked).

## Inputs
- cases/trump-oversight-order/script-full-v4.md, edit_plan_v4.json, audio_full_v4/words.json
- cases/trump-oversight-order/edit/shotmap_v3.tsv (old map: reuse good evidence rows, fix the faults below)
- edit/graphics_index.tsv + edit/cap/*.png (real page captures already made; reuse, re-crop, don't re-fetch)
- ../Aviation/docs/AVIATION_VISUAL_LANGUAGE.md (the edit rulebook owner wants here — read all of it) and
  ../Aviation/docs/STYLES.md sections 14 + "One template, one use"
- assets/clips/*, assets/envato/* (20 licensed), kho/stock/*

## Faults measured in v3 (owner: "lặp đi lặp lại"; must be 0 in v4)
- Same source up to 8x in 60 s (whitehouse.gov EO at 60-120 s). Rule: same source video/page <= 2 per 60 s.
- Same template repeated: 15 near-identical EO page cards + 5 Cornell cards + 24 PRESS cards in one look.
  Rule: each graphic template ONCE per film; a repeated subject changes visual form (footage -> doc -> map/timeline ->
  diagram), not doc -> doc -> doc.
- 27 FOOT rows use interview/studio footage (Garcia FOX 11 / MS NOW, Raskin, NewsNation) as B-roll under narrator voice.
  Rule: talking heads only while that person's own quote is heard (the K clips). Never as filler.
- 58 generic stock rows (Envato/kho) under specific factual claims. Rule: factual sentence = exact evidence / exact event
  footage / a diagram that explains it. Generic stock only for scene-setting lines, never repeated.
- No top-left cards or text labels at all (owner 23/11). On-screen words only inside real evidence (highlighted page lines)
  and the burned captions.

## Task
New edit/shotmap_v4.tsv (same columns as v3) timed from audio_full_v4/words.json:
1. Evidence docs: ONE full EO sequence (page -> continuous push -> marker sweeps the exact lines as voiced), not 15 cards;
   later EO references change form (pull a single phrase into a split, timeline station, or mechanism diagram).
2. Build at most 1 each of: timeline (2007 Blackwater -> 2026 order -> January), mechanism diagram (Congress request ->
   contractor -> White House review -> answer / penalty), comparison split (order text vs 41 USC 4712), seats NUM. Each
   template once. These are specs for the builder (describe motion: start/change/end).
3. Footage 65-75 %, 17-22 cuts/min, change visual type every 20-30 s, <= 2 graphics in a row, 90 % shots <= 6 s,
   1-2 hero shots/min that breathe 3-6 s. Never repeat an exact source timecode.
4. Allocation table at the end: source -> list of film times; prove <= 2 per 60 s; template ledger (template -> 1 use).

## DONE-WHEN
- QC counts printed at file end: max same source per 60 s <= 2, template duplicates 0, talking-head-under-VO rows 0,
  footage %, cuts/min.

OUTPUT: cases/trump-oversight-order/edit/shotmap_v4.tsv
