# WO — trump-oversight-order / graphics v4 E: 4 callback rows added by the fix pass / 2026-11-23
Run: tools/role.sh builder work-orders/trump-oversight-order-gfx4e.md

## Inputs (on disk)
- cases/trump-oversight-order/edit/shotmap_v4.tsv (fixed; rows below), audio_full_v4/words.json
- edit/seg4/render_b.py (renders WEBSCROLL / SPLIT / POST / ANNOT — reuse its functions), edit/seg4/index_B.tsv
- edit/cap/*.png + *.json (DOM rects), edit/qc4/*

## Task
Render these 4 rows exactly like their existing siblings (same page, same look), as edit/seg4/<seg>_<t0 centiseconds 5 digits>.mp4,
1920x1080 30 fps, exact duration, h264_videotoolbox -q:v 72 -allow_sw 0:
1. B8 0.00-2.20 POST — @OversightDems post (same render as B8_00220), push in on the card; it must flow into B8_00220
   (end framing of this row ~= start framing of B8_00220). Voice: "They say accountability is coming."
2. B16 30.20-32.94 WEBSCROLL — politico_1121_yahoo.png, scroll to and highlight the sentence about notice giving the Justice
   Department time to mount a legal challenge (marker lands on "Justice Department").
3. B16 32.94-34.70 WEBSCROLL cont. — marker continues to "legal challenge".
4. B18 4.98-8.64 SPLIT — left real EO "consistent with applicable law" line, right 41 USC 4712 "may not be waived" line;
   highlight left then right. Voice: "text itself defers to the law, so Raskin may have a point."
No circles, no typed text, no labels. Proof frames edit/qc4/E_<n>_{a,c}.jpg; look at them yourself.
Append the 4 rows to edit/seg4/index_B.tsv (same columns: seg t0 t1 file template phrase).

## DONE-WHEN
- 4 mp4 of the right duration exist and are listed in index_B.tsv.

OUTPUT: cases/trump-oversight-order/edit/seg4/B18_00498.mp4
