# WO — trump-nvidia-huang / researcher / 2026-11-24
Run: tools/role.sh researcher work-orders/trump-nvidia-huang-researcher.md

## Inputs (exist on disk)
- cases/trump-nvidia-huang/BRIEF.md
- control/RADAR.md (radar scan 2026-11-24 15:53 +07: rival titles + VPH, Truth posts, Bluesky)
Rival transcripts: NOT available (YouTube returns 429 to this machine). Use rival TITLES in control/RADAR.md + press coverage instead.

## Task
Build the claim + clip ledger for a 7-9 min pro-Democratic, anti-Trump explainer: Trump pushed Nvidia's board to reinstate
Jensen Huang (affair with a woman US intelligence ties to China's Ministry of State Security), said "sex sells", owns NVDA stock.
Tone: hard but factual. Never write "illegal"/"crime" unless a source says so; attribute every allegation ("US intelligence assessed",
"the New York Times reported").

REQUIRED CLAIMS (one row each, primary source first):
K1 Trump Truth post Nov 22 9:54 PM EST "I hope the Board of Nvidia rehires Jensen Huang..." — trumpstruth.org/statuses/43709 + truthsocial URL.
K2 Trump Truth post Nov 23 "correct and proper decision... Great Patriot and National Treasure... Attorney General... does not possess evidence" — exact text.
K3 Trump doctored meme post (Huang, fist, red bra) — Deadline/Axios + archive link.
K4 Nvidia release Nov 23: reinstated "effective immediately", unanimous, "input from senior levels of the United States government", probe "will proceed to conclusion", new Chief Compliance Officer — nvidianews + SEC 8-K.
K5 Trump dialled into the board meeting — Semafor; WH confirmed (Steven Cheung "totally involved... protect our geniuses").
K6 Trump to CNBC (Eamon Javers) Nov 23: "directly and indirectly", "we gave him assurance", "sex sells, fellas", "did nothing wrong", "exonerated", "chips in his brain", China would "hire Jensen" — CNBC article + clip timestamps.
K7 Huang resigned Nov 12; Nov 8 admission "there is no excuse for what I did"; second affair with a subordinate (Reuters/NYT); misled general counsel (Reuters).
K8 Alice Huang / Megaspeed: US intelligence assessment, MSS contact (NYT Nov 22), Megaspeed probed for diverting chips; Commerce blacklisted Megaspeed Nov 23.
K9 Rubio briefed Trump on Air Force One May 12 2026, before Huang joined the Beijing trip (NYT/ABC); earlier warning a year before (NYT Oct 29).
K10 Board chair Harvey Jones Nov 17 earnings call "does not intend to reinstate"; Nov 18 "lack of candor"; Nov 23 "satisfied with respect to Mr. Huang's candor".
K11 Huang X post Nov 17 "honored to answer these calls" — exact text + URL.
K12 Stock: NVDA +30-36% Nov 23 (biggest jump in 20+ years); $1.5T value lost since Nov 6 (CNN) — source.
K13 Trump's portfolio holds millions in Nvidia stock (CNN; financial disclosure / OGE 278) + WH denial line.
K14 Jeffries statement "indefensible, irresponsible and incomprehensible", probe of Nvidia + Lutnick's Commerce — exact.
K15 Warren "reckless" + export-control bills; any Republican pushback (Ricketts, Tim Scott) — exact.
K16 Sonnenfeld "The board should resign. Every one of them" (CNN) — exact.
K17 Fox: Trump Cabinet officials clash over the spy scandal — exact; Rubio reaction (walk-out on question, if sourced).
K18 Next dates: Dec 1 closed-door congressional interviews; Senate Banking public testimony; SEC probe (WSJ).
K19 H200 chip sales to China approved by the administration; Wyden/Neal inquiry — source.
CLIPS: 6-10 on-camera/on-air clips (YouTube URL + in/out + speaker + exact words): CNBC Trump call audio, Jones earnings-call audio,
Jeffries, Warren, Rubio, Sonnenfeld, PBS Liz Landers / Trump "back where he should be". Prefer network/C-SPAN uploads.

Ledger format (tools/ledger_verify.py parses it): one block per claim:
### C1 | short claim
**Exact Quote:** verbatim text that is on the page
**URL:** https://...
**Date:** publish date / access 2026-11-24
**Clip:** URL + mm:ss-mm:ss (spoken quotes only)
**Confidence:** high/med/low
**Counterclaim:** ...

## DONE-WHEN (countable)
- ledger has >= 24 rows covering K1-K19 (missing ones listed under "GAPS" with reason), each with Exact Quote + live URL.
- >= 6 clip rows with YouTube URL + in/out timestamps + verbatim words (mark "timestamp unverified" if not watched).

OUTPUT: cases/trump-nvidia-huang/research/ledger.md
