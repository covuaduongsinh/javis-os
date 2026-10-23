# Kế hoạch triển khai (Deploy) Javis OS v0.295.0 lên VPS Dokploy

**Goal:** Triển khai phiên bản Javis OS mới nhất (v0.295.0) từ GitHub `covuaduongsinh/javis-os` lên VPS Dokploy tại `217.15.160.118`, phục vụ ổn định và bảo mật tại domain `https://javis.dsc.edu.vn`.

---

## 1. Thông tin hạ tầng & Cấu hình triển khai

- **VPS IP:** `217.15.160.118`
- **SSH Access:** `root@217.15.160.118:22` (Sử dụng key `C:\Users\duongsinh\.ssh\id_ed25519`)
- **Dokploy Control Panel:** `https://dokploy.dsc.edu.vn`
- **Dokploy Compose ID:** `qXE2SOod0UndLHhBfdNNi`
- **Dokploy App Name:** `compose-back-up-solid-state-program-8n8fy4`
- **Dokploy API Token:** `javis_appKLyoaMXqJKVnDyyKrssYKMGIfdkkrxpGUijBtXHdKehQOAMzrHcIPoacQLoSJmrE`
- **Domain:** `https://javis.dsc.edu.vn` (SSL Let's Encrypt qua Dokploy Traefik Proxy)
- **Container Service:** `javis` (Image: `ghcr.io/blogminhquy/javis-os:latest` -> phiên bản `0.295.0`)
- **Volumes bảo toàn:** `javis-data`, `javis-brains`, `claude-auth`, `codex-auth`

---

## 2. Quy trình triển khai chi tiết

### Giai đoạn 1: Kích hoạt Dokploy Deploy qua REST API
- Gọi Dokploy API:
  - Endpoint: `POST https://dokploy.dsc.edu.vn/api/compose.deploy`
  - Header: `x-api-key: javis_appKLyoaMXqJKVnDyyKrssYKMGIfdkkrxpGUijBtXHdKehQOAMzrHcIPoacQLoSJmrE`
  - Body: `{"composeId": "qXE2SOod0UndLHhBfdNNi"}`
- Dokploy tự động kéo commit mới nhất `d933d39` từ GitHub `covuaduongsinh/javis-os` về thư mục `/etc/dokploy/compose/compose-back-up-solid-state-program-8n8fy4/code`, kéo image mới `ghcr.io/blogminhquy/javis-os:latest` (v0.295.0) và dựng container `javis`.

### Giai đoạn 2: Đồng bộ các module tùy biến của Fork vào Container
- Vì image gốc `ghcr.io` của upstream không chứa các module chuyên môn riêng của fork Cờ Vua Dương Sinh, quy trình triển khai đồng bộ các thành phần tùy biến từ thư mục mã nguồn clone trên VPS vào container:
  - `server/duongsinh_mcp.py` & `server/mcp_client.py` -> `/app/server/`
  - `server/chess_core/` -> `/app/server/chess_core/`
  - `system/mcp-catalog.json` -> `/app/system/mcp-catalog.json`
  - `system/plugins/chess-*` (5 micro-plugins cờ vua) -> `/app/system/plugins/`
  - `dashboard/chess-board-ui.js`, `dashboard/chat-render.js`, `dashboard/index.html` -> `/app/dashboard/`
  - Thư mục test suite `tests/` -> `/app/tests/`
- Thiết lập quyền sở hữu `javis:javis` và khởi động lại container:
  ```bash
  docker restart javis
  ```

### Giai đoạn 3: Kiểm thử và Xác thực toàn diện (Verification)

1. **Kiểm tra trạng thái container:**
   - Container `javis` đạt trạng thái `healthy`.
   - Phiên bản hệ thống: `docker exec javis cat /app/VERSION` -> `0.295.0`.
2. **Biên dịch bytecode trong container:**
   ```bash
   docker exec javis python -m compileall -q /app/server /app/system/plugins
   ```
3. **Chạy trọn vẹn test suite trong container:**
   - Test kết nối lõi Dương Sinh MCP: `docker exec javis python /app/tests/python/test_duongsinh_mcp.py` (PASS 55/55 checks)
   - Test 5 micro-plugins Cờ Vua: `docker exec javis python /app/tests/python/test_chess_modular_plugins.py` (PASS 21/21 checks)
   - Test UI Bàn cờ FEN & Editor: `docker exec javis node /app/tests/js/test_chess_board_ui.js` (PASS 5/5 checks)
4. **Kiểm tra Public HTTPS:**
   - Endpoint Healthcheck: `https://javis.dsc.edu.vn/health` -> HTTP 200 `{"status":"ok", ...}`
   - Endpoint Static Assets: `https://javis.dsc.edu.vn/static/chess-board-ui.js?v=1` -> HTTP 200 OK
   - Web Dashboard: `https://javis.dsc.edu.vn/` -> HTTP 200 OK
