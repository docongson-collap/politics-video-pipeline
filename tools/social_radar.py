#!/usr/bin/env python3
"""News radar (scout, no login, no vidIQ): rival YouTube RSS -> live VPH, + Truth Social (trumpstruth.org),
Bluesky watchlist, Memeorandum headlines. Plan: docs/NEWS_RADAR_PLAN.md.
usage: python3 tools/social_radar.py [--hours 30]  -> docs/research/radar/<stamp>.json + control/RADAR.md
VPH = views / hours since publish (RSS views lag YouTube by minutes; cross-check the top pick live when possible)."""
import argparse, datetime as dt, json, re, subprocess, sys, time, html
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/research/radar"; OUT.mkdir(parents=True, exist_ok=True)
IDS = OUT / "channel_ids.json"
UA = ["-A", "Mozilla/5.0 (Macintosh) ProofPoliticsRadar/0.2", "-H", "Accept-Language: en"]
# same-stance rivals (docs/COMPETITORS.md A+B) + neutral demand signals
RIVALS = ["briantylercohen", "MeidasTouch", "thedavidpakmanshow", "adammockler", "bulwarkmedia", "TheDamageReport",
          "LegalAFMTN", "FarronBalanced", "katiephangnews", "RobertGouveiaEsq", "DaveAronbergOfficial", "ponderingpolitics",
          "LetsTalkElections", "theamericanledger-w4k", "TheRulingRoomUS", "WashingtonReceipts", "Legal-Fallout",
          "TheOversightDesk", "ForbesBreakingNews", "thehillnews", "MSNBC", "CNN"]
# Stance gate (docs/CHANNEL.md: pro-Democratic, anti-Trump/MAGA, pro-rule-of-law). Demand only counts from same-stance rivals;
# neutral networks (CNN, Forbes, The Hill, MSNBC) are a heat signal, not a pass. A story must have a Trump/MAGA antagonist.
NEUTRAL = {"ForbesBreakingNews", "thehillnews", "MSNBC", "CNN"}
ANTAGONIST = re.compile(r"\b(trump|maga|vance|hegseth|bondi|patel|noem|rubio|lutnick|musk|gop|republican|speaker johnson|"
                        r"stephen miller|kash|rfk|doj|white house)\b", re.I)
BSKY = ["markhamillofficial.bsky.social", "aoc.bsky.social", "gavinnewsom.bsky.social", "jasmine-crockett.bsky.social",
        "chrismurphyct.bsky.social", "repjasmine.bsky.social", "stephenking.bsky.social", "meidastouch.com",
        "jbpritzker.bsky.social", "hakeemjeffries.bsky.social", "adamschiff.bsky.social", "repjamieraskin.bsky.social"]


def get(u, t=25):
    return subprocess.run(["curl", "-sL", "-m", str(t), *UA, u], capture_output=True, text=True).stdout


def channel_ids():
    ids = json.loads(IDS.read_text()) if IDS.exists() else {}
    for h in RIVALS:
        if h not in ids:
            m = re.search(r'"externalId":"(UC[\w-]+)"', get(f"https://www.youtube.com/@{h}"))
            if m:
                ids[h] = m.group(1)
            time.sleep(0.5)
    IDS.write_text(json.dumps(ids, indent=1))
    return ids


def rival_videos(hours):
    now = dt.datetime.now(dt.timezone.utc); rows = []
    for h, cid in channel_ids().items():
        x = get(f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}")
        name = re.search(r"<title>(.*?)</title>", x)
        for vid, t, p, v in re.findall(r"<entry>.*?<yt:videoId>(.*?)</yt:videoId>.*?<title>(.*?)</title>.*?"
                                       r"<published>(.*?)</published>.*?<media:statistics views=\"(\d+)\"", x, re.S):
            age = (now - dt.datetime.fromisoformat(p)).total_seconds() / 3600
            if age <= hours and "/shorts/" not in x.split(vid)[0][-300:]:
                rows.append({"ch": html.unescape(name.group(1)) if name else h, "handle": h, "id": vid,
                             "stance": "N" if h in NEUTRAL else "D",
                             "fit": bool(ANTAGONIST.search(html.unescape(t))),
                             "title": html.unescape(t), "age_h": round(age, 1), "views": int(v),
                             "vph": int(int(v) / max(age, 0.5))})
    return sorted(rows, key=lambda r: -r["vph"])


def truth(hours):
    now = dt.datetime.now(dt.timezone.utc); out = []
    x = get("https://trumpstruth.org/feed")
    for t, link, d in re.findall(r"<item>.*?<title>(.*?)</title>.*?<link>(.*?)</link>.*?<pubDate>(.*?)</pubDate>", x, re.S):
        when = dt.datetime.strptime(d.strip(), "%a, %d %b %Y %H:%M:%S %z")
        if (now - when).total_seconds() / 3600 <= hours:
            t = html.unescape(re.sub(r"<!\[CDATA\[|\]\]>", "", t)).strip()
            out.append({"who": "Trump (Truth Social)", "when": when.isoformat()[:16], "text": t[:600], "url": link})
    return out


def bsky(hours):
    now = dt.datetime.now(dt.timezone.utc); out = []
    for h in BSKY:
        try:
            j = json.loads(get(f"https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed?actor={h}&limit=8&filter=posts_no_replies"))
        except Exception:
            continue
        for it in j.get("feed", []):
            p = it["post"]; rec = p["record"]
            when = dt.datetime.fromisoformat(rec["createdAt"].replace("Z", "+00:00"))
            age = (now - when).total_seconds() / 3600
            if age <= hours:
                rkey = p["uri"].rsplit("/", 1)[-1]
                out.append({"who": h, "when": when.isoformat()[:16], "likes": p.get("likeCount", 0),
                            "likes_per_h": int(p.get("likeCount", 0) / max(age, 0.5)), "text": rec.get("text", "")[:400],
                            "url": f"https://bsky.app/profile/{h}/post/{rkey}"})
    return sorted(out, key=lambda r: -r["likes_per_h"])


def memeorandum():
    x = get("https://www.memeorandum.com/feed.xml")
    return [html.unescape(re.sub("<.*?>", "", t)) for t in re.findall(r"<item>.*?<title>(.*?)</title>", x, re.S)][:25]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--hours", type=float, default=30); a = ap.parse_args()
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M")
    data = {"stamp": stamp, "videos": rival_videos(a.hours), "truth": truth(a.hours), "bsky": bsky(a.hours),
            "memeorandum": memeorandum()}
    (OUT / f"{stamp}.json").write_text(json.dumps(data, indent=1, ensure_ascii=False))
    L = [f"# RADAR {stamp} (last {a.hours:.0f} h; VPH from YouTube RSS)", "",
         "## STANCE-FIT: same-stance rivals (D), title has a Trump/MAGA antagonist — only these can become a case"]
    L += [f"- {r['vph']:>7,} VPH | {r['age_h']:>4} h | {r['ch']} | {r['title']} | {r['id']}"
          for r in data["videos"] if r["stance"] == "D" and r["fit"]][:25]
    L += ["", "## All rival videos by VPH (N = neutral network, heat only; * = stance-fit)"]
    L += [f"- {r['vph']:>7,} VPH | {r['age_h']:>4} h | {r['stance']}{'*' if r['fit'] else ' '} | {r['ch']} | {r['title']} | {r['id']}"
          for r in data["videos"][:40]]
    L += ["", "## Trump Truth Social"] + [f"- {p['when']} {p['text'][:220]} ({p['url']})" for p in data["truth"][:20]]
    L += ["", "## Bluesky (likes/h)"] + [f"- {p['likes_per_h']}/h {p['who']}: {p['text'][:160]}" for p in data["bsky"][:15]]
    L += ["", "## Memeorandum"] + [f"- {t}" for t in data["memeorandum"]]
    (ROOT / "control/RADAR.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
