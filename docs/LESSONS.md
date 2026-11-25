# LESSONS — Politics
Inherited from Economic / Aviation (same pipeline, same owner). Each entry = mechanism, not story.

## Inherited — researcher ledgers paraphrase or invent quotes
- Economic dominos v1: only 5/50 quotes verbatim on the page; 2026-11-06 a researcher typed its own "source extracts" file.
- Mechanism: tools/ledger_verify.py always fetches the live URL; role.sh exits 5 on MISSING/DEAD/LOCAL. Factcheck runs in a separate session.
- Politics addition: a spoken quote needs a clip URL + timestamp, not a news article paraphrase.

## Inherited — verifier PASS is not coverage
- 121/132 rows were one World Bank JSON. Mechanism: WO carries numbered REQUIRED CLAIMS (K-ids) and ≤10 rows per domain; orchestrator greps K-ids.

## Inherited — script copied beats but not content or voice
- Mechanism: researcher starts from `rival_parity.py --rival-facts`; writer WO carries PARITY; role.sh exits 4 on FAIL.

## Inherited — parallel builders hit HTTP 429
- Mechanism: builders serial; runner waits 180 s before retry; WOs carry RESUME notes.

## Inherited — demand gate skipped / maker grading its own work
- Mechanism: scout's `DEMAND: PASS` required; qc never runs in the builder's session.

## Inherited — editing tools/role.sh while a role runs crashes its gates
- Mechanism: never edit role.sh while `pgrep -f tools/role.sh` is non-empty; edit a copy and mv it in when idle.
- When a gate's number disagrees with wc by >2x, check the gate parser before re-dispatching.

## 2026-11-22 alaska-doj-surrender (video 1)
- Fish WAVs carry a bogus 0x7FFFFFFF length header: never use Python `wave` for duration, use ffprobe (else segments render forever).
- ffmpeg zoompan on a still: NO `-loop 1` (zoompan emits d frames per input frame -> endless render).
- Card text in quotation marks must be verbatim from the source; paraphrases go without quotes (QC caught "Ballots were commingled").
- Network clips with burned-in subtitles: don't add our own caption over them if whisper differs from the network's text.
- tools/ocr_haiku.py needs the hermes-agent venv python, not system python3.
- owner: "làm thế này hỏng hết video". v1 cut measured: 24 flat PIL navy cards (one template x24), 18 static doc stills, only 9
  b-roll shots, ~51 shots in 8.5 min (~6/min vs 17-22 target), quotes/headlines retyped as slides, Truth post shown as a CBS
  screenshot, no word timing, no hook preview. Rule now in OPERATING 5b (Aviation Step 4b method: Envato template per need,
  EffectCraft, real headline/post/page with timed marker, one template one use).

- PRESS look (alaska-doj-surrender B2, Nov 2026): tools/fx/press_pass.py (Editorial News Match Cut: paper=Match Cut 1, web=Match Cut 19;
  outlet as plain-text kicker, never a masthead/logo; stretch the template's 1K "Paper003" square over the page or it shows as a
  grey box) + tools/fx/capture_pass.py (real page PNG + DOM rects, multiply marker, smootherstep camera). Mux voice with "-t dur",
  not "-shortest" (copy+shortest dropped 4 frames). alaskabeacon.com + nytimes = Cloudflare/bot wall in headless browser;
  democracydocket.com captures clean.

## 2026-11-22 alaska-doj-surrender hook v2 (edit pipeline)
- Envato "Document Highlighter v1.1" (093cae66): its marker/highlight comps render EMPTY in EffectCraft (expressions read a dashboard slider); default style = Negative Photostat (dark page). Use tools/fx/doc_pass.py = native rebuild from the template's own assets (wood desk, scanned paper, brush marker, dust). Verbatim phrase via pdftotext -bbox-layout, exit 2 if not found.
- Editorial News Match Cut works (tools/fx/press_pass.py, paper=Match Cut 1, web=Match Cut 19). Real page capture (tools/fx/capture_pass.py) beats template cards for credibility; Cloudflare blocks Alaska Beacon/NYT/Truth Social -> Democracy Docket / trumpstruth.org archive.
- Assembly (edit/hook.py): 24/25 fps sources held frames at 30 fps -> minterpolate those sources; `-ss` + fps filter duplicates the first frame of each shot -> setpts=PTS-STARTPTS before fps. Both found by judder_check (13 -> 0).
- Doc-heavy hooks land ~50% footage; the body must carry footage to reach 65%.
- Alaska elections site sits behind a CAPTCHA; sample ballots via web.archive.org (`if_/` raw URL).

## 2026-11-22 alaska-doj-surrender full v2 (body assembly)
- edit/full.py caches footage segs by <beat>_<index>; after inserting/removing shots in a beat, delete that beat's fseg files or stale segs get concatenated.
- Doc segs that end at beat end can be 1 frame short of the 30fps grid: pad graphics with tpad clone (0.2s) before -frames:v.
- doc_pass exits "push window too short" if push start -> first marker < ~0.7s; start the doc shot earlier or move the mark.
- Fox rally clip chyron changes mid-clip ("TRUMP: DEMS ARE A CORRUPT PARTY"); crop chyron + corner bug (crop=iw*0.64:ih*0.68:iw*0.06:0) and re-check edges by frame grab.
- Graphics-heavy body: footage share 58% on first pass; swapping chart/doc intros and verdict callbacks for footage got 63%. Plan footage-first next time (more b-roll sourced up front).
- Never read graphic segs while a subagent is still writing them (empty r_frame_rate crash); wait for the child's completion.

## 2026-11-24 corner logo overlay
- `-i logo.png` + overlay on alaska-doj-surrender-v2 drew the logo only ~5 s, then vanished (trump v2 was fine). Always
  `-loop 1 -framerate 30 -i corner.png` + `overlay=0:0:shortest=1`, then measure corner diff vs source every 25 s, not one frame.

## 2026-11-24 — Research network: NEVER use ShardBrowser IPs/proxies
owner (absolute): web research, scraping, yt-dlp, radar must NEVER go through any ShardBrowser proxy or profile IP
(proxies.json, profile "Facebook" or any other). Those IPs belong to the account personas only. Do not read proxy credentials.

## 2026-11-24 — trump-nvidia-huang build lessons
- Captions over page/evidence shots covered the highlighted line (v1). Fix: tools/fx/captions.py --doc <film ranges of
  WEBHEAD/POST/POSTSEQ/SPLIT/NUM/TIMELINE/FOOT-GFX rows> -> those cards drop to the bottom edge on a dark box. Always pass --doc.
- White corner logo collided with page text on white documents. Use a dark rounded plate behind the logo for the whole film
  (cases/trump-nvidia-huang/edit/logo_plate_1920.png pattern), not the bare logo.
- Fish wavs have a streaming header (nframes=0xFFFFFFFF): wave.getnframes() gives 89478 s. words_json.py now uses ffprobe.
- fish_voice.py voiced "(B3)" origin labels on the tag line; now silent. Keep origin labels in parentheses only.
- Envato: create assets/envato/ before the get loop; some items arrive as .zip -> unzip the .mov.
- zsh does not word-split "$Y" command variables: use a shell function.
- No video exists for some quotes (PBS "He's back where he should be"): voice it attributed + show the article; never fake a clip.
- FB composer "Your file can't be uploaded" (tooltip: "too small, minimum 1 KB") after fb_reel_compose.sh: transient 0-byte read in a reused tab. Fix: shard_fb_cdp.py fresh -> nav /me -> files on the video input directly; it attached fine.
- FB hashtag autocomplete pops up after the pasted caption (offered #democratsdestroyeverything): dismiss, never accept.
