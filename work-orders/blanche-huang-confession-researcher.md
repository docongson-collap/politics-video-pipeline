# WO — blanche-huang-confession / researcher / 2026-11-25
Run: tools/role.sh researcher work-orders/blanche-huang-confession-researcher.md

## Inputs (exist on disk)
- cases/blanche-huang-confession/BRIEF.md
- cases/blanche-huang-confession/research/ref/2dwS_bn2tMM.txt (rival transcript, start-seconds TAB text)
- cases/trump-nvidia-huang/research/ledger-v4.md (yesterday's verified background — re-check any row you reuse)

## Task
Claim + clip ledger for an 8-11 min pro-Democratic, anti-Trump news video: AG Todd Blanche dodged whether DOJ ever investigated
Jensen Huang before Trump called him "exonerated"; China got the chips; Trump owns NVDA, floats a pardon.
Never write "illegal"/"crime"/"cover-up" as fact; attribute every allegation. Network/research traffic: normal internet only,
NEVER any ShardBrowser proxy.

REQUIRED CLAIMS (one row each, primary source first):
K1 Blanche presser date/place/occasion (Nov 24 2026?) + verbatim lines: "I'm not going to get into communications I have with the
   president", "talk about investigation, but what does that mean?", "we have hundreds if not more export investigations",
   "I don't have any information about even what his clearance status is" — video URL + timestamps (DOJ YouTube / C-SPAN / network).
K2 The reporter's question wording ("exonerated ... one of the assurances to Nvidia's board") + who asked if known.
K3 Trump's "exonerated"/"assurance" claim (CNBC Nov 23) — reuse/verify from ledger-v4.
K4 Intelligence/law official admitting China got Nvidia chips: exact person + exact title (BTC says "director of national
   intelligence Jay Clayton" — verify; correct it if wrong), date, verbatim "it appears ... there was access to those chips. Yes." + clip.
K5 SDNY indictment for diverting Nvidia chips to China (justice.gov press release: company, date, route e.g. Singapore).
K6 Trump to New York Post: pardon for Huang "always an option", didn't think necessary — exact + date.
K7 CNBC analysis: Trump Nvidia holdings $12.5M-$58M (as of end 2025), accounts traded NVDA 100+ times since Jan 2025 — exact.
K8 Nvidia $25M to the White House ballroom — source (who reported, exact wording, is it Nvidia or Huang).
K9 Blanche "I work for President Trump" quote: date, venue, verbatim + clip.
K10 NVDA move on reinstatement day (reuse/verify ledger-v4) + Trump stock-holding WH response.
K11 Alice Huang / MSS assessment + Megaspeed blacklist (reuse/verify ledger-v4), one line each.
K12 Any DOJ/FBI statement on whether Huang was interviewed/investigated; any reporting (NYT/WSJ/CNN) that DOJ did NOT investigate.
K13 Democratic reactions Nov 24-25 to Blanche's answers (Jeffries, Raskin, Durbin, Warner, Warren...) — exact.
K14 Next dates: Dec 1 Huang congressional interviews; Dems take House majority Jan 3 2027; Jeffries probe of Nvidia + Commerce.
K15 Rubio dodging the Huang security-risk question Nov 24 (BTC R6YQZWDl7U0) — source clip + words.
CLIPS: >= 6 rows with YouTube URL + in/out + speaker + verbatim words (Blanche x3+, intel official, "I work for President Trump",
pardon news report or Trump audio, Rubio). Prefer DOJ/C-SPAN/network uploads, NOT BTC's video.

Ledger format (tools/ledger_verify.py parses it): one block per claim:
### C1 | short claim
**Exact Quote:** verbatim text that is on the page
**URL:** https://...
**Date:** publish date / access 2026-11-25
**Clip:** URL + mm:ss-mm:ss (spoken quotes only)
**Confidence:** high/med/low
**Counterclaim:** ...

## DONE-WHEN (countable)
- ledger has >= 22 rows covering K1-K15 (missing ones under "GAPS" with reason), each with Exact Quote + live URL.
- >= 6 clip rows with YouTube URL + in/out timestamps + verbatim words (mark "timestamp unverified" if not watched).

OUTPUT: cases/blanche-huang-confession/research/ledger.md
