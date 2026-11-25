#!/usr/bin/env python3
"""ASR check of TTS beats: whisper-cli each <dir>/Bn.wav, compare with <dir>/Bn.txt, report beats whose word error rate
or missing content words exceed a threshold. Prints a summary only; full report -> <dir>/asr_report.json.
Usage: python3 tools/asr_check.py cases/<case>/audio_full_v1 [--wer 0.08]"""
import argparse, json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODEL = ROOT / "kho/whisper-models/ggml-small.en.bin"


NUMW = set("""zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen
eighteen nineteen twenty thirty forty fifty sixty seventy eighty ninety hundred thousand million billion trillion point percent
dollars dollar first second third fourth fifth sixth seventh eighth ninth tenth eleventh twelfth thirteenth fourteenth fifteenth
sixteenth seventeenth eighteenth nineteenth twentieth thirtieth oh and a of to""".split())


def words(t, asr=False):
    # Whisper writes numbers as digits ("$12.9 billion", "1994", "U.S."); the script spells them. Compare NON-number words
    # only (number words dropped from the script side, digit tokens dropped from the ASR side). 2026-11-06.
    t = t.lower().replace("-", " ").replace("u.s.", "u s").replace("w.t.o.", "w t o")
    t = re.sub(r"[$€£]?\d[\d,.]*%?(bn|m|s|th|st|nd|rd)?", " ", t)
    return [w for w in re.findall(r"[a-z']+", t) if w not in NUMW and w not in ("billion", "million", "percent")]


def wer(ref, hyp):
    d = list(range(len(hyp) + 1))
    for i, r in enumerate(ref, 1):
        prev, d[0] = d[0], i
        for j, h in enumerate(hyp, 1):
            cur = min(d[j] + 1, d[j - 1] + 1, prev + (r != h))
            prev, d[j] = d[j], cur
    return d[len(hyp)] / max(1, len(ref))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--wer", type=float, default=0.08)
    ap.add_argument("--from-report", action="store_true", help="re-score asr_report.json without re-running whisper")
    a = ap.parse_args()
    d = Path(a.dir)
    beats = sorted(d.glob("B*.wav"), key=lambda p: int(re.sub(r"\D", "", p.stem)))
    rep, bad = [], []
    old = {r["beat"]: r for r in json.loads((d / "asr_report.json").read_text())} if a.from_report else {}
    for w in beats:
        if a.from_report:
            o = old[w.stem]; ref, hyp = words((d / f"{w.stem}.txt").read_text()), words(o["asr"])
            e = wer(ref, hyp); miss = sorted(set(x for x in ref if len(x) > 3) - set(hyp))
            r = dict(o, wer=round(e, 3), missing=miss); rep.append(r)
            if e > a.wer or len(miss) > 2:
                bad.append(r)
            continue
        ref = words((d / f"{w.stem}.txt").read_text())
        with tempfile.TemporaryDirectory() as td:
            wav16 = Path(td) / "a.wav"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(w), "-ar", "16000", "-ac", "1", str(wav16)], check=True)
            subprocess.run(["whisper-cli", "-m", str(MODEL), "-f", str(wav16), "-otxt", "-of", str(Path(td) / "o"), "-np"],
                           capture_output=True)
            hyp_txt = (Path(td) / "o.txt").read_text() if (Path(td) / "o.txt").exists() else ""
        hyp = words(hyp_txt)
        e = wer(ref, hyp)
        miss = sorted(set(x for x in ref if len(x) > 3) - set(hyp))
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(w)],
                                   capture_output=True, text=True).stdout or 0)
        r = {"beat": w.stem, "wer": round(e, 3), "missing": miss, "dur": round(dur, 2), "words": len(ref), "asr": hyp_txt.strip()}
        rep.append(r)
        if e > a.wer or len(miss) > 2:
            bad.append(r)
    (d / "asr_report.json").write_text(json.dumps(rep, indent=1))
    tot = sum(r["dur"] for r in rep)
    print(f"# {len(rep)} beats, {tot/60:.1f} min, {sum(r['words'] for r in rep)} words, flagged {len(bad)} (wer>{a.wer} or >2 missing words)")
    for r in bad:
        print(f"{r['beat']}\twer={r['wer']}\tmissing={r['missing'][:8]}")


if __name__ == "__main__":
    main()
