#!/usr/bin/env python3
"""Scene sheets -> Haiku (cheap): 9 unique scenes per 3x3 contact sheet, one model call per sheet (~5x fewer image
tokens than one call per frame). Max 45 scenes per master (evenly spread over unique scenes).
Input research/scenes/<id>.scenes.json (from scan_scenes.py detect+split, dup_of set by dHash).
Output research/scenes/<id>.json {scenes:[{t0,t1,dur,frame,scene,text,watermark,logo,anchor,...}]}; sheets in assets/sheets/.
Run with Hermes venv: ~/.hermes/hermes-agent/venv/bin/python v1/scene_sheets.py [ids...]"""
import json, re, sys, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path.home() / ".hermes/hermes-agent"))
from agent.anthropic_credentials import resolve_anthropic_token  # noqa: E402
from agent.anthropic_adapter import build_anthropic_client, _CLAUDE_CODE_SYSTEM_PREFIX  # noqa: E402

PROJ = Path(__file__).resolve().parent.parent
SC, SH = PROJ / "research/scenes", PROJ / "assets/sheets"
MODEL, CAP, TW, TH, BAR = "claude-haiku-4-5", 45, 426, 240, 28
PROMPT = """This is a 3x3 contact sheet of {n} video scenes from one source clip. Each tile has its number (1-{n}) in the
black bar UNDER it (ignore those bar numbers as content). For EACH tile report:
"text": all burned-in text in the tile (captions, tickers, titles, channel names, signage), ' | ' separated, empty if none;
"watermark": true if any overlay logo/bug/channel handle in a corner (graphic or text);
"logo": short description+corner, empty if none;
"anchor": true if presenter/talking head/studio/interview;
"scene": <=18 words: subject, aircraft type + airline livery if identifiable, place, camera move.
Return ONLY JSON {{"tiles":[{{"n":1,"text":"","watermark":false,"logo":"","anchor":false,"scene":""}}, ...]}}"""


def sheet(frames, out):
    cols, rows = 3, -(-len(frames) // 3)
    img = Image.new("RGB", (cols * TW, rows * (TH + BAR)), "black")
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
    except OSError:
        font = ImageFont.load_default()
    for k, f in enumerate(frames):
        x, y = (k % cols) * TW, (k // cols) * (TH + BAR)
        img.paste(Image.open(PROJ / f).convert("RGB").resize((TW, TH)), (x, y))
        d.text((x + 8, y + TH + 3), str(k + 1), fill="yellow", font=font)
    img.save(out, quality=82)


def main():
    import base64
    client = build_anthropic_client(resolve_anthropic_token(model=MODEL))
    SH.mkdir(parents=True, exist_ok=True)
    ids = sys.argv[1:] or sorted(p.name.replace(".scenes.json", "") for p in SC.glob("*.scenes.json"))
    tok = [0, 0]
    for cid in ids:
        out = SC / f"{cid}.json"
        if out.exists():
            continue
        sc = json.loads((SC / f"{cid}.scenes.json").read_text())
        uniq = [i for i, s in enumerate(sc) if s.get("dup_of") is None]
        if len(uniq) > CAP:
            uniq = [uniq[round(k * (len(uniq) - 1) / (CAP - 1))] for k in range(CAP)]
        for g in range(0, len(uniq), 9):
            grp = uniq[g:g + 9]
            p = SH / f"{cid}_{g // 9:02d}.jpg"
            sheet([sc[i]["frame"] for i in grp], p)
            content = [{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                                    "data": base64.b64encode(p.read_bytes()).decode()}},
                       {"type": "text", "text": PROMPT.format(n=len(grp))}]
            tiles = []
            for a in range(4):
                try:
                    r = client.messages.create(model=MODEL, max_tokens=2500, temperature=0,
                                               system=[{"type": "text", "text": _CLAUDE_CODE_SYSTEM_PREFIX}],
                                               messages=[{"role": "user", "content": content}])
                    txt = "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
                    m = re.search(r"\{.*\}", txt, re.S)
                    tiles = json.loads(m.group(0))["tiles"] if m else []
                    tok[0] += r.usage.input_tokens; tok[1] += r.usage.output_tokens
                    break
                except Exception as e:  # noqa: BLE001
                    print(f"  retry {a + 1} {cid}: {type(e).__name__} {str(e)[:120]}", flush=True)
                    time.sleep(5 * (a + 1))
            by = {t.get("n"): t for t in tiles}
            for k, i in enumerate(grp):
                t = dict(by.get(k + 1, {})); t.pop("n", None)
                sc[i].update(t); sc[i]["sheet"] = str(p.relative_to(PROJ))
        out.write_text(json.dumps({"scenes": sc}, ensure_ascii=False, indent=1))
        print(f"{cid}\t{len(uniq)} scenes\ttokens in/out so far {tok}", flush=True)
    print("DONE", tok)


if __name__ == "__main__":
    main()
