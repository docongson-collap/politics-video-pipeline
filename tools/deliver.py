#!/usr/bin/env python3
"""Giao video lên Drive của the owner: upload video + thumbnail, lấy link, dựng sẵn dòng sheet.

    python3 docs/skills/drive-delivery/deliver.py <case-slug> [--thumb PATH] [--video PATH] [--dry]

Đọc <case>/delivery/title.txt, description.txt, tags.txt (UTF-8). Video mặc định là
output/<case-slug>-vN.mp4 có N lớn nhất; thumbnail mặc định là <case>/delivery/thumb.png.
Kết quả: file trên Drive mang tên đúng bằng title, <case>/delivery/row.tsv (cột A–F), dòng đó nằm
sẵn trong clipboard, rồi GHI THẲNG dòng đó vào Google Sheet qua Sheets API (token OAuth của rclone, scope drive),
chỉnh cao hàng 21 px và tự --verify. The owner 08/11: dùng API, KHÔNG dùng Chrome/Allow để điền Sheet nữa.

Không in cấu hình rclone (chứa token).
"""
import argparse, json, os, re, subprocess, sys, tempfile, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID", "")  # set your own Drive root folder id
SHEET_NAME = "00. Thông tin video.xlsx"
# Từ 20/9/2026 the owner chia folder theo kênh: kênh documentary = "Monkey" (Video/Monkey + tab "Monkey"),
# kênh extinct animals = "Extinct". Thumb/ chưa chia.
# Bản delivery cho project Politics (copy từ Economic 22/11). Case = cases/<slug>; luôn truyền --video và --thumb.
# Kênh Aviation = "Flight Anatomy" (Video/Flight Anatomy + Thumb/Flight Anatomy đã có trên Drive, ghost-flights + overnight-shipping giao ở đó).
CHANNEL = "Proof Politics"  # kênh Politics (owner chốt 24/11); đổi tên thì sửa cả docs/CHANNEL.md
VIDEO_DIR = f"Video/{CHANNEL}"
THUMB_DIR = f"Thumb/{CHANNEL}"
RC = ["rclone", "--drive-root-folder-id", FOLDER_ID]
LINK = "https://drive.google.com/file/d/{}/view?usp=drive_link"
BAD = re.compile(r"https?://|www\.", re.I)


def die(msg):
    sys.exit(f"LỖI: {msg}")


def run(args, **kw):
    return subprocess.run(args, check=True, text=True, **kw)


def _guard():
    if CHANNEL == "TBD":
        die("chưa có tên kênh: sửa CHANNEL trong tools/deliver.py + docs/CHANNEL.md")
    if CHANNEL.startswith("TODO"):
        die("chưa chốt tên kênh/tab Drive cho Aviation — hỏi the owner rồi sửa CHANNEL")


def latest_video(slug):
    # skip <slug>-vN.silent.mp4 (no audio) — only <slug>-vN.mp4 is deliverable
    vids = sorted((p for p in (ROOT / "output").glob(f"{slug}-v*.mp4") if re.search(r"-v(\d+)\.mp4$", p.name)),
                  key=lambda p: int(re.search(r"-v(\d+)\.mp4$", p.name).group(1)))
    if not vids:
        die(f"không có output/{slug}-vN.mp4")
    return vids[-1]


def drive_name(title, ext):
    # Drive chấp nhận gần hết ký tự; chỉ bỏ "/" vì rclone hiểu là thư mục.
    # Bỏ dấu chấm cuối title (27/9: "...Vanished." + ".mp4" thành "Vanished..mp4").
    return title.replace("/", "-").strip().rstrip(".") + ext


def file_id(folder, name, must=True):
    out = run(RC + ["lsjson", f"gdrive:{folder}", "--files-only"], capture_output=True).stdout
    for f in json.loads(out):
        if f["Name"] == name:
            return f["ID"]
    if not must:
        return "CHUA_UPLOAD"
    die(f"upload xong mà không thấy {folder}/{name} trên Drive")


def upload(src, folder, name, dry):
    dst = f"gdrive:{folder}/{name}"
    print(f"↑ {src.name} ({src.stat().st_size/1e6:.0f} MB) → {folder}/{name}")
    if dry:
        return file_id(folder, name, must=False)
    run(RC + ["copyto", str(src), dst, "--stats-one-line", "--stats", "30s", "-v"])
    return file_id(folder, name)


def read_sheet():
    """Trả về {row: {col: text}} của tab CHANNEL (export xlsx qua rclone)."""
    tmp = Path(tempfile.mkdtemp())
    run(RC + ["copyto", f"gdrive:{SHEET_NAME}", str(tmp / "sheet.xlsx")])
    z = zipfile.ZipFile(tmp / "sheet.xlsx")
    unesc = lambda s: (s.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
                        .replace("&apos;", "'").replace("&amp;", "&"))
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in re.findall(r"<si>(.*?)</si>", z.read("xl/sharedStrings.xml").decode("utf-8"), re.S):
            shared.append(unesc("".join(re.findall(r"<t[^>]*>(.*?)</t>", si, re.S))))
    rows = {}
    wb = z.read("xl/workbook.xml").decode("utf-8")
    m = re.search(r'<sheet\b[^>]*\bname="%s"[^>]*\br:id="([^"]+)"' % re.escape(CHANNEL), wb)
    if not m:
        die(f"sheet không có tab '{CHANNEL}'")
    rels = z.read("xl/_rels/workbook.xml.rels").decode("utf-8")
    rel = re.search(r'<Relationship\b[^>]*\bId="%s"[^>]*>' % re.escape(m.group(1)), rels).group(0)
    xml = z.read("xl/" + re.search(r'Target="([^"]+)"', rel).group(1).lstrip("/")).decode("utf-8")
    for c in re.finditer(r'<c r="([A-Z]+)(\d+)"([^>]*?)(?:/>|>(.*?)</c>)', xml, re.S):
        col, row, attrs, body = c.group(1), int(c.group(2)), c.group(3), c.group(4) or ""
        v = re.search(r"<v>(.*?)</v>", body, re.S)
        t = re.search(r"<t[^>]*>(.*?)</t>", body, re.S)
        if v and 't="s"' in attrs:
            text = shared[int(v.group(1))]
        elif v:
            text = unesc(v.group(1))
        elif t:
            text = unesc(t.group(1))
        else:
            continue
        if text.strip():
            rows.setdefault(row, {})[col] = text
    return rows


def target_row(rows, title):
    for r, cells in sorted(rows.items()):
        if r > 1 and cells.get("B", "").strip() == title:
            return r, True
    r = 2
    while rows.get(r, {}).get("B", "").strip():
        r += 1
    return r, False


def next_date(rows):
    """Cột G Lịch upload: ngày lớn nhất trong tab + 2 (the owner: các video cách nhau 1 ngày). Tab trống -> ngày mai + 1."""
    import datetime as dt
    best = None
    for r, cells in rows.items():
        g = cells.get("G", "").strip()
        if r < 2 or not g:
            continue
        try:
            v = dt.date(1899, 12, 30) + dt.timedelta(days=int(float(g)))
        except ValueError:
            try:
                v = dt.datetime.strptime(g, "%d/%m/%Y").date()
            except ValueError:
                continue
        best = v if best is None or v > best else best
    nxt = (best + dt.timedelta(days=2)) if best else dt.date.today() + dt.timedelta(days=2)
    return nxt.strftime("%d/%m/%Y")


def _token():
    """Access token OAuth của remote gdrive (rclone tự refresh khi gọi `about`). Không bao giờ in ra."""
    subprocess.run(RC + ["about", "gdrive:"], capture_output=True)
    cfg = json.loads(subprocess.run(["rclone", "config", "dump"], capture_output=True, text=True, check=True).stdout)
    return json.loads(cfg["gdrive"]["token"])["access_token"]


def _gapi(url, body=None, method=None):
    import urllib.request, urllib.error
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None, method=method,
                                 headers={"Authorization": "Bearer " + _token(), "Content-Type": "application/json"})
    try:
        return json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as e:
        die(f"Sheets API {e.code}: {e.read().decode()[:300]}")


def sheet_write(row, cells):
    """Ghi B<row>:G<row> (A = STT và H = checkbox đã có sẵn trong tab) + cao hàng 21 px, qua Sheets API."""
    import urllib.parse
    name = SHEET_NAME.rsplit(".", 1)[0]
    files = json.loads(run(RC + ["lsjson", "gdrive:", "--files-only"], capture_output=True).stdout)
    sid = next((f["ID"] for f in files if f["Name"] in (name, SHEET_NAME)), None) or die(f"không thấy sheet '{name}'")
    meta = _gapi(f"https://sheets.googleapis.com/v4/spreadsheets/{sid}?fields=sheets.properties")
    tab = next((s["properties"]["sheetId"] for s in meta["sheets"] if s["properties"]["title"] == CHANNEL), None)
    if tab is None:
        die(f"sheet không có tab '{CHANNEL}'")
    rng = urllib.parse.quote(f"'{CHANNEL}'!B{row}:G{row}")
    _gapi(f"https://sheets.googleapis.com/v4/spreadsheets/{sid}/values/{rng}?valueInputOption=USER_ENTERED",
          {"values": [cells[1:7]]}, "PUT")
    _gapi(f"https://sheets.googleapis.com/v4/spreadsheets/{sid}:batchUpdate",
          {"requests": [{"updateDimensionProperties": {"range": {"sheetId": tab, "dimension": "ROWS",
                                                                 "startIndex": row - 1, "endIndex": row},
                                                       "properties": {"pixelSize": 21}, "fields": "pixelSize"}}]}, "POST")


def tsv_cell(s):
    s = s.replace("\r\n", "\n").strip("\n")
    if any(ch in s for ch in '\n\t"'):
        return '"' + s.replace('"', '""') + '"'
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("case")
    ap.add_argument("--thumb")
    ap.add_argument("--video")
    ap.add_argument("--dry", action="store_true", help="không upload, chỉ kiểm tra đầu vào và dựng row.tsv")
    a = ap.parse_args()
    _guard()

    case = ROOT / a.case
    d = case / "delivery"
    need = {n: d / f"{n}.txt" for n in ("title", "description", "tags")}
    for n, p in need.items():
        if not p.exists():
            die(f"thiếu {p.relative_to(ROOT)} — title và thumbnail phải do the owner chốt trước")
    title = need["title"].read_text("utf-8").strip()
    desc = need["description"].read_text("utf-8").strip()
    tags = " ".join(need["tags"].read_text("utf-8").split("\n")).strip()
    thumb = Path(a.thumb) if a.thumb else d / "thumb.png"
    video = Path(a.video) if a.video else latest_video(a.case)
    for p in (thumb, video):
        if not p.exists():
            die(f"không thấy {p}")

    if "\n" in title or not title:
        die("title.txt phải đúng một dòng")
    if len(title) > 100:
        die(f"title {len(title)} ký tự > 100 (giới hạn YouTube)")
    if BAD.search(desc):
        die("description có link ngoài — the owner cấm link trong mô tả")
    if re.search(r"^\d+:\d\d\s+Part\s+\w+", desc, re.M | re.I):
        die('chapters còn tiền tố "Part N" — bỏ đi')
    if not re.search(r"^0:00 ", desc, re.M):
        die("description thiếu chapters (dòng 0:00 …)")
    if "#" not in desc.splitlines()[-1]:
        die("dòng cuối description phải là hashtag")
    if len(desc) > 5000:
        die(f"description {len(desc)} ký tự > 5000")
    if len(tags) > 500:
        die(f"tags {len(tags)} ký tự > 500")
    if thumb.stat().st_size > 2_000_000:
        die("thumbnail > 2 MB")

    vid_id = upload(video, VIDEO_DIR, drive_name(title, ".mp4"), a.dry)
    th_id = upload(thumb, THUMB_DIR, drive_name(title, thumb.suffix.lower()), a.dry)

    rows = read_sheet()
    row, existed = target_row(rows, title)
    cells = [str(row - 1), title, desc, tags, LINK.format(vid_id), LINK.format(th_id), next_date(rows)]
    out = d / "row.tsv"
    out.write_bytes(("\t".join(tsv_cell(c) for c in cells) + "\n").encode("utf-8"))
    env = dict(os.environ, LC_ALL="en_US.UTF-8")   # thiếu UTF-8 thì "—" thành mojibake
    subprocess.run(["pbcopy"], input=out.read_bytes(), env=env, check=True)

    print(f"\nvideo : {LINK.format(vid_id)}\nthumb : {LINK.format(th_id)}")
    print(f"row.tsv: {out.relative_to(ROOT)} (đã nằm trong clipboard)")
    if a.dry:
        print(f"--dry: không ghi Sheet (sẽ ghi tab '{CHANNEL}' dòng {row})")
        return
    sheet_write(row, cells)
    print(f"Sheet: đã ghi tab '{CHANNEL}' dòng {row} qua API ({'ghi đè dòng cùng title' if existed else 'dòng trống đầu tiên'}), cao 21 px")
    verify(a.case)


def verify(case_slug):
    """So ô B–F trên sheet với delivery/row.tsv."""
    d = ROOT / case_slug / "delivery"
    want = d / "row.tsv"
    if not want.exists():
        die("chưa có delivery/row.tsv")
    import csv, io
    cells = next(csv.reader(io.StringIO(want.read_text("utf-8")), delimiter="\t"))
    rows = read_sheet()
    row, existed = target_row(rows, cells[1])
    if not existed:
        die(f"sheet chưa có dòng mang title '{cells[1]}'")
    ok = True
    for col, val in zip("BCDEF", cells[1:6]):
        got = rows[row].get(col, "").replace("\r\n", "\n").strip()
        same = got == val.strip()
        ok &= same
        print(f"{col}{row}: {'khớp' if same else f'LỆCH (sheet {len(got)} ký tự, cần {len(val.strip())})'}")
    print("G%d (Lịch upload): chỉ điền khi the owner cho ngày · H%d (Upload YTB): để the owner tự tick" % (row, row))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    if "--verify" in sys.argv:
        sys.argv.remove("--verify")
        verify(sys.argv[1])
    else:
        main()
