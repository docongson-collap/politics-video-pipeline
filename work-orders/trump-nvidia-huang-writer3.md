# WO — trump-nvidia-huang / writer v3 (apply factcheck) / 2026-11-24
Run: tools/role.sh writer work-orders/trump-nvidia-huang-writer3.md

## Inputs (exist on disk)
- cases/trump-nvidia-huang/script-v2.md (parity PASS)
- cases/trump-nvidia-huang/factcheck-v1.md (PASS 110 / FIX 38 / FAIL 0 — every FIX has line number + replacement)
- cases/trump-nvidia-huang/research/ledger-v4.md

## Task
script-v2 -> script-v3: apply ALL 38 FIX rows of factcheck-v1 (use the given replacement wording; if a replacement breaks the
rhythm, rephrase but keep exactly the same factual content and attribution). Key ones: B1 opening must not state as fact that
Trump phoned the board ("reportedly dialed into" / "pushed the board, and says he was represented") and must not say "tied that
CEO to a spy" (affair with a woman US intelligence believed was working for China); CNBC interviewer = David Faber for C30;
Trump's words "J.D., Scott, and, you know, Howard"; "we gave them assurance"; December twenty twenty-five, "a cut of sales";
ballroom = Nvidia's pledge (not paid, not Huang personally); Nvidia denial verbatim "our support for the United States is
paramount, and independent of any business interests"; order of events (Huang X post before Jones remark; Nvidia release before
Trump's 9:07 post; PBS call before the announcement); closing question = new wording (not the rival's).
Keep: claim tags, clip lines (fix their words where the FIX says), beat order, short-punch rhythm (>= 22% sentences <= 5 words),
numbers as spoken words. No new facts.
At the end add ## FIX LOG: factcheck line -> applied (yes/how).

## DONE-WHEN (countable)
- FIX LOG has 38 rows, all applied; ## SCRIPT 1,150-1,350 words; parity PASS.

OUTPUT: cases/trump-nvidia-huang/script-v3.md
MINWORDS: cases/trump-nvidia-huang/script-v3.md 1100 0
PARITY: cases/trump-nvidia-huang/script-v3.md cases/trump-nvidia-huang/research/ref/qhq5GD104I4.txt --ignore Daddy --ignore THE --ignore DAY --ignore Brian --ignore hang --ignore us --ignore america --ignore according
