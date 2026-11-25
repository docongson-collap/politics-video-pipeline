# WO — trump-oversight-order / shot-map v4 fix pass / 2026-11-23
Run: tools/role.sh visual work-orders/trump-oversight-order-visual4fix.md

## Inputs (on disk)
- cases/trump-oversight-order/edit/shotmap_v4.tsv + shotmap_v4_build.py (yours), edit/full_shots_v4.tsv (what was built)
- output/trump-oversight-order-v2_nocap.mp4 (built from it), edit/qc4/repeat_check.jpg, edit/qc4/MECH_c.jpg
- assets/clips/*, assets/envato/* (20 licensed), kho/stock/*, audio_full_v4/words.json
- ../Aviation/docs/AVIATION_VISUAL_LANGUAGE.md

## Faults found by the orchestrator on the built film (your QC said PASS; it counted wrong)
1. The NewsNation full-screen quote graphic ("TRUMP LIMITS CONGRESS ACCESS TO RECORDS", 7q384ildNcs @27-46 s) is used as
   B-roll 7 times: film 2.2, 60.9, 80.6, 85.8, 292.4, 294.9, 297.0 s. Plus 7q384 @52-59 (Capitol with NewsNation chyron) at
   163.8, 238.5, 418.5. A borrowed news graphic is a repeated template -> allowed at most ONCE in the film (outside K2).
   Same source per 60 s counts K clips too: 61/81/86 and 292/295/297 = 3 in 60 s -> FAIL.
2. MS NOW 5lvQekhYyd0 as B-roll at 55.8, 206.9, 210.3, 220.7 (+K5 58.5, K6 222.6) = 4 in 60 s around 207-223 -> FAIL;
   the "WHITE HOUSE WARNS REP. GARCIA" letter graphic appears twice.
3. MECH (B16 rows at film ~?: edit/seg4/B16_*.mp4) is an abstract plate: floating icons + crossing lines on black, no
   words, means nothing on a phone. owner bans abstract plates. Replace all 4 MECH rows with exact evidence or exact footage
   for those lines (EO penalty language from the real wh_eo.png page is already used by DOC once; prefer footage:
   company/contractor/Congress hearing/subpoena, or the real 41 USC 4712 crop for the employee line).
4. capitol_dc.mov used 8 times (136, 180, 234, 300, 344, 373, 408, 437) and 6YLUH8zRzgk 9 times: vary — no source more than
   4 times in the film unless it is the exact event the voice names.

## Task
Edit shotmap_v4.tsv in place (keep row timing; only change the visual source/window/treatment of offending rows), recompute
your QC block counting K clips + FOOT rows together per source, then print a CHANGES list (row -> old -> new).
For any new graphic you would need, prefer footage instead; no new templates.

## DONE-WHEN
- Recomputed QC: max same source per 60 s (incl. K clips) <= 2; no borrowed news graphic more than once; 0 MECH rows;
  no source > 4 uses unless named event.

OUTPUT: cases/trump-oversight-order/edit/shotmap_v4.tsv
