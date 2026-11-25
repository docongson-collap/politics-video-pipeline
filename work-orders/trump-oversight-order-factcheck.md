# WO — trump-oversight-order / factcheck / 2026-11-23
Run: tools/role.sh factcheck work-orders/trump-oversight-order-factcheck.md

## Inputs (must exist on disk before dispatch)
- cases/trump-oversight-order/script-v2.md (## SCRIPT section is what gets voiced)
- cases/trump-oversight-order/research/ledger.md, research/ledger3.md (+ ledger_verify.md, ledger3_verify.md)
- cases/trump-oversight-order/assets/clips/*.srt / *.txt (whisper of clips K1-K6; check lead-ins match what the clip says)

## Task
Check EVERY sentence of ## SCRIPT (narration + clip lead-ins) against the tagged ledger row and, where the row's quote is short,
the live URL. Verdict per sentence: PASS / FIX (give exact replacement wording, same length) / FAIL (cut).
Pay special attention to:
- B2 line 1 "Raskin says the order means nothing" vs his actual words (K1: "doesn't mean anything in terms of federal law").
- B6 lines tagged {K2}: must be things NewsNation actually says in 7q384ildNcs (check assets/clips/7q384ildNcs.txt).
- B7 AP numbers (258 House, 56 Senate, "since 1992", "biggest in over a decade") — exact AP wording, AP attribution present.
- B8 "In the same week" (Scharf memo date vs EO Nov 20), "Earlier this month" (Garcia letter date), Reitz details, "Six experts".
- B10 "The White House argues contractors work so closely..." — is this actually a WH argument in a source? If not, FIX.
- B11 "Lawyer Marc Elias" — attribution OK? Politico line wording.
- B12/B13 4712 paraphrase ("fired or demoted ... for telling a Member of Congress") — fair to the statute? FIX if overstated.
- B13 "The order only says agencies shall consider ending the contract" vs Sec. 4 text.
- Any sentence that states as fact something only in a Counterclaim field or only in a rival transcript.
Opinion lines marked "In our view" are opinion — check only that they don't contain a false fact.

## DONE-WHEN (countable)
- Every ## SCRIPT sentence has a verdict row; summary line "PASS n / FIX n / FAIL n".
- For each FIX/FAIL: line number, original, replacement, source URL.

OUTPUT: cases/trump-oversight-order/factcheck-v2.md
