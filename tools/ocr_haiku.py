#!/usr/bin/env python3
"""Frame OCR + watermark + scene description via Claude Haiku, using the SAME Anthropic credential Hermes runs on
(no OmniRoute, no separate `claude` CLI login). Replaces ocr_gemini.py when Gemini is down (owner 06/11).
Run with the Hermes venv:  ~/.hermes/hermes-agent/venv/bin/python tools/ocr_haiku.py IMG [IMG ...] --out res.json
Options: --batch N (frames per request, default 8), --model (default claude-haiku-4-5).
Output JSON: {"frames":[{"file","text","caption","watermark","logo","scene_text","scene"}]}. Token is never printed."""
import argparse, base64, json, os, re, sys, time
from pathlib import Path

HERMES = Path.home() / ".hermes/hermes-agent"
sys.path.insert(0, str(HERMES))
from agent.anthropic_credentials import resolve_anthropic_token  # noqa: E402
from agent.anthropic_adapter import build_anthropic_client, _CLAUDE_CODE_SYSTEM_PREFIX  # noqa: E402

PROMPT = """You are an OCR + watermark + shot-description engine for video QC. For EACH of the {n} images (ids {ids}):
(1) read ALL visible text burned into the picture (captions, tickers, titles, channel names, signage);
(2) check all 4 corners/edges for ANY overlay logo/bug/watermark, INCLUDING purely graphic icons with no text;
(3) describe the shot in <=20 words: subject, aircraft type/airline livery if identifiable, location, camera (e.g.
"Aer Lingus A320 taking off, side view, Dublin, sunrise"; "news anchor in studio"; "map graphic").
Return ONLY JSON: {{"frames":[{{"id":<id>,"text":"<all text ' | ' separated, empty if none>",
"caption":<true if overlay caption/subtitle/ticker added in editing>,"watermark":<true if any overlay logo/bug/handle>,
"logo":"<description + position, empty if none>","scene_text":<true if text physically in scene>,
"scene":"<shot description>","anchor":<true if talking head/studio/presenter>}}]}}"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("images", nargs="+")
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--model", default="claude-haiku-4-5")
    ap.add_argument("--out")
    a = ap.parse_args()
    token = resolve_anthropic_token(model=a.model)
    if not token:
        sys.exit("no Anthropic credential resolved")
    client = build_anthropic_client(token)
    res, t0, usage = [], time.time(), [0, 0]
    for s in range(0, len(a.images), a.batch):
        chunk = a.images[s:s + a.batch]
        ids = list(range(len(chunk)))
        content = [{"type": "text", "text": PROMPT.format(n=len(chunk), ids=ids)}]
        for i, p in zip(ids, chunk):
            mt = "image/png" if p.endswith(".png") else "image/jpeg"
            content += [{"type": "text", "text": f"image id={i}"},
                        {"type": "image", "source": {"type": "base64", "media_type": mt,
                                                     "data": base64.b64encode(Path(p).read_bytes()).decode()}}]
        for attempt in range(4):
            try:
                r = client.messages.create(model=a.model, max_tokens=4000, temperature=0,
                                           system=[{"type": "text", "text": _CLAUDE_CODE_SYSTEM_PREFIX}],
                                           messages=[{"role": "user", "content": content}])
                txt = "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
                frames = json.loads(re.search(r"\{.*\}", txt, re.S).group(0))["frames"]
                usage[0] += r.usage.input_tokens; usage[1] += r.usage.output_tokens
                break
            except Exception as e:  # noqa: BLE001
                print(f"  retry {attempt + 1}: {type(e).__name__}: {str(e)[:160]}", file=sys.stderr)
                time.sleep(5 * (attempt + 1))
        else:
            frames = []
        by = {f.get("id"): f for f in frames}
        for i, p in zip(ids, chunk):
            f = dict(by.get(i, {"text": "?", "scene": "?"})); f.pop("id", None); f["file"] = p
            res.append(f)
            print(f"{Path(p).name}\t{'WM' if f.get('watermark') else '-'}\t{f.get('scene', '')}\t[{f.get('text', '')}]")
    print(f"# {len(res)} frames, {time.time() - t0:.1f}s, model={a.model}, tokens in/out={usage}")
    if a.out:
        Path(a.out).write_text(json.dumps({"frames": res}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
