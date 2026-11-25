# WO — trump-oversight-order / graphics pace fix A / 2026-11-23
Run: tools/role.sh builder work-orders/trump-oversight-order-pacea.md

## Why (owner 23/11, watching v2): "transitions go black; the highlight is not finished before the cut so viewers can't
follow; the page scroll is jerky => edit for the viewer, not for the machine."
Measured by tools/fx/gfx_gate.py on the built segs (edit/qc4/gfx_gate_before.txt): 20/26 FAIL — fade-from-dark starts
(up to 32 frames), highlight held 0.07-1.3 s before the cut, page "scrolls" that are 0.1-0.3 s teleports of up to 240 px
per frame with direction reversals, and 0 px motion elsewhere.

## Inputs (on disk)
- cases/trump-oversight-order/edit/seg4/render_a.py (your renderer; timings are hardcoded there), edit/cap/*.png+json,
  audio_full_v4/words.json, edit/shotmap_v4.tsv (rows already RETIMED by the orchestrator; same-page rows merged)
- tools/fx/gfx_gate.py (the gate), edit/seg4/index_A.tsv

## Viewer-pace rules (apply to every row you own)
1. Cut in on a fully visible picture: no fade from black/dark, no dark first frame (gate lead_dark = 0).
2. One camera move per shot, continuous: ease-in-out over >= 0.8 s, sub-pixel position (float crop + resample, never
   int-rounded steps), <= 24 px/frame at 1080p, never reverses direction. A long page travel = start the move earlier
   and make it longer, never faster. If two targets are far apart, cut (hard cut inside the shot) instead of whipping.
3. Highlight sweep starts on the spoken phrase and sweeps at reading pace, but it must be COMPLETE >= 1.5 s before the
   shot ends, and the finished highlight + text stays still on screen for that hold (no zoom-out, no return to the old
   framing, no fade). If the voice is later than that, start the sweep earlier — the reader leads the voice.
4. Text readable on a phone: highlighted line >= 34 px x-height in the frame, no half lines at the frame edge.
5. Encode h264_videotoolbox -q:v 72 -allow_sw 0. Overwrite the same output names: edit/seg4/<seg>_<t0 as in the existing
   index>.mp4 (merged rows keep the first row's name). Update index_A.tsv t1 + phrase for retimed/merged rows and
   DELETE index lines of rows that were merged away.

## DONE-WHEN
- python3 tools/fx/gfx_gate.py <every mp4 you own> -> all PASS (paste the output). Exception allowed only for a deliberate
  hard cut inside MATCHCUT (say so and show the frame).
- proof frames edit/qc4/pace_<file>_{start,hold}.jpg looked at by you.

## Your rows (seg t0-t1 in VO-segment seconds, new timing)
B1 4.54-9.80 KSTAT (already push-and-hold; just retime to 5.26 s and keep), B4 1.80-10.92 DOC, B4 10.92-19.68 DOC, B5 11.84-16.15 WEBHEAD, B5 19.44-22.64 DOC (next row is DOC, cannot extend: finish the sweep by 1.70 s), B5 22.64-27.88 DOC, B10 17.54-20.80 QUOTELIFT, B14 24.86-29.01 HLGT, B16 11.60-17.20 DOC

OUTPUT: cases/trump-oversight-order/edit/seg4/index_A.tsv
