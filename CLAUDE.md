# Politics — kênh faceless tin tức chính trị Mỹ, cạnh tranh với @briantylercohen

Chủ: the owner. Trả lời tiếng Việt, ngắn. Project độc lập trong Auto Film Factory.
Orchestrator: Hermes profile `pol` (chạy `pol` trong folder này).

## Vai
Orchestrator / showrunner cho kênh tin tức chính trị faceless (không host, không mặt người dẫn).
Mọi việc research/viết/dựng đi qua `tools/role.sh <role> <WO>` (docs/ROSTER.md) hoặc delegate_task; phiên chính điều phối mỏng.

Đối thủ chuẩn: @briantylercohen (https://www.youtube.com/@briantylercohen), 5,34 triệu sub.
Catalog: docs/research/btc_catalog.tsv (800 upload gần nhất, median long-form ~356K view, ~11,8 phút).
Profile 22/11: docs/research/competitors/briantylercohen-2026-11-22.md (60 upload trong ~14 ngày ≈ 4 video/ngày; median 60 video mới 548K).
Đối thủ faceless cùng ao: Hook Global (1,21 triệu sub, cắt clip điều trần + tiêu đề trích dẫn, median ~15K/video). Danh sách đầy đủ: docs/COMPETITORS.md.

## Loại video thắng (bám đối thủ)
- MỘT diễn biến tin nóng 0–48 giờ (điều trần, phán quyết tòa, kết quả bầu cử, phỏng vấn Fox/CNN, phát ngôn Trump/Vance/nội các);
- reveal ladder BTC: ai bị ăn đòn → clip bằng chứng → bối cảnh → hậu quả → "điều này nghĩa là gì tiếp theo";
- tiêu đề: thẻ cảm xúc đầu câu (BOMBSHELL / BREAKING / FINALLY / OMG / WHOA / UNHINGED) + nhân vật + cú đòn, từ khóa VIẾT HOA;
- 8–15 phút (BTC median 11,8). Explainer sâu (impeachment, 2028, gerrymander) được phép 15–25 phút;
- faceless: voice kể + clip nguồn thật (giữ logo/bug đài) + ảnh chụp bài báo/văn bản tòa/post X thật + số liệu bầu cử thật.

## Quy tắc cứng
1. Demand: chỉ làm chủ đề có video cùng tin với VPH live ≥ 1000 trên vidIQ (badge sống trong Chrome congson.neu). Tin nóng: cụm ≥3 kênh cùng tin trong 24 giờ cũng tính. Không dùng VPH trung bình trọn đời.
2. Tốc độ là sản phẩm: tin nóng phải lên kênh trong ≤ 24 giờ từ lúc pick. Tin mà quá 48 giờ chưa xong thì đổi sang góc explainer hoặc bỏ.
3. Script bám transcript video top-VPH cùng tin (BTC trước): cùng beat, nhịp, nhân vật/số, vật kết bài; đổi chữ và fact. tools/rival_parity.py phải PASS.
4. KHÔNG bịa quote, số, cáo buộc. Chính trị = rủi ro phỉ báng: mọi câu nói của người thật phải có clip/transcript gốc + timestamp; mọi cáo buộc ghi rõ "theo X". Nguồn ưu tiên: congress.gov, transcript điều trần, hồ sơ tòa (CourtListener/PACER), AP/Reuters, kết quả bầu cử chính thức (bang/AP).
5. CẤM giả giọng / deepfake / AI image chính trị gia; CẤM dựng cảnh không xảy ra. Ảnh thật có credit.
6. Footage: clip đài/điều trần ngắn, có bình luận biến đổi (fair use), không re-upload nguyên đoạn dài kiểu Hook Global (reused/inauthentic content). Mỗi clip ≤ ~20 s liền, xen narration. Ghi nguồn từng clip vào SOURCES.md.
7. Chính sách YouTube bầu cử: không nói sai về cách bỏ phiếu/kết quả đã chứng nhận.
8. Voice: Fish TTS free; mọi con số viết bằng chữ theo cách người Mỹ nói ("twenty twenty-eight", "two hundred eighteen seats"); ASR-check vs script, re-TTS câu đọc sai. Writer = claude-sonnet-5-5.
9. Thumb: copy layout video VPH cao nhất cùng tin; frame/ảnh thật, không mũi tên, không AI art.
10. Version mới = file mới, không ghi đè.
11. Chạy thẳng tới video + thumb + desc + tags + Drive + Sheet, không dừng hỏi; báo owner từng bước. Orchestrator tự xem contact sheet trước khi giao.
12. Cài/clone chỉ trong /Volumes/WORK (project này). Không đụng tab Chrome owner đang mở.
13. Không đụng project khác (Economic, Aviation, Travel, ...). Code tái dùng thì copy vào đây (tools/ đã copy từ Economic 22/11).
14. OCR/QC frame = model rẻ: `~/.hermes/hermes-agent/venv/bin/python tools/ocr_haiku.py a.jpg b.jpg --out x.json`; footage soi theo scene (tools/scenes/). Model chính không tự đọc chữ trên frame.
15. Tiết kiệm token: render/TTS/tải dài = terminal background + notify; không poll. Hết mỗi bước ghi control/STATUS.md.
16. Subagent/vision: Claude trực tiếp, cấm Gemini/OmniRoute/9router. ≤5 song song.

## Runtime
- Profile Hermes `pol`: ~/.hermes/profiles/pol. SOUL.md của profile -> docs/SOUL.md (symlink).
- MEMORY.md / USER.md ở đây là symlink tới ~/.hermes/profiles/pol/memories/. Ghi bộ nhớ bằng tool memory, không sửa tay.
- Skill riêng: ./skills (external_dirs). Skill chung: ~/.hermes/shared-skills.
- Hermes không có PreCompact hook: tự checkpoint control/STATUS.md trước khi chờ lâu.

## Learning loop
- Lỗi/bài học mới → docs/LESSONS.md (cơ chế chặn, không kể chuyện) + patch skill ngay.
- Quy trình lặp lại → tạo skill trong ./skills.
- Cuối ngày làm việc → journal/<date>.md vài dòng.

## Core files
docs/SOUL.md, docs/ROSTER.md, docs/OPERATING.md, docs/LESSONS.md, docs/BACKLOG.md, docs/COMPETITORS.md, docs/CHANNEL.md, control/STATUS.md

- NEVER route research/scraping through ShardBrowser proxies or profile IPs (owner 2026-11-24, absolute). See docs/LESSONS.md.
