#!/usr/bin/env python3
"""Read-only scan of posts in FB groups (Politics profile, must already be started).
usage: fb_group_scan.py OUT.jsonl GROUP_ID[:sort] ...   sort = TOP_POSTS | CHRONOLOGICAL | (default feed)
Appends one JSON line per post: group, author, text, reactions, comments, shares, media, age, url."""
import json, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = str(Path.home() / ".hermes/hermes-agent/venv/bin/python")
CDP = str(ROOT / "tools/shard_fb_cdp.py")


def t(*a, timeout=90):
    r = subprocess.run([PY, CDP, *a], capture_output=True, text=True, timeout=timeout, cwd=ROOT)
    return "\n".join(l for l in (r.stdout + r.stderr).splitlines() if not l.startswith("health")).strip()


def ev(js):
    o = t("eval", js)
    try:
        return json.loads(o)
    except Exception:
        return o


EXTRACT = r'''(()=>{
const num=s=>{if(!s)return 0;s=s.replace(/,/g,"");const m=s.match(/([\d.]+)\s*([KM]?)/i);if(!m)return 0;return Math.round(parseFloat(m[1])*({K:1e3,M:1e6}[m[2].toUpperCase()]||1))};
const feed=document.querySelector("[role=feed]");if(!feed)return [];
const out=[];
[...feed.children].forEach(c=>{
 const a=c.querySelector("[aria-posinset], [role=article]")||c; const txt=c.innerText||""; if(txt.length<20)return;
 // expand "See more"
 const author=(c.querySelector("h2, h3, strong a, h4")||{}).innerText||"";
 const msg=[...c.querySelectorAll("[data-ad-preview=message], [data-ad-comet-preview=message], div[dir=auto][style*=text-align]")].map(e=>e.innerText).join(" ").trim();
 const labs=[...c.querySelectorAll("[aria-label]")].map(e=>e.getAttribute("aria-label"));
 let reactions=0; labs.forEach(l=>{const m=l.match(/^(Like|Love|Care|Haha|Wow|Sad|Angry): ([\d.,]+[KM]?) (people|person)/);if(m)reactions+=num(m[2])});
 const cl=labs.find(l=>/^Comment on .*, [\d.,]+[KM]? comments?$/.test(l)), sl=labs.find(l=>/^Share .*, [\d.,]+[KM]? shares?$/.test(l));
 const cm=cl&&cl.match(/, ([\d.,]+[KM]?) comments?$/), sh=sl&&sl.match(/, ([\d.,]+[KM]?) shares?$/);
 const links=[...c.querySelectorAll("a[href]")].map(x=>x.href);
 const url=links.find(h=>/\/groups\/[^/]+\/(posts|permalink)\/\d+/.test(h))||links.find(h=>/\/(reel|videos|watch)\//.test(h))||"";
 const media=c.querySelector("video")||links.some(h=>/\/(reel|videos|watch)\//.test(h))?"video":([...c.querySelectorAll("img")].some(i=>i.width>200)?"photo":"text");
 const ext=links.find(h=>/l\.facebook\.com\/l\.php/.test(h));
 out.push({author:author.split("\n")[0].slice(0,60),text:(msg||txt).replace(/\n+/g," ").slice(0,600),reactions,comments:cm?num(cm[1]):0,shares:sh?num(sh[1]):0,media:ext?"link":media,url:url.split("?")[0],raw_head:txt.replace(/\n+/g," | ").slice(0,160)});
});
return out})()'''


def scan(gid, sort, out, scrolls=10):
    u = f"https://www.facebook.com/groups/{gid}/" + (f"?sorting_setting={sort}" if sort else "")
    t("nav", u, "14")
    time.sleep(3)
    name = ev('(document.querySelector("h1 a, h1")||{}).innerText||""')
    seen, rows = set(), []
    for i in range(scrolls):
        ev('(()=>{document.querySelectorAll("[role=feed] [role=button]").forEach(b=>{if((b.innerText||"").trim()=="See more")b.click()});return 1})()')
        time.sleep(1)
        got = ev(EXTRACT)
        for p in got if isinstance(got, list) else []:
            k = p["url"] or p["text"][:80]
            if k in seen:
                continue
            seen.add(k)
            p.update(group=name, gid=gid, sort=sort or "default")
            rows.append(p)
        ev('window.scrollBy(0,2500)')
        time.sleep(3)
    with open(out, "a") as f:
        for p in rows:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"{gid} {sort}: {len(rows)} posts ({name})")


if __name__ == "__main__":
    out = sys.argv[1]
    for g in sys.argv[2:]:
        gid, _, sort = g.partition(":")
        scan(gid, sort, out)
