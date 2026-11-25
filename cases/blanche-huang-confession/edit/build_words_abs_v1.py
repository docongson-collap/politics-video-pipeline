#!/usr/bin/env python3
"""Build edit/words_abs_v1.json (WO task 3, blanche-huang-confession v1):
  - VO words (audio_full_v1/words.json) shifted to absolute film time, then realigned per segment to
    script-full-v1.md with difflib: only equal-length replace runs swap in the script's word (keeping
    the ASR timing); everything else (inserts/deletes/unequal-length replaces) keeps the ASR word,
    since there is no ASR timing to attach to a word the script has but the take didn't actually align
    to. This is what fixes ASR misspellings of proper nouns (Nvidia, Huang, Blanche, Megaspeed,
    Mediaite, Pod Force One, subpoena, Raskin, Jeffries, Bonta) -- the script already has the correct
    spelling at the same position.
  - K-clip words (K1..K9) via whisper-cli -ml 1 -sow -oj on the exact clip window (edit_plan_v1.json's
    in/out), then realigned the same way against edit_plan_v1.json's own "words" field for that K id
    (a verified transcript) -- so clip-specific ASR misses come from the clip's own verified transcript,
    not a fresh guess.
  - Quote characters stripped from all word text (captions.py doesn't expect them); exact duplicate
    (w,s,e) entries dropped.
Needs edit/full_shots_v1.tsv to already exist (run edit/full_v1.py first).
"""
import difflib, json, re, subprocess, sys, tempfile
from pathlib import Path

CASE = Path(__file__).resolve().parents[1]
ROOT = CASE.parents[1]
E = CASE / "edit"
AUD = CASE / "audio_full_v1"
FFMPEG = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
WHISPER_BIN = "whisper-cli"
WHISPER_MODEL = ROOT / "kho/whisper-models/ggml-small.en.bin"

sys.path.insert(0, str(E))
from full_v1 import resolve_clip, load_shotmap, beat_order  # reuse src-string parsing, no duplicate logic


def norm(w):
    return re.sub(r"[^a-z0-9']", "", w.lower())


def script_segments():
    text = (CASE / "script-full-v1.md").read_text()
    out = {}
    for seg, body in re.findall(r"\[(B\d+)\] \([^)]*\)\n((?:(?!\n\[).*\n?)*)", text):
        clean = re.sub(r"\{[^}]*\}", "", body)
        out[seg] = clean.split()
    return out


def clip_scripts():
    """edit_plan_v1.json's own "words" field, keyed by K-id -- a verified transcript of the clip, used
    as the realignment target for whisper's output."""
    plan = json.load(open(CASE / "edit_plan_v1.json"))
    return {row["id"]: row["words"].split() for row in plan if row["type"] == "clip"}


def realign(asr_words, script_words):
    """asr_words: [{'w','s','e'}] (segment-relative); script_words: list[str]. Returns new word list,
    same length/order as asr_words (never invents timing for a word the ASR never heard)."""
    a_norm = [norm(w["w"]) for w in asr_words]
    s_norm = [norm(w) for w in script_words]
    sm = difflib.SequenceMatcher(a=a_norm, b=s_norm, autojunk=False)
    out = list(asr_words)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "replace" and (i2 - i1) == (j2 - j1):
            for k in range(i2 - i1):
                out[i1 + k] = {"w": script_words[j1 + k], "s": asr_words[i1 + k]["s"], "e": asr_words[i1 + k]["e"]}
        # equal / unequal-length replace / insert / delete: leave the ASR word+timing as-is
    return out


def beat_starts():
    """seg -> absolute film start time, from edit/full_shots_v1.tsv (written by edit/full_v1.py)."""
    import csv
    starts = {}
    with open(E / "full_shots_v1.tsv") as f:
        rd = csv.DictReader(f, delimiter="\t")
        for r in rd:
            seg = r["seg"]
            if seg not in starts:
                starts[seg] = float(r["t_abs"])
    return starts


def clip_words(seg, p, off, d):
    """whisper-cli -ml 1 -sow -oj on the exact clip window -> segment-relative word list [{'w','s','e'}]."""
    words = []
    with tempfile.TemporaryDirectory() as td:
        wav = Path(td) / "clip.wav"
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-ss", f"{off:.3f}", "-t", f"{d:.3f}",
                        "-i", str(p), "-ar", "16000", "-ac", "1", str(wav)], check=True)
        res = subprocess.run([WHISPER_BIN, "-m", str(WHISPER_MODEL), "-f", str(wav), "-ml", "1",
                              "-sow", "-oj", "-of", str(Path(td) / "clip")],
                             capture_output=True, text=True)
        jpath = Path(td) / "clip.json"
        if not jpath.exists():
            print(f"WARN: whisper-cli produced no json for {seg} ({res.stderr[:200]})", file=sys.stderr)
            return words
        wj = json.load(open(jpath))

        def walk(o):
            if isinstance(o, dict):
                if "text" in o and "offsets" in o and isinstance(o["offsets"], dict):
                    yield o
                for v in o.values():
                    yield from walk(v)
            elif isinstance(o, list):
                for v in o:
                    yield from walk(v)

        for ent in walk(wj):
            w = ent["text"].strip()
            if not w:
                continue
            s = ent["offsets"]["from"] / 1000.0
            e = ent["offsets"]["to"] / 1000.0
            words.append({"w": w, "s": s, "e": e})
    return words


def main():
    starts = beat_starts()
    vo_words = json.load(open(AUD / "words.json"))
    scripts = script_segments()
    clip_txt = clip_scripts()
    shotmap_rows = load_shotmap()
    order = beat_order(shotmap_rows)
    k_rows = {r["seg"]: r for r in shotmap_rows if r["treat"] == "CLIP"}
    bounds = {s: starts[order[i + 1]] if i + 1 < len(order) else None for i, s in enumerate(order)}

    out = []
    overrun = 0
    for seg in order:
        beat0 = starts.get(seg)
        if beat0 is None:
            sys.exit(f"{seg}: no beat_start in full_shots_v1.tsv (run edit/full_v1.py first)")
        bound = bounds[seg]  # absolute start of the next beat (whisper/ASR can bleed a few ms past the
        # exact clip/beat window -- drop any word whose absolute start would land in the next beat).
        if seg.startswith("K"):
            r = k_rows[seg]
            p, off, d = resolve_clip(r["src"])
            asr = clip_words(seg, p, off, d)
            realigned = realign(asr, clip_txt.get(seg, []))
            for w in realigned:
                abss = round(beat0 + w["s"], 3); abse = round(beat0 + w["e"], 3)
                if bound is not None and abss >= bound - 0.01:
                    overrun += 1; continue
                out.append({"w": w["w"], "s": abss, "e": abse})
        else:
            asr = vo_words.get(seg, [])
            realigned = realign(asr, scripts.get(seg, []))
            for w in realigned:
                abss = round(beat0 + w["s"], 3); abse = round(beat0 + w["e"], 3)
                if bound is not None and abss >= bound - 0.01:
                    overrun += 1; continue
                out.append({"w": w["w"], "s": abss, "e": abse})

    # strip quote chars (several documents quoted verbatim in VO; captions.py doesn't expect them)
    for w in out:
        w["w"] = w["w"].replace('"', "").replace("\u201c", "").replace("\u201d", "").strip()
    out = [w for w in out if w["w"]]

    # drop exact duplicate consecutive entries
    deduped = []
    for w in out:
        if deduped and deduped[-1] == w:
            continue
        deduped.append(w)

    json.dump(deduped, open(E / "words_abs_v1.json", "w"), indent=0)
    print(f"{len(deduped)} words -> {E / 'words_abs_v1.json'} "
          f"(dropped {len(out) - len(deduped)} duplicates, {overrun} beat-overrun ASR words)")


if __name__ == "__main__":
    main()
