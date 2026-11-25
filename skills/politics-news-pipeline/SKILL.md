---
name: politics-news-pipeline
description: "Use when making Politics videos or researching rivals."
---

# Politics news pipeline (pick → upload ≤ 24 h)

Project: /Volumes/WORK/Auto Film Factory/Politics. Rules: CLAUDE.md. Roles: docs/ROSTER.md. Steps: docs/OPERATING.md.

## Steps
1. Scout (live vidIQ via CDP relay): BTC latest 30 + docs/COMPETITORS.md + story queries this week.
   PASS = same-story video ≥1000 live VPH, or ≥3 channels on the story < 24 h. Pick the best yourself; write cases/<slug>/BRIEF.md.
2. Rival transcript of the top same-story video -> cases/<slug>/research/ref/<id>.txt.
3. Researcher ledger: claims + clip URL + in/out timestamp for every spoken quote (tools/ledger_verify.py gate).
4. Writer script (PARITY gate), clips marked [CLIP Kn mm:ss–mm:ss], numbers as spoken words. Factcheck in a clean session, 0 FAIL.
5. Voice: tools/fish_voice.py, tools/asr_check.py, re-TTS misreads.
6. Clips: yt-dlp source, cut windows ≤ ~20 s, keep outlet bug; headlines/filings as real page captures; X posts real.
6b. Edit direction BEFORE building (docs/OPERATING.md 5b, Aviation Step 4b method): Envato templates per visual need
   (press headline, X/Truth post, filing, chart, timeline) gated in EffectCraft; real headline/post/page with a marker timed to
   the spoken word; one template one use; footage 65-75 %, 17-22 cuts/min; hook preview first. Flat PIL slide cards = rejected
   (v1 alaska-doj-surrender: 24 identical cards, ~6 cuts/min, owner: "hỏng hết video").
   Working toolkit + recipe in references/edit-v2-toolkit.md (tools/fx/doc_pass.py, press_pass.py, capture_pass.py,
   case edit/hook.py assembler, footage.tsv via skill politics-footage-shotlist). Parallelise: one subagent per look
   (doc / press / footage) with a shared research/v2_context.md, then assemble + gate yourself.
   Gate the hook before showing owner: judder_check = 0, ebur128 ~-16 LUFS, contact sheet every 2 s eyed, footage share +
   cuts/min printed. Doc-heavy hooks land ~50 % footage — make the body footage-heavy to reach 65 %.
   After hook OK: write the body shot table (edit/full.py), and in parallel: doc_pass specs run serially in background
   yourself (EC lock), one subagent for PRESS/POST captures, one for NUM/timeline; pre-render footage with --partial;
   eye every QC tile yourself before assembling. Body table footage-first (graphics start right before their first
   pop/marker); full.py prints footage share — below 65 % trim graphics into b-roll before delivering.
   Final report to owner: output path, the numbers (length, shots, cuts/min, footage %, judder, LUFS), what each section
   shows, fixes made, honest weak spots, then TITLE / DESCRIPTION / TAGS pasted + thumbnail path.
7. Build chapters serially, assemble, qc (tools/ocr_haiku.py), contact sheet 1 frame/5 s checked by eye.
8. Packaging from live VPH (title in BTC grammar, real-frame thumb, tags-research.md) -> tools/deliver.py -> report to owner.
9. Facebook cut of the packaging + posting via the ShardBrowser profile "Facebook" ONLY (never any other profile, never a new
   account) — see references/facebook-distribution.md

Clip audit (when owner asks how much network footage is used): count from edit/full_shots.tsv joined to edit/footage.tsv by
source id, in Python — report shots, seconds, % of runtime per outlet, and which clips keep live sound (each ≤ ~20 s).

## Stance
One consistent view (docs/CHANNEL.md): pro-Dem, anti-Trump/MAGA. Script frames the story and ends with our verdict; opinion is
said as ours, quotes/numbers exact. Recipe: docs/research/competitors/stance_analysis.md (144-video coded study): tease +
damning clip/doc open, contradiction/hypocrisy device, insult 0-1, one 'to be fair' line, no Dem criticism, close = verdict +
next date + identity CTA (prescription close = 0.52x views).
That recipe came from a 16-video read and is PROVISIONAL until the coded corpus (discovery/stance_corpus/, ~144 transcripts) is
summarised; update it from the counts, not from impressions.

## Rival research (competitors, stance, title grammar)
Procedure + commands in references/rival-research.md (always-on rules below):
- Competitors = channels with the SAME consistent pro-Dem/anti-Trump stance. Neutral aggregators/clip dumps (Hook Global, Forbes
  Breaking News, networks) are clip sources and demand signals, never models; owner rejected an aggregator-style channel.
- Split rivals into host channels (demand proof) vs faceless (format proof) vs slop (invented thumbnail quotes) to avoid.
- Never draw conclusions from a handful of videos: owner rejects it. Minimum ~10 channels x ~15 recent long videos, coded with one
  codebook into JSON, then counted in Python; plus ~200 titles/channel for title-level features. Report numbers, not anecdotes.

## Pitfalls
- A news story older than 48 h at delivery: switch to an explainer angle or drop it.
- Never put words in a politician's mouth: no paraphrase inside quote marks, no AI voice, no AI face.
- Hook Global style full-clip re-uploads = reused-content risk; narration must carry each segment.
- Record new lessons in docs/LESSONS.md and patch this skill the same turn.
