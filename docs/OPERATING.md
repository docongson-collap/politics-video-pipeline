# OPERATING — Politics

## Layout
cases/<slug>/  BRIEF.md, research/ (ref transcripts, ledger, shot-map), script-vN.md, full.txt, SOURCES.md, assets/, audio/, build/, delivery/
work-orders/   WOs + logs/ (role.sh transcripts)
tools/         copied from Economic 22/11: role.sh, rival_parity.py, ledger_verify.py, vidiq_*.py, fish_voice.py, asr_check.py,
               ocr_haiku.py, scenes/, deliver.py, delivery/sheet_cdp.py, yt_tags.py, comp_profile.py, recent_velocity.sh, make_corner_logo.py
docs/research/btc_catalog.tsv  rival catalog (yt-dlp --flat-playlist, 800 latest)
kho/           local venvs, models, footage cache (gitignored)

## Pipeline (each step = one WO via tools/role.sh, or orchestrator directly when speed demands)
0. Topic: scout reads live vidIQ VPH on BTC latest + COMPETITORS + story queries. PASS = same-story video ≥1000 VPH or a 3-channel cluster.
1. BRIEF.md: story, rival reference (id + VPH), the hit, the consequence, 3 titles in BTC grammar, clips + documents needed.
2. Rival transcript -> cases/<slug>/research/ref/<id>.txt (yt-dlp auto-subs; if bot-blocked use youtube-transcript-api in a kho venv).
3. researcher ledger (claims + clip timestamps) -> writer script (PARITY gate) -> factcheck 0 FAIL.
4. Voice: tools/fish_voice.py per line (key in ~/.config/son/fish.env, never print), tools/asr_check.py word times + misread re-TTS.
5. Clips: download source clips (yt-dlp) into cases/<slug>/assets/clips, cut exact windows; visual shot-map -> builders (serial) -> assemble -> qc.
5b. Edit direction (copied from Aviation OPERATING Step 4b + AVIATION_VISUAL_LANGUAGE, owner 22/11 "làm thế này hỏng hết video"):
   - Never build cards/quotes/headlines from flat PIL slides. Per video: list 3-5 visual needs (press headline, X/Truth post,
     court filing, vote chart, timeline), search Envato video-templates (copy Travel/tools/envato.py), tile previews, pick
     2-3, license to the case, gate in EffectCraft (render 4+ frames vs preview), log in cases/<slug>/research/edit_direction.md
     and docs/EDIT_LOOKS.md. Templates proven in Aviation: Editorial News Match Cut a8d88afb (press), X Social Media motion_en
     7e6b7f2e (posts), Flat DataViz bars 404f4682 / timeline 1a546449 — Politics must license its own copies.
   - Press/quote = VERBATIM real headline + quote from the outlet, yellow marker sweeps while the voice says it (words.json).
     Web article = real page capture (DOM rects, Aviation sydney-london/v1/quote_capture.py): headline first, scroll, then
     highlight. Court filing = whole page -> one push to target line -> marker sweep. Never retype a claim as a fake card.
   - One template, one use per film; footage 65-75%, 17-22 cuts/min, no >2 text cards in a row; text <=6 words, lands ±0.3 s
     of the spoken word; outlet bug visible on every borrowed clip; no unrelated burned-in captions under narration.
   - Hook preview (45-70 s) before the full edit.
6. Orchestrator eye check (contact sheet, 1 frame / 5 s) -> packaging -> tools/deliver.py (Drive + Sheet) -> report to owner.
Chain steps in cases/<slug>/run.sh (resumable). Report each step to owner.

## Live vidIQ (owner's real Chrome)
browser_exec Chromium has no Google login and no vidIQ. Use the CDP relay on port 9333 (ONE Allow per Chrome session):
`lsof -nP -iTCP:9333 -sTCP:LISTEN`; if down copy Aviation's hardened cdp_relay.py + real_chrome.py into tools/ (do not import
across projects), start the relay once in background, tell owner one line to click Allow. Detail: skill youtube-competitor-research.

## Delivery
tools/deliver.py uploads video + thumb to Drive (Video/<CHANNEL>, Thumb/<CHANNEL>) and fills the Sheet via API.
CHANNEL is "TBD" until owner names the channel: deliver.py stops with an error until docs/CHANNEL.md + CHANNEL are set.

## Channel name corner
Once named: tools/make_corner_logo.py -> docs/brand/corner_logo_1080.png, overlay top-left for the whole film.
Sources and credits live in the description, not on screen.
