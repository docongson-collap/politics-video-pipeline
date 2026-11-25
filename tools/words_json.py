#!/usr/bin/env python3
"""Word timings for a voiced audio dir: whisper-cli per B*.wav -> <dir>/words.json {Bn:[{w,s,e}], Bn_dur}.
Usage: python3 tools/words_json.py cases/<case>/audio_full_vN"""
import json, subprocess, sys, wave
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODEL = ROOT / "kho/whisper-models/ggml-small.en.bin"


def main():
    d = Path(sys.argv[1]).resolve()
    out = {}
    for wav in sorted(d.glob("B*.wav"), key=lambda p: int(p.stem[1:])):
        b = wav.stem
        w16 = d / f".{b}.16k.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(wav), "-ar", "16000", "-ac", "1", str(w16)], check=True)
        subprocess.run(["whisper-cli", "-m", str(MODEL), "-f", str(w16), "-ml", "1", "-sow", "-oj", "-of", str(d / f".{b}")],
                       check=True, capture_output=True)
        js = json.loads((d / f".{b}.json").read_text())
        words = []
        for seg in js["transcription"]:
            w = seg["text"].strip()
            if not w:
                continue
            s, e = seg["offsets"]["from"] / 1000, seg["offsets"]["to"] / 1000
            words.append({"w": w, "s": round(s, 2), "e": round(e, 2)})
        # Fish wavs carry a streaming header (nframes = 0xFFFFFFFF -> 89478 s); measure with ffprobe instead (2026-11-24)
        dur = subprocess.run(["ffprobe", "-v", "0", "-show_entries", "format=duration", "-of", "csv=p=0", str(wav)],
                             capture_output=True, text=True).stdout.strip()
        out[f"{b}_dur"] = round(float(dur), 3)
        out[b] = words
        w16.unlink()
    (d / "words.json").write_text(json.dumps(out, indent=0))
    print(d / "words.json", sum(len(v) for k, v in out.items() if not k.endswith("_dur")), "words")


if __name__ == "__main__":
    main()
