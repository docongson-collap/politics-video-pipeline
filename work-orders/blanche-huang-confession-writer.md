# WO — blanche-huang-confession / writer / 2026-11-25
Run: tools/role.sh writer work-orders/blanche-huang-confession-writer.md

## Inputs (exist on disk)
- cases/blanche-huang-confession/BRIEF.md (story, demand, rival ladder, titles)
- cases/blanche-huang-confession/research/ledger.md (ONLY fact source) + research/ledger_audit.md (which rows are verbatim-OK,
  numbers-OK, or paraphrase-only — obey it)
- cases/blanche-huang-confession/research/ref/2dwS_bn2tMM.txt (Brian Tyler Cohen, ~50K VPH, same story — reveal ladder model)
- cases/blanche-huang-confession/research/ref/TC-axC1IL00_cbs.txt (full presser transcript, start-seconds TAB text; our clip source)
- docs/CHANNEL.md, docs/SOUL.md (stance: pro-Democratic, anti-Trump/MAGA, pro-rule-of-law; opinion said as ours, facts exact)
- cases/trump-nvidia-huang/script-v3.md (yesterday's script on the same saga: do NOT reuse its openers, lead-ins, phrasing;
  viewers may have seen it — one-line recap of the backstory max)

## Task
Narration script, 8-9 min total: 1,100-1,300 spoken narration words (~165 wpm) + on-tape clips. Proof Politics = every beat rests
on tape or a document. Reveal ladder (mirror BTC, our own words):
1. B1 (0:00-0:15) payoff in plain words: the president told Nvidia's board its CEO was "exonerated" — and his own attorney general
   can't say anyone investigated. Then the clip: reporter's question + Blanche "I'm not going to get into communications I have
   with the president" (C1/C3, 0:01-0:50 of TC-axC1IL00, you may split it).
2. B2 (by 0:40) tease: "and then the president said the word pardon" (C7) — paid off near the end.
3. The dodge, clip by clip with our narration between: "investigated for what?" (1:08), "hundreds if not more export
   investigations" (2:01) -> but Megaspeed/Alice Huang's company is under DOJ investigation for diverting Nvidia chips (C13/C6,
   attributed) -> "good corporate citizen" (9:53) -> clearance "no information" (13:49).
4. Why it matters: the chips. DNI Jay Clayton (C5/C20): China appears to have had access to those chips; SDNY case (C6). NYT on
   Alice Huang / MSS (C12, paraphrase, attributed). One-line backstory recap (reinstated Monday after Trump's push).
5. Contradiction device: Trump said "a pretty good investigation" found Huang "exonerated" (C4) vs Blanche "what does that mean?".
   Blanche on Fox that night: "that assumes there is an investigation" (C25) if the ledger supports it.
6. Follow the money: at least 103 NVDA trades, twelve point five to fifty-eight million dollars (C8), more than thirty percent jump
   on reinstatement day (C11), the twenty-five-million ballroom (C9, say exactly what the source says: pledge/donation, by Nvidia).
   One fair line: no reporting proves the money bought the outcome.
7. Who Blanche works for: "I work for President Trump" (C10/C21 clip).
8. Pay off the tease: pardon "always an option, I guess, but I don't think it'll be necessary" (C7, print quote -> attributed, not a
   clip), plus Trump telling Huang not to take the Fifth before Congress.
9. Reaction: Raskin "gobbledygook" (C24), Schumer's rocket-engines line (C26), Rubio walking away when asked (C16/C23).
10. Close: verdict as OUR view; next dates (Huang's closed-door session with House committees next week per C15; Democrats take the
    House January third); ONE comment question to the viewer (not the rival's wording).
Rules: never say "illegal", "crime", "cover-up" or "spy" as fact — attribute ("US intelligence assessed", "the Times reported").
No quote marks around paraphrase. Every number in spoken words the way people say it ("one hundred and three times", "twelve and a
half million dollars", "twenty twenty-six", "November twenty-fourth"). Short sentences (avg 8-11 words), vary rhythm; no opener
used more than twice; every clip lead-in different; speaker named in the sentence. Each factual sentence ends with {C..}.
Clips on their own line as {CLIP Cn mm:ss-mm:ss "exact words"} — timestamps from TC-axC1IL00_cbs.txt for the presser (each clip
<= 20 s of speech), from the ledger row for others; max 8 clips.
After ## SCRIPT add ## ON-SCREEN: per beat the exact <=6-word text, doc/headline/post crop (real CNBC/NY Post/CNN pages, DOJ release).

## DONE-WHEN (countable)
- ## SCRIPT 1,100-1,350 narration words; payoff within first 30 words; tease before word 120; ends with a comment question.
- 0 factual sentences without {C..}; parity PASS vs BTC transcript.

OUTPUT: cases/blanche-huang-confession/script-v1.md
MINWORDS: cases/blanche-huang-confession/script-v1.md 1050 0
PARITY: cases/blanche-huang-confession/script-v1.md cases/blanche-huang-confession/research/ref/2dwS_bn2tMM.txt --ignore THE --ignore DAY --ignore Brian --ignore Wong --ignore Hang --ignore Hong --ignore Blanch --ignore consigary
