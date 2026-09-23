# Kế hoạch phát triển và tài liệu quy hoạch (Plans)

Thư mục này dùng để lưu trữ toàn bộ các kế hoạch nâng cấp, tính năng mới, tái cấu trúc (refactoring) và đồng bộ hệ thống của dự án **Javis OS (covuaduongsinh fork)**.

## Quy ước đặt tên file

- Định dạng: `YYYY-MM-DD-<ten-ke-hoach-ngan-gon>.md`
- Ví dụ: `2026-09-23-dong-bo-upstream-v0-64-20.md`

## Cấu trúc chuẩn của một kế hoạch

Mỗi tài liệu kế hoạch cần tuân thủ cấu trúc:
1. **Goal:** Mục tiêu rõ ràng trong 1 câu.
2. **Architecture & Diagram:** Giải pháp kiến trúc và sơ đồ Mermaid.
3. **Global Constraints:** Các ràng buộc và phạm vi an toàn dữ liệu.
4. **Bite-sized Tasks:** Từng tác vụ chi tiết kèm checkbox `- [ ]`, code diff, lệnh test và commit tương ứng.
5. **Verification Plan:** Kịch bản kiểm thử tự động và thủ công trước khi bàn giao.
