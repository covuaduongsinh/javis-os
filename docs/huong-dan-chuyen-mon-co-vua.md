# Cẩm Nang Sử Dụng: Bộ Tính Năng Chuyên Môn Cờ Vua Trên Javis OS

Chào mừng bạn đến với **Hệ Thống Trợ Lý Chuyên Môn Cờ Vua** tích hợp trong Javis OS dành riêng cho hệ sinh thái **Cờ vua Dương Sinh**.

Tài liệu này hướng dẫn chi tiết cách sử dụng các tính năng cờ vua từ cơ bản đến nâng cao thông qua chat trực tiếp (Web Dashboard, Zalo, Telegram) hoặc qua các Trợ lý AI chuyên môn.

---

## 1. Tổng Quan 5 Plugin Cờ Vua Đang Hoạt Động

Bạn có thể vào mục **Năng lực > Plugins** trên thanh điều hướng để xem hoặc bật/tắt từng plugin:

| Plugin | Tên hiển thị | Danh mục công cụ | Chức năng chính |
|---|---|---|---|
| `chess-engine` | **Đánh giá & Phân tích Thế cờ** | `chess_eval`, `chess_game_analyze`, `chess_tablebase` | Đánh giá điểm thế cờ Stockfish, tìm nước Blunder, tính Accuracy %, cờ tàn Syzygy 7 quân |
| `chess-openings` | **Sách Khai cuộc ECO** | `chess_openings` | Tra cứu tên khai cuộc, mã ECO, tỷ lệ thắng/hòa của Grandmasters |
| `chess-puzzles` | **Ngân hàng Bài tập & Thế cờ** | `chess_puzzles` | Sinh bài tập theo chủ đề (*Ghim, Bắt đôi, Chiếu hết...*), tạo bài tập sửa lỗi cá nhân |
| `chess-scout` | **Trinh sát Kỳ thủ & Đối thủ** | `chess_player_scout` | Phân tích thói quen khai cuộc, tỷ lệ thắng/thua của kỳ thủ trên Lichess / Chess.com |
| `chess-board` | **Bàn cờ Trực quan** | `chess_render_board` | Vẽ hình bàn cờ ASCII/Markdown/SVG có tọa độ chuẩn FIDE |

---

## 2. Các Mẫu Câu Lệnh Thực Tế (Prompt Templates)

Bạn có thể nhắn tin trực tiếp với Javis ở khung chat bất kỳ hoặc chuyển sang các Agent chuyên biệt:

### 🔍 1. Phân Tích Thế Cờ FEN Đơn Lẻ
> **Mẫu lệnh:**
> *"Javis hãy phân tích thế cờ này giúp tôi: `r1bqkb1r/pppp1ppp/2n5/4p3/2B1n3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 5`"*

- **Javis sẽ làm gì:**
  - Tự động nhận diện khai cuộc (Italian Game / Two Knights Defence).
  - Đánh giá điểm số của máy (vd: `+0.45 pawns`), gợi ý 3 nước đi tối ưu (`Bxf7+`, `d4`, `Qe2`).
  - Vẽ bàn cờ trực quan kèm tọa độ để bạn nhìn rõ vị trí các quân.

---

### 📊 2. Phân Tích Toàn Bộ Ván Đấu PGN (Chấm Điểm & Tìm Lỗi Sai)
> **Mẫu lệnh:**
> *"Javis hãy phân tích ván đấu này của học viên và chỉ ra các bước ngoặt sai lầm: [Dán nội dung PGN vào đây]"*

- **Javis sẽ làm gì:**
  - Tính điểm độ chính xác (**Accuracy %**) và điểm tổn thất (**ACPL**) của cả hai bên.
  - Liệt kê chính xác các nước **Blunder** (Sai lầm lớn làm mất ưu thế), **Mistake** (Sai sót), **Inaccuracy** (Thiếu chính xác).
  - Đưa ra bài học cốt lõi sau ván đấu để HLV gửi cho học viên.

---

### 🧩 3. Sinh Bài Tập Chiến Thuật Cho Lớp Học
> **Mẫu lệnh:**
> *"Tìm cho thầy 3 bài tập cờ vua chủ đề Bắt đôi (Fork) mức Elo 1300 cho học viên ôn tập"*
>
> *(Hoặc: "Tìm 2 bài tập cờ tàn Tốt cơ bản mức Elo 1200")*

- **Javis sẽ làm gì:**
  - Trích xuất bài tập từ ngân hàng bài tập theo đúng chủ đề và mức Elo.
  - Vẽ bàn cờ cho từng bài tập, ghi rõ lượt Trắng đi hay Đen đi, kèm gợi ý và đáp án nước đi tối ưu.

---

### 🔄 4. Biến Ván Thua Thành Bài Tập Sửa Lỗi (Blunder to Puzzle)
> **Mẫu lệnh:**
> *"Học viên Nguyễn Văn A vừa đấu ván này bị thua, hãy trích xuất các thế cờ em ấy đi sai để làm bài tập về nhà: [Dán PGN]"*

- **Javis sẽ làm gì:**
  - Tự động lọc ra những thời điểm học viên đi blunder.
  - Tạo các câu hỏi tình huống: *"Ở nước thứ 15, em đã đi Xe e8 dẫn đến mất quân. Hãy tìm lại nước đi tối ưu nhất?"*

---

### 🕵️ 5. Trinh Sát Đối Thủ Trước Giải Đấu
> **Mẫu lệnh:**
> *"Trinh sát kỳ thủ Lichess `magnuscarlsen` (hoặc tên tài khoản đối thủ) giúp tôi để chuẩn bị cho học viên"*

- **Javis sẽ làm gì:**
  - Quét lịch sử đấu gần nhất của đối thủ.
  - Báo cáo: Khi cầm Trắng họ thích đánh khai cuộc gì? Khi cầm Đen chống 1.e4/1.d4 họ đáp trả bằng hệ thống nào? Tỷ lệ thắng thua ra sao?
  - Gợi ý kế hoạch tác chiến để khắc chế đối thủ.

---

### 👑 6. Tra Cứu Cờ Tàn Tuyệt Đối (Syzygy Tablebase 7 Quân)
> **Mẫu lệnh:**
> *"Thế cờ tàn này là Thắng, Hòa hay Thua lý thuyết: `8/8/8/4k3/4P3/4K3/8/8 w - - 0 1`"*

- **Javis sẽ làm gì:**
  - Tra cứu trực tiếp Syzygy Tablebase và khẳng định kết quả 100% chính xác (vd: *Trắng thắng lý thuyết, chiếu hết sau N nước nếu Đen đi chuẩn nhất*), giải thích kỹ thuật chiếm ô đối diện (Opposition).

---

## 3. Cách Sử Dụng 3 Agent Cờ Vua Chuyên Biệt

Mở menu **Năng lực > Cộng sự > Trợ lý**, bạn sẽ thấy 3 Agent cờ vua đã được tạo sẵn:

1. **👨‍🏫 Huấn luyện viên Cờ Vua (`hlv-co-vua`):**
   - Đóng vai HLV trưởng ân cần, giải thích nước đi cờ vua kèm lý do sư phạm (an toàn Vua, chiếm trung tâm, cấu trúc Tốt).
2. **🧐 Chuyên Gia Phân Tích Ván Đấu (`chuyen-gia-phan-tich-van-dau`):**
   - Đóng vai Đại Kiện Tướng chuyên bóc tách biên bản thi đấu sau các giải đấu lớn, chỉ ra điểm rơi phong độ và bài học chiến lược.
3. **🎯 Trợ Lý Trinh Sát Đối Thủ (`trinh-sat-doi-thu`):**
   - Đóng vai trinh sát viên chuyên lập kế hoạch tác chiến và chuẩn bị biến khai cuộc khắc chế trước từng vòng đấu.

---

## 4. Kết Nối Đồng Bộ Với Lõi Cờ Vua Dương Sinh

Khi bạn hỏi về một học viên cụ thể trong hệ thống (vd: *"Kiểm tra phong độ thi đấu của em Trần Minh Quân"*):
1. Javis sẽ dùng tool `ds_hoc_vien` để tìm tài khoản Lichess của em đó.
2. Tự động kết hợp với tool `chess_player_scout` để tổng hợp thành tích thi đấu gần nhất và đề xuất bài tập phù hợp cho Huấn luyện viên.

---

## 5. An Toàn Cập Nhật (Upstream Safe)

Toàn bộ hệ thống cờ vua nằm hoàn toàn trong các thư mục độc lập:
- `system/plugins/chess-*/`
- `server/chess_core/`
- `brains/Brain Default/agents/` & `skills/`

Bạn có thể an tâm chạy lệnh `git pull upstream main` để nâng cấp các phiên bản Javis OS mới nhất trong tương lai mà **không lo bị xung đột mã nguồn**.
