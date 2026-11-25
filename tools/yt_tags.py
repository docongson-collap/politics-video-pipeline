#!/usr/bin/env python3
"""Fetch video tags (videoDetails.keywords) + channel keywords via YouTube innertube (works when yt-dlp/HTML are bot-blocked).
usage: python3 tools/yt_tags.py <out.json> <videoId|@handle> ...
"""
import json, sys, time, urllib.request, re

API = "https://www.youtube.com/youtubei/v1/{}?prettyPrint=false"
CTX = {"client": {"clientName": "WEB", "clientVersion": "2.20251015.01.00", "hl": "en"}}


def post(ep, body):
    body = dict(body, context=CTX)
    req = urllib.request.Request(API.format(ep), data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=20))


def video(vid):
    v = post("player", {"videoId": vid}).get("videoDetails", {})
    return {"id": vid, "title": v.get("title"), "channel": v.get("author"), "views": int(v.get("viewCount", 0) or 0),
            "keywords": v.get("keywords", [])}


def channel(handle):
    r = post("navigation/resolve_url", {"url": f"https://www.youtube.com/{handle}"})
    bid = r["endpoint"]["browseEndpoint"]["browseId"]
    d = post("browse", {"browseId": bid})
    md = d.get("metadata", {}).get("channelMetadataRenderer", {})
    return {"id": handle, "channel": md.get("title"), "description": md.get("description"), "channel_keywords": md.get("keywords", "")}


if __name__ == "__main__":
    out, items = sys.argv[1], sys.argv[2:]
    res = []
    for it in items:
        try:
            res.append(channel(it) if it.startswith("@") else video(it))
        except Exception as e:
            res.append({"id": it, "error": str(e)})
        time.sleep(0.4)
    json.dump(res, open(out, "w"), indent=1, ensure_ascii=False)
    print(f"{len(res)} items -> {out}; errors: {sum('error' in r for r in res)}")
