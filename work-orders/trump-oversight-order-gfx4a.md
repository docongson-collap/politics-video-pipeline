# WO — trump-oversight-order / graphics v4 A: DOC + HLGT + KSTAT + QUOTELIFT + WEBHEAD / 2026-11-23
Run: tools/role.sh builder work-orders/trump-oversight-order-gfx4a.md

## Inputs (on disk)
- cases/trump-oversight-order/edit/shotmap_v4.tsv (approved; find your rows by the treatment column = template name; the
  TEMPLATE LEDGER at lines ~209-223 describes each template), audio_full_v4/words.json, edit_plan_v4.json
- edit/cap/*.png + *.json (real page captures at DPR 2 with DOM rects of phrases) — re-capture with browser only if a needed
  phrase rect is missing (open your own tab, close it after; never touch owner's tabs)
- tools/fx/{capture_pass,doc_pass,num_pass,post_pass,press_pass}.py (all encode on GPU: h264_videotoolbox), kho/envato_templates/*
- ../Aviation/docs/AVIATION_VISUAL_LANGUAGE.md (motion grammar per template type; Precision annotation + Geometry rules)

## Rules
- Output each row as edit/seg4/<seg>_<row t0 in centiseconds>.mp4, 1920x1080 30 fps, duration = row t1-t0 exactly.
- Encode h264_videotoolbox -q:v 72 -allow_sw 0 (never libx264). Python+PIL+ffmpeg frame rendering is fine; keep it simple
  and correct rather than fancy. Highlights at original resolution from DOM rects, one strip per real line, land on the
  spoken word ±0.3 s (words.json; segment Bn times are relative to that VO segment).
- No typed text except inside real evidence. No circles/rings/arrows. No lower thirds/labels.
- Proof frames start/action/end -> edit/qc4/<template>_{a,b,c}.jpg; look at them yourself (readable on a phone, marker
  on the right words, no half lines at frame edges).
- Append one line per rendered row to edit/seg4/index_<WO-letter>.tsv: seg | t0 | t1 | file | template | phrase.

## Task
Render every shot-map v4 row of: DOC (EO page sequence: one continuous push, marker sweeps exact lines), HLGT (cornell 4712 highlight), KSTAT (100,000 lifted out of the GMA/ABC page), QUOTELIFT (abc.png phrase lift), WEBHEAD (AP headline/identity push).

## DONE-WHEN
- edit/seg4/index_A.tsv lists every row of these templates with an existing mp4 of the right duration; proof frames exist.

OUTPUT: cases/trump-oversight-order/edit/seg4/index_A.tsv

## RESUME (previous run was killed by the orchestrator, not by you)
- edit/seg4 already holds some finished mp4s + edit/qc4 proof frames + edit/seg4/render_b.py. Check each of YOUR rows: keep a
  file whose duration matches and whose proof frames look right; render only the missing ones; then write index_<letter>.tsv.
