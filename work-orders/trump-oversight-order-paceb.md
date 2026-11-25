# WO — trump-oversight-order / graphics pace fix B / 2026-11-23
Run: tools/role.sh builder work-orders/trump-oversight-order-paceb.md

## Why (owner 23/11, watching v2): "transitions go black; the highlight is not finished before the cut so viewers can't
follow; the page scroll is jerky => edit for the viewer, not for the machine."
Measured by tools/fx/gfx_gate.py on the built segs (edit/qc4/gfx_gate_before.txt): 20/26 FAIL — fade-from-dark starts
(up to 32 frames), highlight held 0.07-1.3 s before the cut, page "scrolls" that are 0.1-0.3 s teleports of up to 240 px
per frame with direction reversals, and 0 px motion elsewhere.

## Inputs (on disk)
- cases/trump-oversight-order/edit/seg4/render_b.py (your renderer; timings are hardcoded there), edit/cap/*.png+json,
  audio_full_v4/words.json, edit/shotmap_v4.tsv (rows already RETIMED by the orchestrator; same-page rows merged)
- tools/fx/gfx_gate.py (the gate), edit/seg4/index_B.tsv

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
   index>.mp4 (merged rows keep the first row's name). Update index_B.tsv t1 + phrase for retimed/merged rows and
   DELETE index lines of rows that were merged away.

## DONE-WHEN
- python3 tools/fx/gfx_gate.py <every mp4 you own> -> all PASS (paste the output). Exception allowed only for a deliberate
  hard cut inside MATCHCUT (say so and show the frame).
- proof frames edit/qc4/pace_<file>_{start,hold}.jpg looked at by you.

## Your rows (seg t0-t1 in VO-segment seconds, new timing)
B7 0.00-4.22 POST (next is a clip: finish by 2.72 s), B8 0.00-8.84 POST (merged: one continuous push on the post, then highlight, then hold), B14 0.00-4.37 WEBSCROLL, B14 12.03-19.84 WEBSCROLL (merged: one slow scroll then sweep then hold), B15 2.76-10.57 SPLIT, B15 10.57-18.81 SPLIT, B15 23.65-29.09 SPLIT, B16 30.20-35.70 WEBSCROLL (merged), B18 4.98-9.04 SPLIT

OUTPUT: cases/trump-oversight-order/edit/seg4/index_B.tsv
