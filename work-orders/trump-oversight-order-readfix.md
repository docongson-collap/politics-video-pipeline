# WO — trump-oversight-order / graphics readability fix / 2026-11-23
Run: tools/role.sh builder work-orders/trump-oversight-order-readfix.md

## Why
Orchestrator checked the finished v2 frame 0.4 s before each graphic cut (edit/qc4/holds.jpg). Pace now passes, but the
highlighted text is too small to read on a phone in: B5 11.84 WEBHEAD (AP "a universe of tens of thousands of businesses"
is ~15 px x-height, top-left of a mostly empty white frame), B7 0.00 POST and B8 0.00 POST (Oversight Dems statement card:
body text is tiny; nothing readable), B14 0.00 / B14 12.03 / B16 30.20 WEBSCROLL (Politico body text ~18 px).

## Task
Re-render only those 6 rows (renderers edit/seg4/render_a.py, render_b.py; same file names, same durations as now in
index_A/index_B). Keep the pace rules that already pass (no dark lead, one smooth move, highlight finished >= 1.5 s
before the end and held still). Change: end framing is a push-in so the highlighted line has >= 40 px x-height at
1080p and fills >= 60% of frame width, centred vertically in the upper 2/3 of the frame (captions sit at the bottom
third — keep the highlighted line above y = 700). For the POST card, push in on the sentence that the voice is reading
and highlight it. Zoom by resampling the native-resolution capture (crop window shrink), sub-pixel, eased.

## DONE-WHEN
- python3 tools/fx/gfx_gate.py on the 6 files -> all PASS (paste); edit/qc4/read_<file>_hold.jpg shows the
  highlighted line readable at 25% scale (look at it yourself).

OUTPUT: cases/trump-oversight-order/edit/seg4/B5_01184.mp4
