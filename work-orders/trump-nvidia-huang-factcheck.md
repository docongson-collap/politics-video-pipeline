# WO — trump-nvidia-huang / factcheck / 2026-11-24
Run: tools/role.sh factcheck work-orders/trump-nvidia-huang-factcheck.md

## Inputs (exist on disk)
- cases/trump-nvidia-huang/script-v2.md (## SCRIPT section is what gets voiced)
- cases/trump-nvidia-huang/research/ledger-v4.md + research/ledger-v4_verify.md (OK 30/31; C12 quote not verbatim)
- cases/trump-nvidia-huang/research/ref/qhq5GD104I4.txt (rival transcript — NOT a source; nothing may rest on it alone)

## Task
Check EVERY sentence of ## SCRIPT (narration, clip lead-ins and {CLIP ...} words) against the tagged ledger row and, where the
row's quote is short, the live URL. Verdict per sentence: PASS / FIX (exact replacement wording, same length) / FAIL (cut).
Special attention:
- Alice Huang: every "spy"/"Chinese intelligence"/"asset" line must be attributed (US intelligence assessed / NYT / ABC reported).
  B1 line 3 "US intelligence had tied that CEO to a suspected Chinese spy" — fair to the sources? FIX if overstated.
- B1 "The president phoned a private company's board" — Semafor + WH confirmation wording; Trump told CNBC "directly and
  indirectly" / "represented". Do not state more than sourced.
- Dates: Nov 8 letter, Nov 12 resignation, Nov 17 Jones call, Nov 18 "lack of candor", Nov 22 9:54 PM EST post, Nov 23 release,
  Megaspeed listing Nov 23, May 12 Air Force One, "fall of twenty twenty-five" first briefing.
- H200 / "twenty-five percent cut for the US" / "Back in December" (which year?) — C19 source wording.
- Stock jump: only "more than thirty percent" allowed (C12). Trump's Nvidia holdings range (C13) exact + attribution.
- Ballroom: $25M pledge is Nvidia's (the company), not Huang personally; any implied quid pro quo must be framed as a question/our
  view, with Nvidia's denial line present.
- Every {CLIP Cn "..."} must be words the person actually said (CNBC transcript / earnings-call transcript), verbatim.
- Hearing dates: Dec 1 closed-door (three House committees), Dec 3 public Senate Banking.
- Any sentence whose fact sits only in a Counterclaim field or only in the rival transcript.
Opinion lines (clearly ours) — check only that they contain no false fact.

## DONE-WHEN (countable)
- Every ## SCRIPT sentence has a verdict row; summary line "PASS n / FIX n / FAIL n".
- For each FIX/FAIL: line number, original, replacement, source URL.

OUTPUT: cases/trump-nvidia-huang/factcheck-v1.md
