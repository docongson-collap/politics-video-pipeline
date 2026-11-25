# WO — trump-nvidia-huang / researcher fix pass / 2026-11-24
Run: tools/role.sh researcher work-orders/trump-nvidia-huang-researcher2.md

## Inputs (exist on disk)
- cases/trump-nvidia-huang/research/ledger.md (v1, 25 rows)
- cases/trump-nvidia-huang/research/ledger_verify.md (tools/ledger_verify.py result: OK=7, 18 rows fail)

## Task
Write ledger v2 = v1 with every failing row fixed. The verifier fetches the URL and looks for the Exact Quote fragments and
numbers ON THAT PAGE. So for each failing row: either replace the URL with a page that really contains the exact words
(primary or wire copy: AP, Reuters, CNBC transcript, nvidianews, sec.gov 8-K, house.gov/senate.gov, Yahoo/MSN syndication of
the same story), or shorten the Exact Quote to words verbatim on the page. Never paraphrase inside Exact Quote.
- C3, C5, C7, C9, C10, C17, C18: NUMS (quote fragments not found on page) -> fix quote/URL.
- C12 WEAK, C13 MISSING (Trump's NVDA holdings: use OGE 278e / financial disclosure coverage with the exact range), C15 MISSING
  (Warren / Ricketts / Tim Scott: their own .senate.gov release or X post + wire copy).
- C8 DEAD: replace investing.com with NYT/Reuters/AP/CNN page on Alice Huang + MSS.
- C19 PAYWALL 403: keep the senate.gov URL, add a second row/URL from press (Reuters/CNBC) quoting Wyden/Neal.
- C20-C25 clips: YouTube watch pages are not verifiable from this machine (429). Give each clip row an Exact Quote + URL of a
  TEXT page that carries the same spoken words (CNBC transcript, network article, earnings-call transcript e.g. Motley Fool /
  Seeking Alpha / nvidia investor page, PBS transcript) and keep the video URL on the **Clip:** line.
Network rule: do NOT use any proxy (no ShardBrowser proxy, ever). Plain web tools only.

## DONE-WHEN (countable)
- `python3 tools/ledger_verify.py cases/trump-nvidia-huang/research/ledger-v2.md` shows NUMS+MISSING+DEAD+NOSRC <= 3,
  remaining failures listed under GAPS with reason.

OUTPUT: cases/trump-nvidia-huang/research/ledger-v2.md
