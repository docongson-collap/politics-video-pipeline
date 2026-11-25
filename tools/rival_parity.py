#!/usr/bin/env python3
"""Rival parity gate: does our script follow the rival's transcript closely enough?

Usage:
  tools/rival_parity.py --ours a350f/full.txt --rival a350f/research/ref/3stjU_vtQr0.txt
  tools/rival_parity.py --rival-facts <rival.txt>   # list the rival's concrete facts (for the researcher WO)

Checks (FAIL = exit 1):
  1. sentence length: our avg words/sentence <= rival avg * 1.25
  2. short sentences: our share of sentences <= 6 words >= rival share * 0.6
  3. rival entities: names/models/companies the rival says >= 2 times;
     we must cover >= 70% of them (each missing one is listed)
  4. stat repetition: no single percent/number phrase spoken more than 2 times
Lesson: docs/LESSONS.md 2026-10-16 (a350f v6 copied the beats but not the content).
"""
import argparse, re, sys
from collections import Counter

STOP = set("""The A An And But So Or If In On At Of To For By With From As It Its It's
That This These Those There Their They Them He She His Her We Our You Your I I'm Me My
What Which Who Why How When Where Then Than Now Just Not No Yes Also Even Still Back
Because Well Okay Right Look Here And Today Today's Mr Mrs Some Most More Much Many One Two
Three Four Five Six Seven Eight Nine Ten First Second Third Next Last Every Each All Both Any
Is Was Were Are Be Been Being Do Does Did Has Have Had Will Would Can Could Should Might May Must
Let Wait Basically Actually Really Okay Oh Like Yeah""".split())
MONTHS = set("January February March April May June July August September October November December".split())


def load(path):
    t = open(path, encoding="utf-8").read()
    if path.endswith(".md") and "## SCRIPT" in t:  # writer script file: spoken section only
        t = t.split("## SCRIPT", 1)[1].split("\n## ", 1)[0]
        t = re.sub(r"^\[B\d+\]\s*CHAPTER[^\n]*$", "", t, flags=re.M)  # drop chapter headers only; beat text may share the tag line
    t = re.sub(r"\{[A-Z]\d+[^}]*\}", "", t)
    t = re.sub(r"^\[B\d+\]\s*", "", t, flags=re.M)
    t = re.sub(r"\[\d+:\d+(?::\d+)?\]", " ", t)  # transcript timestamps
    t = re.sub(r">>|\[music\]", " ", t, flags=re.I)
    return re.sub(r"\s+", " ", t).strip()


def sentences(t):
    return [s for s in re.split(r"(?<=[.!?])\s+", t) if len(s.split()) > 0]


def norm_ent(e):
    e = e.lower().replace("-", "").replace(" ", "")
    return {"mcdonnelldouglas": "mcdonnelldouglas", "macdonalddouglas": "mcdonnelldouglas",
            "unitedparcelservice": "ups", "unitedparcel": "ups"}.get(e, e)


def entities(t):
    """Proper nouns / model designators (MD11, A300, 777F, FedEx, Fred Smith, Atlas)."""
    out = Counter()
    for m in re.finditer(r"\b(?:[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?|[A-Z]{1,3}-?\d{2,4}[A-Z]?|\d{3}-?\d?[A-Z]{1,2}|\d{3}X)\b", t):
        w = m.group(0)
        first = w.split()[0]
        if first in STOP or first in MONTHS or w in STOP:
            if " " in w and w.split()[1] not in STOP:
                w = w.split()[1]
            else:
                continue
        out[norm_ent(w)] += 1
    return out


def stats(t):
    s = sentences(t)
    lens = [len(x.split()) for x in s]
    return {"words": sum(lens), "sent": len(s), "avg": sum(lens) / max(1, len(s)),
            "short": sum(1 for l in lens if l <= 6) / max(1, len(s))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ours")
    ap.add_argument("--rival", action="append", default=[])
    ap.add_argument("--rival-facts")
    ap.add_argument("--min-cover", type=float, default=0.70)
    ap.add_argument("--ignore", action="append", default=[], help="rival entity to skip (sponsor names)")
    a = ap.parse_args()

    if a.rival_facts:
        t = load(a.rival_facts)
        for e, n in entities(t).most_common():
            if n >= 2:
                print(f"{n:3d}  {e}")
        nums = Counter(re.findall(r"\b\d[\d,.]*\s?(?:%|percent|tons?|tonnes|units|orders|airplanes|freighters)?", t))
        print("numbers:", ", ".join(k for k, _ in nums.most_common(40)))
        return 0

    if not a.ours or not a.rival:
        ap.error("--ours and --rival required")
    ours = load(a.ours)
    rival = " ".join(load(r) for r in a.rival)
    so, sr = stats(ours), stats(rival)
    fail = []

    print(f"ours : {so['words']} words, {so['sent']} sentences, avg {so['avg']:.1f} w/s, short {so['short']:.0%}")
    print(f"rival: {sr['words']} words, {sr['sent']} sentences, avg {sr['avg']:.1f} w/s, short {sr['short']:.0%}")
    if so["avg"] > sr["avg"] * 1.25:
        fail.append(f"sentences too long: {so['avg']:.1f} > {sr['avg'] * 1.25:.1f} (rival x1.25)")
    if so["short"] < sr["short"] * 0.6:
        fail.append(f"too few short punch sentences: {so['short']:.0%} < {sr['short'] * 0.6:.0%}")

    eo, er = entities(ours), entities(rival)
    ign = {norm_ent(x) for x in a.ignore} | {"cargo", "pro"}
    key = [e for e, n in er.items() if n >= 2 and e not in ign]
    have = lambda e: any(o == e or o.startswith(e) or e.startswith(o) for o in eo if len(o) >= 3)
    missing = sorted((e for e in key if not have(e)), key=lambda e: -er[e])
    cover = 1 - len(missing) / max(1, len(key))
    print(f"rival entities (said >=2x): {len(key)}, covered {cover:.0%}")
    if missing:
        print("  missing: " + ", ".join(f"{e}({er[e]}x)" for e in missing))
    if cover < a.min_cover:
        fail.append(f"rival entity coverage {cover:.0%} < {a.min_cover:.0%}")

    nw = r"(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|point|and|a)(?:-[a-z]+)?"
    # whole spoken number ("five point five percent"), not its last word — else 5.5% and 2.5% both count as "five percent"
    stat_re = rf"\b\d[\d,.]*\s(?:percent)\b|\b\d[\d,.]*%|\b(?:{nw}\s)*{nw}\spercent\b"
    rep = [(k, n) for k, n in Counter(m.lower() for m in re.findall(stat_re, ours)).items() if n > 2]
    if rep:
        fail.append("same stat spoken >2x: " + ", ".join(f"'{k}' {n}x" for k, n in rep))

    for f in fail:
        print("FAIL", f)
    print("RIVAL PARITY:", "FAIL" if fail else "PASS")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
