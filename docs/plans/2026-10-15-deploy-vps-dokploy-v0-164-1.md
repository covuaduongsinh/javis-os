# Kế hoạch triển khai (Deploy) Javis OS v0.164.1 lên VPS Dokploy

**Goal:** Triển khai phiên bản Javis OS mới nhất (v0.164.1) từ GitHub `covuaduongsinh/javis-os` lên VPS Dokploy tại `217.15.160.118`, phục vụ ổn định tại domain `https://javis.dsc.edu.vn`.

---

## 1. Thông tin hạ tầng & Cấu hình triển khai

- **VPS IP:** `217.15.160.118`
- **SSH Access:** `root@217.15.160.118:22` (Sử dụng key `C:\Users\duongsinh\.ssh\id_ed25519`)
- **Dokploy Control Panel:** `https://dokploy.dsc.edu.vn`
- **Dokploy Compose ID:** `qXE2SOod0UndLHhBfdNNi`
- **Dokploy App Name:** `compose-back-up-solid-state-program-8n8fy4`
- **Dokploy API Token:** `javis_appKLyoaMXqJKVnDyyKrssYKMGIfdkkrxpGUijBtXHdKehQOAMzrHcIPoacQLoSJmrE`
- **Domain:** `https://javis.dsc.edu.vn` (SSL Let's Encrypt qua Dokploy Traefik Proxy)
- **Container Service:** `javis` (Image: `ghcr.io/blogminhquy/javis-os:latest`)
- **Volumes bảo toàn:** `javis-data`, `javis-brains`, `claude-auth`, `codex-auth`

---

## 2. Các bước triển khai chi tiết

### Task 1: Kích hoạt Dokploy Deploy qua REST API
- Endpoint: `POST https://dokploy.dsc.edu.vn/api/compose.deploy`
- Payload: `{"composeId": "qXE2SOod0UndLHhBfdNNi"}`
- Header: `x-api-key: javis_appKLyoaMXqJKVnDyyKrssYKMGIfdkkrxpGUijBtXHdKehQOAMzrHcIPoacQLoSJmrE`

### Task 2: Đồng bộ các module tùy biến của Fork vào Container
- Đảm bảo các file/module tùy biến (Cờ vua Dương Sinh MCP, 5 Micro-plugins Cờ vua, Giao diện bàn cờ FEN, mcp_client.py, mcp-catalog.json) từ repo git clone của Dokploy (`/etc/dokploy/compose/compose-back-up-solid-state-program-8n8fy4/code`) được đồng bộ đầy đủ vào `/app` trong container `javis`.
- Khởi động lại container `javis` nếu cần thiết để nạp mã nguồn mới.

### Task 3: Xác thực toàn diện sau triển khai
- Kiểm tra Docker container: `docker ps -f name=javis`
- Kiểm tra log container: `docker logs javis --tail 50`
- Kiểm tra Endpoint Public: `curl -s https://javis.dsc.edu.vn/health` (HTTP 200 OK)
- Kiểm tra phiên bản hoạt động: `docker exec javis cat VERSION` (kỳ vọng: `0.164.1` hoặc bản mới nhất từ ghcr `0.165.1`).
