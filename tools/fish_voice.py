#!/usr/bin/env python3
"""Voice for a hook script: cases/<case>/script-hook-vN.md (## SCRIPT, [Bn] blocks) -> cases/<case>/audio_hook_vN/Bn.wav
Fish s2.1-pro-free, same voice/params as Aviation v2_pipeline.fish_tts (copied, not imported). Resumable: existing wavs skipped.
Usage: python3 tools/fish_voice.py cases/dominos/script-hook-v1.md
"""
import json, os, re, sys, time, urllib.error, urllib.request
from pathlib import Path

FISH_URL = "https://api.fish.audio/v1/tts"
FISH_MODEL = "s2.1-pro-free"
FISH_VOICE_ID = "e3cd384158934cc9a01029cd7d278634"


def fish_key():
    k = os.environ.get("FISH_API_KEY")
    fp = Path("~/.config/son/fish.env").expanduser()
    if not k and fp.exists():
        for ln in fp.read_text().splitlines():
            if ln.startswith("FISH_API_KEY="):
                k = ln.split("=", 1)[1].split("#")[0].strip()
    if not k:
        sys.exit("FISH_API_KEY not set (env or ~/.config/son/fish.env)")
    return k


def fish_tts(key, text, out):
    body = json.dumps({"text": text, "format": "wav", "sample_rate": 24000, "latency": "normal", "normalize": True,
                       "temperature": 0.6, "top_p": 0.7, "chunk_length": 300, "reference_id": FISH_VOICE_ID}).encode()
    last = None
    for attempt in range(4):
        req = urllib.request.Request(FISH_URL, data=body, method="POST", headers={
            "Authorization": f"Bearer {key}", "Content-Type": "application/json", "model": FISH_MODEL})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                audio = r.read()
            break
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read()[:200]!r}"
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(10 * (attempt + 1)); continue
            sys.exit(f"Fish error: {last}")
    else:
        sys.exit(f"Fish error after retries: {last}")
    if audio[:4] != b"RIFF":
        sys.exit(f"Fish returned non-wav ({audio[:60]!r})")
    out.write_bytes(audio)


def beats(script):
    t = Path(script).read_text(encoding="utf-8").split("## SCRIPT", 1)[1].split("\n## ", 1)[0]
    out = []
    for m in re.finditer(r"^\[(B\d+)\]([^\n]*)\n(.*?)(?=^\[B\d+\]|\Z)", t, re.S | re.M):
        head = m.group(2).strip()
        # text on the tag line is spoken, except labels: "(B3)" origin tags and CHAPTER titles (v4 voiced "(B1)", 2026-11-24)
        silent = not head or head.upper().startswith("CHAPTER") or re.fullmatch(r"\([^)]*\)", head)
        body = m.group(3) if silent else head + "\n" + m.group(3)
        body = re.sub(r"<!--.*?-->", "", body, flags=re.S)          # comments (clip markers) are never spoken
        txt = re.sub(r"\{(?:[A-Z]\d+|CLIP|K\d+)[^}]*\}", "", body)
        out.append((m.group(1), re.sub(r"\s+", " ", txt).strip()))
    return out


def main():
    script = Path(sys.argv[1]).resolve()
    m = re.search(r"script-(\w+)-v(\d+)\.md$", script.name)
    kind, ver = (m.group(1), m.group(2)) if m else ("hook", re.search(r"-v(\d+)\.md$", script.name).group(1))
    od = script.parent / f"audio_{kind}_v{ver}"; od.mkdir(exist_ok=True)
    key = fish_key()
    for b, txt in beats(script):
        (od / f"{b}.txt").write_text(txt + "\n")
        wav = od / f"{b}.wav"
        if not txt:  # chapter-title-only beat: nothing spoken
            continue
        if wav.exists() and wav.stat().st_size > 1000:
            continue
        fish_tts(key, txt, wav)
        print("wrote", wav.name, len(txt.split()), "words")


if __name__ == "__main__":
    main()
