# WO — trump-nvidia-huang / writer v2 (parity fix) / 2026-11-24
Run: tools/role.sh writer work-orders/trump-nvidia-huang-writer2.md

## Inputs (exist on disk)
- cases/trump-nvidia-huang/script-v1.md (1,269 words; parity FAIL)
- cases/trump-nvidia-huang/research/ledger-v4.md (ONLY fact source)
- cases/trump-nvidia-huang/research/ref/qhq5GD104I4.txt (BTC rival transcript)

## Why
Parity gate on v1: short punch sentences 13% (< 16% needed; rival 27%). Missing rival entity "Scott": Trump told CNBC he worked
with "JD and Scott" and Howard Lutnick (C30) — the ledger row's exact words decide who is named; do not guess a surname that the
ledger does not give. ("hang", "us", "america", "according" are transcript noise and are ignored.)

## Task
script-v1 -> script-v2: SAME facts, SAME claim tags, SAME clips and beat order. Only:
1. Turn ~25 long sentences into punches: short sentences of 1-5 words ("He said it out loud." "Six days." "Based on what?").
   Target >= 22% sentences of <= 5 words, average still 8-11 words.
2. Use the C30 line so the viewer hears who Trump says he worked with (JD, Scott, Howard), tagged {C30}.
3. No new facts, names or numbers; numbers stay as spoken words.

## DONE-WHEN (countable)
- ## SCRIPT 1,150-1,350 words; parity PASS.

OUTPUT: cases/trump-nvidia-huang/script-v2.md
MINWORDS: cases/trump-nvidia-huang/script-v2.md 1100 0
PARITY: cases/trump-nvidia-huang/script-v2.md cases/trump-nvidia-huang/research/ref/qhq5GD104I4.txt --ignore Daddy --ignore THE --ignore DAY --ignore Brian --ignore hang --ignore us --ignore america --ignore according
