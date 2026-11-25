# NEWS RADAR — săn tin từ mạng xã hội của nhân vật nổi tiếng Mỹ (đề xuất 2026-11-24)

## Nguồn đã đo thật hôm nay (curl, không login)
| Nguồn | Kết quả | Dùng làm gì |
|---|---|---|
| Truth Social của Trump qua trumpstruth.org/feed | OK, full text + giờ đăng, post 23/11 18:55 UTC có ngay | nguồn số 1: post Trump |
| Bluesky public API (getAuthorFeed) | OK, text + likes + reposts (Mark Hamill 8.5K likes/post) | Dem, người nổi tiếng chuyển sang Bluesky |
| X (Twitter) logged-out: nitter, xcancel | CHẾT (trống / trang chặn) | cần đường khác (dưới) |
| Exa search "X post" | OK, ra bài báo trích post X (vd MTG chửi Trump 22/11), trễ vài giờ | bắt post X đã thành tin |
| YouTube RSS của đối thủ | OK, có views + giờ đăng -> tự tính VPH, KHÔNG cần vidIQ/Chrome Allow. BTC "Trump ally PUBLICLY ABANDONS Trump" 6.5 h = 64K VPH | xác nhận nhu cầu |
| Memeorandum, Google News RSS, Politico, The Hill | OK | xem báo lớn đã đưa chưa, lấy nguồn |
| whitehouse.gov/presidential-actions/feed, Federal Register API, CourtListener RSS | OK | văn bản gốc để làm bằng chứng |
| Reddit, AP | chặn (403 / Cloudflare) | bỏ |
| Instagram/Threads/TikTok | không đụng (luật Meta của máy) | bỏ |

## Quy trình (tools/social_radar.py, cron 30 phút)
1. Watchlist ~80 tài khoản (docs/WATCHLIST.md): Trump, Vance, nội các (Hegseth, Bondi, Patel, Noem, Rubio...), MAGA quay xe
   (MTG, Massie, Tucker, Bannon), lãnh đạo Dem (Newsom, AOC, Raskin, Garcia, Crockett, Pritzker, Jeffries), người nổi tiếng
   hay nói chính trị (Mark Hamill, Stephen King, Musk), host Fox.
2. Lấy post mới: Truth (RSS), Bluesky (API), X (xem mục X). Chấm điểm: tốc độ like/repost theo giờ + kiểu tin ăn view
   (A chửi B, đồng minh quay lưng, tự thú trên sóng, đe dọa/ra lệnh, hậu quả thật: kiện, sa thải, bỏ phiếu).
3. Đối chiếu nhu cầu: RSS 30 kênh đối thủ (COMPETITORS.md) mỗi 30 phút. PASS khi ≥3 kênh làm cùng chuyện < 24 h hoặc
   1 video đối thủ ≥ 5K VPH. Ưu tiên chuyện kênh faceless (Pondering, Oversight Desk...) chưa làm.
4. Ghi control/RADAR.md: top 5 chuyện, mỗi chuyện có text post + link + ảnh chụp post thật (bằng chứng lên hình),
   video đối thủ + VPH, báo nào đã đưa, văn bản gốc nếu có.
5. Chuyện top 1 -> tự mở case + BRIEF -> chạy pipeline như cũ, mục tiêu post -> upload ≤ 24 h.

## Kiểu video hợp với nguồn này
"Cuộc khẩu chiến": post A -> post B đáp -> clip trên sóng -> văn bản/số liệu -> hậu quả + verdict. Mỗi bước là ảnh chụp
post thật hoặc clip thật, đúng chuẩn "proof" của kênh. Title theo BTC: "Trump ally PUBLICLY ABANDONS Trump...".

## X: chọn 1
A. Tài khoản X phụ (không phải acc chính) đăng nhập vào twitter-cli đã có sẵn trên máy: đọc list watchlist trực tiếp,
   gần realtime. Mày tự nhập cookie, tao không xem.
B. Không login: chỉ bắt post X khi báo đã trích (Exa), trễ 2-6 h. Đủ cho video phân tích, chậm cho tin nóng.
