# Edit v2 toolkit (Envato/EffectCraft looks + real captures + assembly)

Shared EffectCraft how-to: /Users/doson/.hermes/skills/media/envato-elements-download/references/ae-templates-effectcraft.md
(read-only for this profile — record Politics verdicts here and in docs/LESSONS.md).

## Envato
- `tools/envato.py` (copied from Travel; cookies read in place via ENVATO_SECRETS, never printed). License project = "Politics".
- Search results JSON carry full itemUuid — always take the uuid from search output; never type/guess a uuid (guessed ones
  return "Download failed"). Licenses + PDFs land next to the zip; log in kho/envato_templates/LICENSES.json.
- Triage: curl preview mp4, 8-frame tile per template, one vision look, then license the shortlist.

## Looks (Politics verdicts)
| Look | Template | Status |
|---|---|---|
| DOC filing/ballot | Document Highlighter v1.1 (093cae66) | Its own marker comps render empty + Negative Photostat default in EC -> `tools/fx/doc_pass.py <BEAT> <spec.json>` rebuilds the look from the template's assets (wood desk, scanned paper multiply, brush marker via track matte, dust MULTIPLY). Whole page -> one smootherstep push -> settle -> marker at words.json time. Phrase located with `pdftotext -bbox-layout`; exit 2 if not verbatim. |
| PRESS headline | Editorial News Match Cut (a8d88afb) | `tools/fx/press_pass.py` paper=Match Cut 1, web=Match Cut 19. No fake outlet logo: outlet as plain text kicker. Looks flat alone — prefer over footage. |
| PRESS real page | browser capture + DOM rects | `tools/fx/capture_pass.py` — more credible than template cards. Second marker must hit words the voice actually says. |
| PRESS tall page (headline -> later paragraph) | `tools/fx/tall_capture.py` (exec after quote_capture.py in browser_exec) | One captureBeyondViewport band at DPR 2 (clip scale MUST be 1 — scale multiplies DPR -> 4x image). Picks the first VISIBLE match (hidden duplicates of h1 exist). CLEAN_JS breaks some navs (AP) — skip it when the page is clean. Multi-line headline rects overlap vertically -> trim y per line + `pad:[5,0]` or the overlap band double-darkens. Light text on dark hero (AP, NBC): mark `"mode":"invert"` in capture_pass. Put frame top/bottom edges in paragraph gaps (row-ink profile) so no half lines at edges. |
| POST animated | `tools/fx/post_pass.py <spec>` | card over blurred footage; tesseract word boxes locate phrases (exit 2 if not verbatim); crop the bg (`bg_crop`) above the network chyron or blurred chyron text still reads. |
| POST (Truth Social) | real capture | truthsocial.com and its API are Cloudflare-blocked headless; capture the `.status` card from trumpstruth.org/statuses/<n> (archive keeps original status ID) via CDP Page.captureScreenshot clip at scale 2. |
| NUM chart / seat arc / timeline | Flat DataViz 404f4682 (chart) / 1a546449 (timeline) | `tools/fx/num_pass.py N17\|...\|all`, specs CASE/edit/specs/num_<shot>.json. EC render of the template comp with its chrome/palette/Inter font kept; expression-driven bar rows switched off and rebuilt as keyed shape/text layers (word-anchored pops, blocks sliding onto bars, CAM null slow push so no frozen frame). Template font Inter must be installed where EffectCraft sees it. One template = the whole consecutive numbers story. Exact figure on screen even when voice rounds ("more than 7,700" -> 7,756). |
| Photoreal Newspaper (d30cce40) | 3D plates RGB/OB/AO 4K 25 fps | licensed, not tested |
| Election Pack (4327d1cb) | Premiere MOGRTs only | not usable without Premiere |

## doc_pass batch runs
- One spec per (page, window); a phrase on another page = another spec. Find pages first: per-page `pdftotext -f i -l i`
  with whitespace collapsed, match the phrase lowercase.
- Batch with `while read beat name; do python3 tools/fx/doc_pass.py $beat spec.json < /dev/null; done < jobs.txt` —
  without `< /dev/null` the pass eats the loop's stdin and later lines arrive truncated (KeyError '3', empty spec name).
- Keep >= ~0.7 s between push start and the first marker or the pass exits "push window too short"; move `from`/`push.at`
  earlier or anchor the mark later (a number in seconds works as `at`).
- Callbacks (verdict beat) can reuse an earlier doc seg with an offset late enough that the marker is already drawn.

## Real sources that block bots
- elections.alaska.gov PDFs sit behind a CAPTCHA: get them via Wayback `https://archive.org/wayback/available?url=...`
  then the `if_/` raw URL.
- Alaska Beacon / NYT / Truth Social / apnews.com: Cloudflare -> use another outlet (Democracy Docket, CNBC, NBC work) or an archive.
  Paywalled outlet report (NYT): capture an outlet that reports it with attribution in its headline (e.g. CNBC '...: NYT').
  Voice credit must match the page: an AP-bylined story on nbcnews.com is fine to cite as NBC News; pick the article whose
  wording matches the voice ('roughly 20,000' vs 'over 20,000').
  apnews.com articles render from Wayback (`web.archive.org/web/<ts>/<url>`, remove #wm-ipp-base); images often not archived.
- vision_analyze refuses a 4th load of the same file path: write each QC frame to a new filename.

## Word timing
`whisper-cli -m kho/whisper-models/ggml-small.en.bin -f B.16k.wav -ml 1 -sow -oj` per beat -> audio_full_v1/words.json
({beat: [{w,s,e}]}). On-screen text and marker sweeps anchor to these times (±0.3 s).

## Assembly (case edit/hook.py pattern)
- Shot table per beat: (t0, t1, source, src_offset, label); boundaries snapped to the cumulative 30 fps grid; verify each
  segment's frame count; concat -c copy; audio = per-part loudnorm I=-16 + apad/atrim to the exact part length, concat.
- Sources at 24/25 fps give held frames at 30 -> run `minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1`
  on those sources only (detect r_frame_rate).
- `-ss` + fps filter duplicates each shot's first frame -> put `setpts=PTS-STARTPTS` before scale/fps.
- judder_check (tools/fx/judder_check.py) flags a hold right before a hard cut on near-static footage — inspect frame diffs
  before "fixing" those.
- Soundbite clips without burned subtitles get a verbatim caption PNG near the top (ffmpeg has no drawtext); keep the network
  bug/chyron visible.
- Full video = case edit/full.py: imports hook.SHOTS for the hook, BODY table for the rest, KCLIPS {pieces, lower third,
  verbatim captions timed relative to clip start} for source soundbites; prints footage share, cuts/min and max run of
  consecutive graphics (labels DOC/PRESS/POST/NUM = graphics). Graphic segs start at their spec `from`, so
  offset = t0 - from. `--partial` pre-renders footage segs while graphics are still being built (cached; minterpolate makes
  ~80 shots take ~13 min). Graphic segs ending at beat end can be 1 frame short of the snapped grid -> pad with
  `tpad=stop_mode=clone:stop_duration=0.2` on graphics only.
- Footage segs are cached as fseg/<beat>_<index>.mp4: after inserting/removing a shot in a beat, delete that beat's fseg files
  first, or stale segs with shifted indices get concatenated silently. Final output goes to Politics/output/ (project root),
  not the case dir; copy into CASE/delivery/.
- Footage share falls short on graphics-heavy bodies (first pass ~58 %). Fix by footage-first trims, not new graphics: start
  each NUM/doc shot just before its first pop/marker (cover the intro with b-roll), cut doc tails after the marker lands,
  and replace verdict-beat doc callbacks with footage. Plan the body table footage-first so it lands >= 65 %.
- Network chyrons change mid-clip (Fox rally: 'TRUMP: DEMS ARE A CORRUPT PARTY' = words not on tape). Check every soundbite
  piece's chyron; if it editorialises, crop chyron AND corner bug per piece (Fox 720p: `crop=iw*0.64:ih*0.68:iw*0.06:0`)
  and re-grab a full-res frame to confirm no logo sliver at any edge.
- judder_check flags the first frame of an ease-in move (POST card start, diff ~0.4) — compare first-frame diffs of the
  standalone seg; if identical it is the ease, not a stutter.
- Do not assemble/probe while subagents are still writing segs: a half-written mp4 has no stream and ffprobe returns ''.
- Thin footage pool: mine long news clips already downloaded — scene list (edit/scenes.json) -> midpoint frames -> one
  contact sheet per clip -> vision -> pick clean b-roll (no studio anchor, crop tickers with a `crop=` per shot).
- Contact sheet: grab single frames with -ss per time and tile (fps=1/2,tile=5x6 on a short clip emits a partial/odd tile).
