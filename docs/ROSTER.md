# ROSTER — Politics roles, models, gates

Runner: `tools/role.sh <role> <WO.md>` (model/provider/toolsets hard-coded per role).
Each WO lists `OUTPUT: <path>` lines; role.sh exits 3 if any output is missing or not written by this run.
Writer WOs must also carry `PARITY: <script> <rival transcript>`; role.sh exits 4 on FAIL.
Researcher outputs named *ledger*.md are checked by tools/ledger_verify.py (exit 5 on MISSING/DEAD).
WO template: control/templates/WO.md. WOs in English, ≤ 4 scenes for builders, DONE-WHEN countable.
Never dispatch a WO before its inputs exist on disk.

| # | Role | Provider / model | Gate it feeds |
|---|---|---|---|
| 0 | orchestrator | Hermes profile `pol` | every gate; eye check before owner |
| 1 | scout | anthropic / claude-haiku-4-5 | demand gate (vidIQ ≥1000 or 3-channel news cluster) |
| 2 | researcher | anthropic / claude-sonnet-4-6 | claim + clip ledger |
| 3 | writer | anthropic / claude-sonnet-5-5 | script (+ rival parity) |
| 4 | factcheck | anthropic / claude-sonnet-5-5 | script facts + quotes (0 FAIL), separate session |
| 5 | visual | anthropic / claude-opus-5-5 | shot-map + clip windows |
| 6 | builder | anthropic / claude-sonnet-5 | chapter renders |
| 7 | qc | anthropic / claude-sonnet-5 | machine gates + frame review (tools/ocr_haiku.py) |
| 8 | packaging | anthropic / claude-haiku-4-5 | title/thumb/desc/tags |

All roles run Claude via the Hermes credential. No Gemini, OmniRoute or 9router.
Order: scout → (PASS) researcher → writer → factcheck → voice → visual → builders (serial) → assemble → qc → orchestrator eye → packaging → Drive.
A FAIL stops the line. Opus/Sonnet builders run ONE AT A TIME (parallel = HTTP 429). Runners are resumable.
News speed target: pick → upload ≤ 24 h. If a step blocks > 2 h, orchestrator does it directly.

## role: scout
Goal: prove or refuse current demand for ONE news story.
- Chrome profile congson.neu (vidIQ), via the relay in docs/OPERATING.md; reuse an existing YouTube tab, never close his tabs.
- Live vidIQ VPH badge only. Scan @briantylercohen latest 30 + every channel in docs/COMPETITORS.md + the story query (this week).
- Table: id, title, channel, age, exact badge text, date read. Breaking cluster = ≥3 channels on the same story < 24 h.
- Prefer a story still climbing after 6–24 h and with no faceless explainer yet.
- DONE-WHEN: last line `DEMAND: PASS <id> <vph>` / `DEMAND: PASS CLUSTER <n> channels` or `DEMAND: FAIL`.

## role: researcher
Goal: claim + clip ledger the script can stand on.
- Start from the rival transcript: `tools/rival_parity.py --rival-facts <rival.txt>`; every person/number said ≥2x gets a sourced row.
- Primary first: the original clip (network/committee/C-SPAN page + timestamp), congress.gov, court filings (CourtListener), official
  election results, AP/Reuters. Partisan sites only as "X reported", never as fact.
- Each row: ID, claim, exact quote, URL, publish date, access date, clip URL + in/out timestamp if spoken, confidence, counterclaim.
- DONE-WHEN: ledger has the WO's claim count; every row has quote + URL; every spoken quote has clip + timestamp.

## role: writer
Goal: BTC-grade script from the ledger only.
- Copy the top-VPH same-story transcript beat by beat: hook (who got hit), clip setups ("watch this"), reaction lines, context, consequence, what's next.
- Mark clips inline: [CLIP K7 00:12–00:31]. Narration between clips ≤ 40 s.
- Beats [B1]..[Bn]; every factual sentence ends with its claim ID {C12}. 160–175 wpm. Numbers written as spoken words.
- Never add a fact not in the ledger; list gaps under "MISSING CLAIMS".
- DONE-WHEN: word count in range, 0 untagged factual sentences, rival_parity PASS.

## role: factcheck
Goal: independent check in a clean session.
- Open every URL and every clip timestamp; confirm the quote is verbatim and the sentence does not overstate (alleged vs proven,
  proposed vs passed, projected vs certified, who said it).
- DONE-WHEN: every tagged sentence and every [CLIP] has PASS/FAIL/WEAK + reason.

## role: visual
Goal: each spoken claim gets an exact visual.
- shot-map: beat, words, evidence, source + window, treatment (clip / headline page capture / filing page highlight / X post /
  results map / number card), rights note, MATCH/NO MATCH.
- Clips keep the outlet bug; ≤ ~20 s continuous; no foreign burned-in text; no AI images of real people.
- DONE-WHEN: 0 NO MATCH rows, every clip row has a window + SOURCES.md line.

## role: builder
Goal: turn assigned beats into a chapter in the approved look (case studio/PLANNER_BRIEF.md is the law).
- Cuts on word times; text arrives when the voice says it. Save a draft within ~10 tool calls; rerun until gates PASS.
- Render only if the WO says so.
- DONE-WHEN: the WO's OUTPUT exists and its gates pass.

## role: qc
Goal: catch what the maker cannot see (clean session).
- Frames at every quote, name and number; on-screen text vs script; wrong person/face labels; flashes; frozen holds; clip > 20 s; missing source.
- DONE-WHEN: every issue with timecode + frame path, or 0 per check.

## role: packaging
Goal: title/thumb/desc/tags mirroring the top live-VPH video on the same story.
- Title in BTC grammar (emotion tag + person + hit, CAPS keywords), ≤ 70 chars, no claim the video does not prove.
- Thumb: real frame/photo, rival layout, no arrows, no AI art. Tags from a live VPH scan (delivery/tags-research.md).
- DONE-WHEN: title.txt, description.txt (sources listed), tags.txt, thumb, tags-research.md.
