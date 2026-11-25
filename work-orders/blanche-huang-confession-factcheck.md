# WO — blanche-huang-confession / factcheck / 2026-11-25
Run: tools/role.sh factcheck work-orders/blanche-huang-confession-factcheck.md

## Inputs (exist on disk)
- cases/blanche-huang-confession/script-v1.md (## SCRIPT section is what gets voiced)
- cases/blanche-huang-confession/research/ledger.md + research/ledger_audit.md (which rows are verbatim-OK / paraphrase-only)
- cases/blanche-huang-confession/assets/clip_index.md (VERIFIED file timestamps + exact words for every clip we hold)
- cases/blanche-huang-confession/research/ref/TC-axC1IL00_cbs.txt (full presser transcript; captions spell Huang as "Wong")
- cases/blanche-huang-confession/research/ref/2dwS_bn2tMM.txt (rival transcript — NOT a source)

## Task
Check EVERY sentence of ## SCRIPT (narration, clip lead-ins and {CLIP ...} words) against the tagged ledger row and, where the row's
quote is short, the live URL. Verdict per sentence: PASS / FIX (exact replacement wording, similar length) / FAIL (cut).
Special attention:
- Every {CLIP ...}: words must be what is on tape per clip_index.md / the presser transcript, and the timestamp must be the file time
  from clip_index.md (FIX the timestamps: C3 question is at 0:01-0:14, C1 answer 0:15-0:50, Clayton clip = CNN_me20cb... 1:50-2:01,
  Pod Force One = podforceone_hVCMk36xo_s_1015.mp4 0:10-0:33). Each clip <= 20 s of speech; trim the words to fit.
- The Pod Force One clip: script must keep the fairness line that he said Biden's DOJ did too (he says "but they did too").
- Line 42 "on November twelfth, Blanche himself said an investigation into the chips was ongoing" — the presser transcript has a
  reporter saying that (TC-axC1IL00_cbs.txt search "November 12th"); what exactly is sourced? FIX wording to what the source says.
- Line 38 Nov 16 vs Nov 17 date of the DOJ/Commerce Megaspeed statement (CNBC Nov 24 says Nov 17) — resolve from the source.
- Line 70 "after the president pushed the board" — attribute to sourced wording.
- Line 78 Bloomberg Law Fox quote exact; line 82-83 NBC administration official wording exact.
- Line 98 ballroom: exact source wording (pledge/committed/donated; anonymous request) — Washington Post via ledger C9.
- Line 123 California AG — which row supports it? If none, FAIL.
- Line 124 / 133 tagged C26 — does C26 support "no charges announced" and "the White House rejected the criticism"? If not, FIX/FAIL.
- Line 135 Rubio "On Monday, at the State Department" — BTC posted it Nov 24 (Tuesday); resolve the day/place from the source.
- Line 137 "The Post reported he views Nvidia as a malign influence" — which Post, exact wording?
- Line 147-150 dates and Jeffries wording exact (C15).
- Alice Huang: every spy/MSS line attributed.
- New content allowed ONLY from clip_index.md (on tape): propose ONE insertion row in B9 using Raskin's clip 0:26-0:34
  "The Trump administration's giving us exoneration without investigation." (replace the paraphrased gobbledygook line or add it),
  and in B9 Rubio may use the Fox clip (no words, walk-off) instead of narration only.
Opinion lines (clearly ours) — check only that they contain no false fact.

## DONE-WHEN (countable)
- Every ## SCRIPT sentence has a verdict row; summary line "PASS n / FIX n / FAIL n".
- For each FIX/FAIL: line number, original, replacement, source URL.

OUTPUT: cases/blanche-huang-confession/factcheck-v1.md
