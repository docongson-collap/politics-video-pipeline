# WO — trump-oversight-order / researcher / 2026-11-23
Run: tools/role.sh researcher work-orders/trump-oversight-order-researcher.md

## Inputs (must exist on disk before dispatch)
- cases/trump-oversight-order/BRIEF.md
- cases/trump-oversight-order/research/ref/FfW2uazzwMk.txt (BTC + Marc Elias, top VPH)
- cases/trump-oversight-order/research/ref/YpdfsKXJfxY.txt (The Oversight Desk, faceless, best structured)
- cases/trump-oversight-order/research/ref/GcMI9SpZ-Iw.txt (Legal AF)

## Task
Build the claim + clip ledger for a 7-9 min pro-Democratic, anti-Trump explainer on Trump's Nov 20 2026 executive order
"Protecting the Executive's Privileges and Enhancing Efficiencies in Federal Contracting" (contractors must notify the White House of
congressional requests, coordinate, withhold what it calls privileged; penalty termination/suspension/debarment).
Start with `python3 tools/rival_parity.py --rival-facts <each rival transcript>`; every person/number said 2x+ gets a sourced row.

REQUIRED CLAIMS (one row each, primary source first):
K1 EO title, date signed (Nov 20), number (14,438 if confirmed) — whitehouse.gov presidential-actions page (exact text).
K2 Section 2 duties (notify / coordinate / abide by instructions on withholding) — exact EO text.
K3 Subcontractors covered; prime contractor responsible — EO text.
K4 Penalty section: termination/cancellation, debarment/suspension — EO text.
K5 "valid legislative purpose" / "certain congressional leaders have threatened" — EO text or fact sheet.
K6 Number of contractors (~100,000 per Bloomberg Government, as reported by ABC/GMA; AP "tens of thousands") and contract dollars (~$793B, find source).
K7 Democrats' majorities after the midterm (House seats count; Senate count) — AP or official, and Jan 3 2027 swearing-in.
K8 Raskin statement: the order has no "force" of law — Forbes clip suc6XA3Je50 with timestamp + any written statement.
K9 WH Counsel letter to Rep. Robert Garcia suggesting criminal exposure — ABC/AP article, exact lines.
K10 Will Scharf memo: agencies need WH permission before employees testify — ABC report, exact lines; Scharf on-camera quote (find clip + timestamp).
K11 Texas US attorney letters to senators/House members — source.
K12 Politico: "legality and enforceability of the order is unclear" + any legal expert quote (Elias "executive order can only bind the federal government").
K13 Executive privilege basis: US v. Nixon 1974 (Supreme Court) — primary.
K14 1789 Capital / Vulcan Elements $620M Pentagon loan / Raskin letter (only if sourced by AP/Reuters/major outlet); Don Jr. denial clip.
K15 Ballroom donors / contracts (Public Citizen via Fortune) — only if sourced; mark as "reported".
K16 Any White House defense line (fact sheet: "harassing private companies") — exact.
K17 Any Trump on-camera remark about Democrats' investigations / oversight this month (clip + timestamp).
CLIPS: find 6-10 short on-camera clips (YouTube URL + in/out timestamp + speaker + exact words) usable in the FIRST 60 SECONDS and body:
Raskin (Forbes suc6XA3Je50), NewsNation 7q384ildNcs, Scharf, Garcia, Trump, Jeffries/Schumer on oversight. Prefer network/C-SPAN/Forbes uploads.

Ledger format (tools/ledger_verify.py parses it): one block per claim:
### C1 | short claim
**Exact Quote:** verbatim text that is on the page
**URL:** https://...
**Date:** publish date / access 2026-11-23
**Clip:** URL + mm:ss-mm:ss (spoken quotes only)
**Confidence:** high/med/low
**Counterclaim:** ...

## DONE-WHEN (countable)
- ledger has >= 22 rows covering K1-K17 (missing ones listed under "GAPS" with reason), each with Exact Quote + live URL.
- >= 6 clip rows with YouTube URL + in/out timestamps + verbatim words.

OUTPUT: cases/trump-oversight-order/research/ledger.md
