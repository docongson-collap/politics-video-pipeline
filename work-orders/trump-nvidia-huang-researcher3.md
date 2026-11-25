# WO — trump-nvidia-huang / researcher fix pass 3 / 2026-11-24
Run: tools/role.sh researcher work-orders/trump-nvidia-huang-researcher3.md

## Inputs (exist on disk)
- cases/trump-nvidia-huang/research/ledger-v3.md (31 rows; C26-C31 added from rival parity with BTC qhq5GD104I4)
- cases/trump-nvidia-huang/research/ledger-v3_verify.md (OK=23; failing: C28-C31 MISSING, C10/C19/C22 PAYWALL 403, C12 WEAK)
- cases/trump-nvidia-huang/research/ref/qhq5GD104I4.txt (BTC transcript, top same-stance rival)

## Task
Write ledger-v4 = ledger-v3 with the failing rows re-sourced to pages that a plain urllib fetch can read and that contain the
Exact Quote verbatim (AP copy syndicated on abcnews.go.com / usnews / yahoo / local TV sites, CNBC, Reuters, the senator's own
.senate.gov release, x.com post URL as secondary). PBS and the Guardian block the verifier; replace them.
- C28 Cornyn "No national security risk? Based on what?" + defensive briefing question.
- C29 Tim Scott: Huang testifies publicly before Senate Banking Dec. 3; Warren "reckless".
- C30 Trump to CNBC "I believed my intervention was very important ... JD and Scott ... Howard" — find CNBC transcript/article text.
- C31 House Intelligence spokesperson "changes nothing" (NBC News original).
- C10/C22 Harvey Jones "does not intend to reinstate": use TechCrunch 2026-11-17 or CNN 2026-11-17 (both quote it).
- C19 keep senate.gov, add a readable press URL quoting Wyden/Neal.
- C12: make the quote match the page exactly.
Network rule: do NOT use any proxy (no ShardBrowser proxy, ever). Plain web tools only.

## DONE-WHEN (countable)
- `python3 tools/ledger_verify.py cases/trump-nvidia-huang/research/ledger-v4.md` -> failures (everything not OK) <= 2,
  listed under GAPS with reason.

OUTPUT: cases/trump-nvidia-huang/research/ledger-v4.md
