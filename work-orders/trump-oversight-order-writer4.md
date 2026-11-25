# WO — trump-oversight-order / writer v4 (anti-repetition) / 2026-11-23
Run: tools/role.sh writer work-orders/trump-oversight-order-writer4.md

## Inputs (must exist on disk before dispatch)
- cases/trump-oversight-order/script-v3.md (factchecked; every claim and claim tag in it is cleared)
- cases/trump-oversight-order/factcheck-v2.md (what wording is allowed: hedges like "could", "might", "appeared to" must stay)
- ../Aviation/docs/STYLES.md sections 13-14 (script rules owner uses for all channels)

## Why
owner: "mày bị lỗi lặp đi lặp lại cách diễn đạt". Measured on v3 (1,228 words, 7.5 min):
"White House" 16x, "Congress" 16x, "the order" 9x (5 sentences open with it), "privilege" 9x, "Garcia" 8x,
"Politico" 6x ("Politico says" opens 4 sentences), clip lead-ins "Here is / Here's" 8x, "Nixon" 5x, "not absolute" 3x,
"Imagine" 3x, "In our view" 3x, "Now, the ..." 3x, "That is" opens 3 sentences. It sounds like a template.

## Task
Rewrite script-v3 -> script-v4: SAME facts, SAME claim tags, SAME clips (exact {K..} lines unchanged, same order), SAME beat
order and hedges. Change only the wording so no phrase pattern repeats:
1. No sentence opener (first two words) used more than twice in the film.
2. Main nouns at most ~1 per minute each: "White House" <= 8, "Congress" <= 8, "the order" <= 5 (use "Trump's directive",
   "the new rule", "it", "the memo-like order" etc.), "privilege" <= 5, "Politico" <= 3 (name the reporter/outlet once,
   then "the same report"), "Garcia" <= 5 (he is "the incoming Oversight chairman" once), "Nixon" <= 2, "not absolute" 1.
3. Clip lead-ins: each different; at most 1 "Here's". Identify the speaker inside a natural sentence (there are no on-screen
   name cards anymore, so the voice must say who speaks, e.g. "Jamie Raskin, the top Democrat who led Trump's second
   impeachment, didn't hold back." — only facts that are in the ledger).
4. Connect beats with but / so / because / which means (>= 8 in the film), not with "Now, ..." (0 uses of "Now,").
5. Re-hook every 60-90 s (a short open question or a promise the film then pays off); every open loop is closed.
6. "In our view" <= 2; vary the stance markers ("We think", "That's the tell", ...), opinion still clearly ours.
7. Keep payoff in the first sentence (<= 20 words), tease by ~0:35, three paths payoff, comment question ending.
8. Keep sentences short (avg 8-11 words), but vary rhythm: some 3-word punches, some 16-word lines.
9. Numbers as spoken words. No new facts, no new names, no new numbers.

## DONE-WHEN (countable)
- ## SCRIPT 1,150-1,300 words; caps in 1-6 met (print a COUNTS table at the end of the file: each tracked phrase -> count).
- Every factual sentence still carries its claim tag; {K..} lines byte-identical to v3.

OUTPUT: cases/trump-oversight-order/script-v4.md
MINWORDS: cases/trump-oversight-order/script-v4.md 1100 0
PARITY: cases/trump-oversight-order/script-v4.md cases/trump-oversight-order/research/ref/YpdfsKXJfxY.txt --ignore OversightDesk --ignore Since --ignore Ending --ignore Lawyers --ignore Office
