# Video workflow (US political news explainer, 8–11 min)

Pick a hot story -> published video in under 24 h. Each stage runs as an AI agent "role"
(`tools/role.sh <role> work-orders/<slug>-<role>.md`). The orchestrator writes the work order (WO),
gates the output, and moves to the next stage. Worked example of every file: `cases/blanche-huang-confession/`
and its WOs in `work-orders/blanche-huang-confession-*.md`.

Detailed rules: `skills/politics-news-pipeline/SKILL.md`, `docs/OPERATING.md`, `docs/LESSONS.md`.

## 1. Pick the story (scout)
- Watch the main rival channels (docs/COMPETITORS.md). Pick a story whose rival video is running
  >= 1000 views/hour, or that 3+ channels covered in the last 24 h.
- Write `cases/<slug>/BRIEF.md`: angle, rival video id, what must be proved, hard rules.

## 2. Research (researcher)
- Rival transcript -> `research/ref/`. Primary sources only (full press conference, filings, original interviews).
- Output `research/ledger.md`: every claim with source URL; every quote with clip file + in/out timestamp.
- Gate: `tools/ledger_verify.py`. Quotes that can't be verified word for word are paraphrased, never quoted.

## 3. Script (writer) + factcheck
- `script-vN.md`, ~1200–1400 words. Clips marked `{CLIP Kn file mm:ss-mm:ss "quote"}`.
  Numbers written as spoken ("twenty-five million"). Allegations always attributed.
- Rival parity gate: `tools/rival_parity.py` (cover the rival's key entities).
- Factcheck in a clean session -> `factcheck-vN.md` (PASS/FIX/FAIL per sentence). Fix all FAIL before voice.

## 4. Voice
- Split script into VO segments (`script-full-v1.md`, `edit_plan_v1.json`).
- TTS: `tools/fish_voice.py` (needs FISH_API_KEY). ASR check: `tools/asr_check.py`; re-TTS any misread line.
- Word timings: `tools/words_json.py` -> `audio_full_v1/words.json`.

## 5. Clips
- Download the original source video (yt-dlp), run whisper on it to get exact timestamps
  (YouTube captions drift). Index in `assets/clip_index.md`. Live-sound clips <= ~20 s each.

## 6. Shot map (visual)
- `edit/shotmap_v1.tsv`: one row per shot, timed to the spoken word.
  Targets: footage 65–75 %, 17–22 cuts/min, no shot > 6 s, every template used once.
- Graphics = real web pages / filings / posts, captured and highlighted on the exact phrase being read.

## 7. Graphics
- `edit/build_graphics.py` (+ `edit/work/plan.py`): capture pages, highlight, render each graphic segment.
- QC by eye on a contact sheet: no cookie/popup banners, no half-cut lines, highlight on the right words.

## 8. Build (builder)
- `edit/full_v1.py`: renders every shot, assembles, adds corner logo, normalises to -16 LUFS.
- Captions: `tools/fx/captions.py` -> burned in with ffmpeg `ass=`.
- QC: contact sheet 1 frame / 5–6 s checked by eye (no anchors talking under narration, no unrelated chyrons/tickers,
  no black frames), `tools/ocr_haiku.py` for on-screen text, ebur128 loudness.

## 9. Packaging + delivery
- Thumbnail: real frame of the main person, copy the layout of the top rival thumbnail.
- `delivery/title.txt`, `description.txt` (chapters + sources), `tags.txt`.
- `tools/deliver.py`: upload to Drive + fill the tracking sheet (set DRIVE_FOLDER_ID, rclone remote `gdrive`).
- Facebook: re-encode ~6 Mbps, post as a Public reel with the thumbnail as cover, then a sources comment
  (`skills/politics-news-pipeline/references/facebook-distribution.md`; account setup not included in this repo).

## Requirements
macOS, Python 3, ffmpeg (ffmpeg-full for `ass`), yt-dlp, whisper.cpp + `ggml-small.en.bin`, Playwright/Chromium,
an agent runner for `tools/role.sh` (Hermes), API keys via env vars (never committed).
Absolute paths in scripts use `/Volumes/WORK/...` — change to your own location.
