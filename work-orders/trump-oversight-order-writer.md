# WO — trump-oversight-order / writer / 2026-11-23
Run: tools/role.sh writer work-orders/trump-oversight-order-writer.md

## Inputs (must exist on disk before dispatch)
- cases/trump-oversight-order/BRIEF.md (story + FORMAT = Facebook plan B — read it fully)
- cases/trump-oversight-order/research/ledger.md (ONLY fact source) + research/ledger_verify.md
- cases/trump-oversight-order/research/ref/YpdfsKXJfxY.txt (faceless rival, beat model), ref/FfW2uazzwMk.txt (BTC/Elias, angle)
- cases/trump-oversight-order/assets/clips/suc6XA3Je50.txt (Raskin, whisper), assets/clips/7q384ildNcs.txt (NewsNation, whisper)
- docs/CHANNEL.md, docs/SOUL.md (stance: pro-Democratic, anti-Trump; opinion said as ours, facts exact)

## Task
Write the narration script for a 7-8 minute Facebook-first explainer (target 1,150-1,300 spoken words at ~165 wpm, excluding clips).
Why this format: our last Facebook video lost half its viewers by 0:12 (muted feed autoplay, slow legal setup). So:
1. B1 (0:00-0:10) = the payoff in plain words, no legal jargon: Trump just ordered about one hundred thousand companies to check
   with HIM before answering Congress, weeks before Democrats take over. Then [CLIP K1 00:12-00:23] Raskin "inter-office memo ...
   closing early before the Thanksgiving holiday ... doesn't mean anything in terms of federal law".
2. B2 (by 0:35) = tease the end: what happens when a bank or Boeing gets a Democratic subpoena and a White House "no" — "stay for that".
3. Then the order itself in 2-3 short beats (notify / coordinate / withhold; subcontractors; the stick = lose the contract), each
   quote short enough for a 3-second on-screen crop (<= 15 words per quoted line).
4. Why now: Democrats' majorities and January third; Scharf memo; WH Counsel letter to Garcia; Texas US attorney letters (pattern).
5. The White House's best case, fairly (executive privilege is real, US v. Nixon 1974, fact sheet "harassing private companies"),
   one "to be fair" beat — then why it fails (an EO binds the government, not private companies — Elias via BTC/Politico unclear).
6. The payoff of the tease: the three scenarios (company cooperates / company tells White House, WH goes to court / courts decide).
7. Close: verdict as OUR view ("In our view ..."), next date January third, and ONE comment question to the viewer
   (e.g. "If your company got that subpoena, would you call Congress back or the White House first? Tell us below.").
Do NOT use claims C14 (1789 Capital — MISSING) or C15 (ballroom donors — unverified). AP-only numbers (C6b $793B, C7) only with
"according to the Associated Press". No quote marks around paraphrase. Numbers as spoken words ("one hundred thousand",
"twenty twenty-seven", "January third"). Short sentences: a person scrolling must get each line instantly.
Mark clips inline on their own line: {K1 suc6XA3Je50 00:12.0-00:23.2}, {K2 7q384ildNcs 00:46-00:57} (NewsNation: Oversight
Democrats called it "desperate ... totally unprecedented and blatantly unlawful"), {K3 suc6XA3Je50 00:23.1-00:34.7}
(Raskin "We've got the Constitution on our side ... we're gonna do that"). Use each clip once; no other clips.
Beats [B1]..[Bn], each factual sentence ends with its claim ID {C2}. Also write a short "## ON-SCREEN" list per beat: the
exact <=6-word text or quote crop that should appear (a doc crop max 3 s).

## DONE-WHEN (countable)
- ## SCRIPT section 1,150-1,350 words; B1 payoff sentence within the first 30 words; tease line before word 100.
- 0 factual sentences without {C..}; ends with a comment question; parity PASS.

OUTPUT: cases/trump-oversight-order/script-v1.md
MINWORDS: cases/trump-oversight-order/script-v1.md 1100 0
PARITY: cases/trump-oversight-order/script-v1.md cases/trump-oversight-order/research/ref/YpdfsKXJfxY.txt
