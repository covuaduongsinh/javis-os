/* chess-board-ui.js - Component Bàn Cờ Trực Quan & Trình Xếp Cờ Sắc Nét cho Javis OS (Cờ Vua Dương Sinh)
   Thuần SVG/CSS/JS, không phụ thuộc CDN, hỗ trợ Light/Dark mode, lật bàn cờ, xem & sửa FEN trực tiếp,
   bảng xếp cờ (thêm/xóa/di chuyển quân), copy FEN chuẩn, mở Lichess Analysis đúng vị trí.
*/
(function () {
  "use strict";

  // Bộ mã SVG vector chuẩn thi đấu quốc tế (Lichess/Wikimedia standard)
  var PIECES_SVG = {
    // Quân Trắng
    P: '<svg viewBox="0 0 45 45"><path d="M22 9c-2.21 0-4 1.79-4 4 0 .89.29 1.71.78 2.38-1.95 1.12-3.28 3.21-3.28 5.62 0 2.03.93 3.84 2.38 5.03-3.26 1.4-5.63 4.6-5.88 8.47h19.98c-.24-3.87-2.61-7.07-5.88-8.47 1.45-1.19 2.38-3 2.38-5.03 0-2.41-1.33-4.5-3.28-5.62.49-.67.78-1.49.78-2.38 0-2.21-1.79-4-4-4z" fill="#fff" stroke="#000" stroke-width="1.5" stroke-linecap="round"/></svg>',
    N: '<svg viewBox="0 0 45 45"><path d="M22 10c10.5 1 16.5 8 16 29H15c0-9 10-6.5 8-21" fill="#fff" stroke="#000" stroke-width="1.5"/><path d="M24 18c.38 2.91-5.55 7.37-8 9-3 2-2.82 4.34-5 4-1.042-.94 1.41-3.04 0-3-1 0 .19 1.23-1 2-1 0-4.003 1-4-4 0-2 6-12 6-12s1.89-1.9 2-3.5c-.73-.994-.5-2-.5-3 1-1 3 2.5 3 2.5h2s.78-1.992 2.5-3c1 0 1 3 1 3" fill="#fff" stroke="#000" stroke-width="1.5"/><circle cx="9.5" cy="25.5" r="1" fill="#000"/></svg>',
    B: '<svg viewBox="0 0 45 45"><g fill="none" fill-rule="evenodd" stroke="#000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><g fill="#fff"><path d="M9 36c3.39-.97 10.11.43 13.5-2 3.39 2.43 10.11 1.03 13.5 2 0 0 1.65.54 3 2-.68.97-1.65.99-3 .5-3.39-.97-10.11.46-13.5-1-3.39 1.46-10.11.03-13.5 1-1.354.49-2.323.47-3-.5 1.354-1.94 3-2 3-2z"/><path d="M15 32c2.5 2.5 12.5 2.5 15 0 .5-1.5 0-2 0-2 0-2.5-2.5-4-2.5-4 5.5-1.5 6-11.5-5-15.5-11 4-10.5 14-5 15.5 0 0-2.5 1.5-2.5 4 0 0-.5.5 0 2z"/><path d="M25 8a2.5 2.5 0 1 1-5 0 2.5 2.5 0 1 1 5 0z"/></g><path d="M17.5 26h10M15 30h15M22.5 15.5v5M20 18h5"/></g></svg>',
    R: '<svg viewBox="0 0 45 45"><g fill="#fff" stroke="#000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 39h27v-3H9v3zM12 36v-4h21v4H12zM11 14V9h4v2h5V9h5v2h5V9h4v5" stroke-linecap="butt"/><path d="M34 14l-3 3H14l-3-3"/><path d="M31 17v12.5H14V17"/><path d="M31 29.5l1.5 2.5h-20l1.5-2.5"/><path d="M11 39h23v2.5H11z" stroke-linecap="butt"/></g></svg>',
    Q: '<svg viewBox="0 0 45 45"><g fill="#fff" stroke="#000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8 12a2 2 0 1 1-4 0 2 2 0 1 1 4 0zM24.5 7.5a2 2 0 1 1-4 0 2 2 0 1 1 4 0zM41 12a2 2 0 1 1-4 0 2 2 0 1 1 4 0zM16 8.5a2 2 0 1 1-4 0 2 2 0 1 1 4 0zM33 8.5a2 2 0 1 1-4 0 2 2 0 1 1 4 0z"/><path d="M9 26c8.5-1.5 21-1.5 27 0l2-12-7 11V11l-5.5 13.5-3-15-3 15-5.5-14V25L7 14l2 12z"/><path d="M9 26c0 2 1.5 2 2.5 4 1 1.5 1 1 .5 3.5-1.5 1-1.5 2.5-1.5 2.5-1.5 1.5.5 2.5.5 2.5 6.5 1 16.5 1 23 0 0 0 2-1 .5-2.5 0 0 0-1.5-1.5-2.5-.5-2.5-.5-2 .5-3.5 1-2 2.5-2 2.5-4-8.5-1.5-18.5-1.5-27 0z"/><circle cx="6" cy="12" r="2"/><circle cx="14" cy="9" r="2"/><circle cx="22.5" cy="8" r="2"/><circle cx="31" cy="9" r="2"/><circle cx="39" cy="12" r="2"/></g></svg>',
    K: '<svg viewBox="0 0 45 45"><g fill="none" fill-rule="evenodd" stroke="#000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22.5 11.63V6M20 8h5" stroke-linejoin="miter"/><path d="M22.5 25s4.5-7.5 3-10.5c0 0-1-2.5-3-2.5s-3 2.5-3 2.5c-1.5 3 3 10.5 3 10.5" fill="#fff" stroke-linecap="butt"/><path d="M11.5 37c5.5 3.5 15.5 3.5 21 0v-7s9-4.5 6-10.5c-4-6.5-13.5-3.5-16 4V23v-2c-2.5-7.5-12-10.5-16-4-3 6 6 10.5 6 10.5v7z" fill="#fff"/><path d="M11.5 30c5.5-3 15.5-3 21 0M11.5 33.5c5.5-3 15.5-3 21 0M11.5 37c5.5-3 15.5-3 21 0"/></g></svg>',

    // Quân Đen
    p: '<svg viewBox="0 0 45 45"><path d="M22 9c-2.21 0-4 1.79-4 4 0 .89.29 1.71.78 2.38-1.95 1.12-3.28 3.21-3.28 5.62 0 2.03.93 3.84 2.38 5.03-3.26 1.4-5.63 4.6-5.88 8.47h19.98c-.24-3.87-2.61-7.07-5.88-8.47 1.45-1.19 2.38-3 2.38-5.03 0-2.41-1.33-4.5-3.28-5.62.49-.67.78-1.49.78-2.38 0-2.21-1.79-4-4-4z" fill="#333" stroke="#000" stroke-width="1.5" stroke-linecap="round"/></svg>',
    n: '<svg viewBox="0 0 45 45"><path d="M22 10c10.5 1 16.5 8 16 29H15c0-9 10-6.5 8-21" fill="#333" stroke="#000" stroke-width="1.5"/><path d="M24 18c.38 2.91-5.55 7.37-8 9-3 2-2.82 4.34-5 4-1.042-.94 1.41-3.04 0-3-1 0 .19 1.23-1 2-1 0-4.003 1-4-4 0-2 6-12 6-12s1.89-1.9 2-3.5c-.73-.994-.5-2-.5-3 1-1 3 2.5 3 2.5h2s.78-1.992 2.5-3c1 0 1 3 1 3" fill="#333" stroke="#000" stroke-width="1.5"/><circle cx="9.5" cy="25.5" r="1" fill="#fff"/></svg>',
    b: '<svg viewBox="0 0 45 45"><g fill="none" fill-rule="evenodd" stroke="#000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><g fill="#333"><path d="M9 36c3.39-.97 10.11.43 13.5-2 3.39 2.43 10.11 1.03 13.5 2 0 0 1.65.54 3 2-.68.97-1.65.99-3 .5-3.39-.97-10.11.46-13.5-1-3.39 1.46-10.11.03-13.5 1-1.354.49-2.323.47-3-.5 1.354-1.94 3-2 3-2z"/><path d="M15 32c2.5 2.5 12.5 2.5 15 0 .5-1.5 0-2 0-2 0-2.5-2.5-4-2.5-4 5.5-1.5 6-11.5-5-15.5-11 4-10.5 14-5 15.5 0 0-2.5 1.5-2.5 4 0 0-.5.5 0 2z"/><path d="M25 8a2.5 2.5 0 1 1-5 0 2.5 2.5 0 1 1 5 0z"/></g><path d="M17.5 26h10M15 30h15M22.5 15.5v5M20 18h5" stroke="#fff"/></g></svg>',
    r: '<svg viewBox="0 0 45 45"><g fill="#333" stroke="#000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M9 39h27v-3H9v3zM12 36v-4h21v4H12zM11 14V9h4v2h5V9h5v2h5V9h4v5" stroke-linecap="butt"/><path d="M34 14l-3 3H14l-3-3"/><path d="M31 17v12.5H14V17"/><path d="M31 29.5l1.5 2.5h-20l1.5-2.5"/><path d="M11 39h23v2.5H11z" stroke-linecap="butt"/></g></svg>',
    q: '<svg viewBox="0 0 45 45"><g fill="#333" stroke="#000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M8 12a2 2 0 1 1-4 0 2 2 0 1 1 4 0zM24.5 7.5a2 2 0 1 1-4 0 2 2 0 1 1 4 0zM41 12a2 2 0 1 1-4 0 2 2 0 1 1 4 0zM16 8.5a2 2 0 1 1-4 0 2 2 0 1 1 4 0zM33 8.5a2 2 0 1 1-4 0 2 2 0 1 1 4 0z"/><path d="M9 26c8.5-1.5 21-1.5 27 0l2-12-7 11V11l-5.5 13.5-3-15-3 15-5.5-14V25L7 14l2 12z"/><path d="M9 26c0 2 1.5 2 2.5 4 1 1.5 1 1 .5 3.5-1.5 1-1.5 2.5-1.5 2.5-1.5 1.5.5 2.5.5 2.5 6.5 1 16.5 1 23 0 0 0 2-1 .5-2.5 0 0 0-1.5-1.5-2.5-.5-2.5-.5-2 .5-3.5 1-2 2.5-2 2.5-4-8.5-1.5-18.5-1.5-27 0z"/><circle cx="6" cy="12" r="2"/><circle cx="14" cy="9" r="2"/><circle cx="22.5" cy="8" r="2"/><circle cx="31" cy="9" r="2"/><circle cx="39" cy="12" r="2"/></g></svg>',
    k: '<svg viewBox="0 0 45 45"><g fill="none" fill-rule="evenodd" stroke="#000" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22.5 11.63V6M20 8h5" stroke-linejoin="miter"/><path d="M22.5 25s4.5-7.5 3-10.5c0 0-1-2.5-3-2.5s-3 2.5-3 2.5c-1.5 3 3 10.5 3 10.5" fill="#333" stroke-linecap="butt"/><path d="M11.5 37c5.5 3.5 15.5 3.5 21 0v-7s9-4.5 6-10.5c-4-6.5-13.5-3.5-16 4V23v-2c-2.5-7.5-12-10.5-16-4-3 6 6 10.5 6 10.5v7z" fill="#333"/><path d="M11.5 30c5.5-3 15.5-3 21 0M11.5 33.5c5.5-3 15.5-3 21 0M11.5 37c5.5-3 15.5-3 21 0" stroke="#fff"/></g></svg>'
  };

  // CSS Stylesheet tự động gắn cho bàn cờ (Tối ưu bố cục gọn gàng, căn chỉnh chuẩn xác)
  var CHESS_CSS = `
    .jv-cb-wrap {
      display: inline-flex;
      flex-direction: column;
      margin: 12px 0;
      padding: 12px;
      background: var(--bg-card, #ffffff);
      border: 1px solid var(--border-color, #e2e8f0);
      border-radius: 12px;
      box-shadow: 0 4px 14px rgba(0,0,0,0.08);
      width: fit-content;
      max-width: 100%;
      font-family: inherit;
      box-sizing: border-box;
      vertical-align: top;
    }
    .dark .jv-cb-wrap {
      background: #1e293b;
      border-color: #334155;
      box-shadow: 0 4px 14px rgba(0,0,0,0.3);
    }
    .jv-cb-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 8px;
      font-size: 13px;
      font-weight: 600;
      color: var(--text-color, #1e293b);
      gap: 8px;
      width: 100%;
      box-sizing: border-box;
    }
    .dark .jv-cb-header { color: #f1f5f9; }
    .jv-cb-badge {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      padding: 3px 8px;
      background: var(--bg-subtle, #f1f5f9);
      border-radius: 6px;
      font-size: 12px;
      font-weight: 500;
      white-space: nowrap;
    }
    .dark .jv-cb-badge { background: #334155; color: #cbd5e1; }
    .jv-cb-badge.edit-active {
      background: #fef08a;
      color: #854d0e;
      font-weight: bold;
    }
    .dark .jv-cb-badge.edit-active {
      background: #854d0e;
      color: #fef08a;
    }

    /* Bàn cờ và Tọa độ căn chỉnh hoàn hảo */
    .jv-cb-board-box {
      display: inline-flex;
      flex-direction: column;
      user-select: none;
      width: fit-content;
      box-sizing: border-box;
    }
    .jv-cb-board-row {
      display: flex;
      align-items: stretch;
    }
    .jv-cb-ranks {
      width: 18px;
      display: flex;
      flex-direction: column;
      justify-content: space-around;
      align-items: center;
      font-size: 11px;
      font-weight: bold;
      color: #64748b;
      padding-right: 4px;
      box-sizing: border-box;
    }
    .jv-cb-grid {
      width: min(336px, calc(100vw - 72px));
      height: min(336px, calc(100vw - 72px));
      display: grid;
      grid-template-columns: repeat(8, 1fr);
      grid-template-rows: repeat(8, 1fr);
      border: 2px solid #475569;
      border-radius: 4px;
      overflow: hidden;
      box-shadow: 0 2px 8px rgba(0,0,0,0.12);
      box-sizing: border-box;
      aspect-ratio: 1 / 1;
    }
    .jv-cb-files {
      margin-left: 18px;
      width: min(336px, calc(100vw - 72px));
      display: flex;
      justify-content: space-around;
      align-items: center;
      font-size: 11px;
      font-weight: bold;
      color: #64748b;
      padding-top: 4px;
      box-sizing: border-box;
    }
    .jv-cb-sq {
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      user-select: none;
      transition: background-color 0.1s ease;
      width: 100%;
      height: 100%;
      box-sizing: border-box;
    }
    .jv-cb-sq.light { background-color: #f0d9b5; }
    .jv-cb-sq.dark { background-color: #b58863; }
    .jv-cb-sq.selected {
      outline: 3px solid #3b82f6 !important;
      outline-offset: -3px;
      background-color: #93c5fd !important;
      z-index: 2;
    }
    .jv-cb-sq.editable {
      cursor: pointer;
    }
    .jv-cb-sq.editable:hover {
      filter: brightness(1.08);
    }
    .jv-cb-sq svg {
      width: 85%;
      height: 85%;
      filter: drop-shadow(0 1px 2px rgba(0,0,0,0.25));
      pointer-events: none;
    }

    .jv-cb-actions {
      display: flex;
      gap: 6px;
      margin-top: 10px;
      flex-wrap: wrap;
      max-width: min(354px, calc(100vw - 54px));
      box-sizing: border-box;
    }
    .jv-cb-btn {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 5px 9px;
      background: var(--bg-subtle, #f1f5f9);
      border: 1px solid var(--border-color, #cbd5e1);
      border-radius: 6px;
      font-size: 12px;
      color: var(--text-color, #334155);
      cursor: pointer;
      transition: all 0.15s ease;
      text-decoration: none;
      white-space: nowrap;
    }
    .dark .jv-cb-btn {
      background: #334155;
      border-color: #475569;
      color: #f1f5f9;
    }
    .jv-cb-btn:hover {
      background: var(--primary-color, #2563eb);
      color: #ffffff;
      border-color: var(--primary-color, #2563eb);
    }
    .jv-cb-btn.active {
      background: #2563eb;
      color: #ffffff;
      border-color: #1d4ed8;
      font-weight: 600;
    }
    .jv-cb-btn.btn-save {
      background: #16a34a;
      color: #ffffff;
      border-color: #15803d;
      font-weight: bold;
    }
    .jv-cb-btn.btn-save:hover {
      background: #15803d;
    }

    /* Drawer xem & sửa FEN */
    .jv-cb-fen-drawer {
      margin-top: 10px;
      padding: 8px;
      background: var(--bg-subtle, #f8fafc);
      border: 1px dashed var(--border-color, #cbd5e1);
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      max-width: min(354px, calc(100vw - 54px));
      box-sizing: border-box;
    }
    .dark .jv-cb-fen-drawer {
      background: #0f172a;
      border-color: #475569;
    }
    .jv-cb-fen-input-row {
      display: flex;
      gap: 6px;
    }
    .jv-cb-fen-input {
      flex: 1;
      min-width: 0;
      padding: 5px 8px;
      font-family: monospace, Consolas, sans-serif;
      font-size: 11px;
      border: 1px solid #cbd5e1;
      border-radius: 4px;
      background: #ffffff;
      color: #0f172a;
    }
    .dark .jv-cb-fen-input {
      background: #1e293b;
      border-color: #475569;
      color: #f8fafc;
    }
    .jv-cb-fen-err {
      font-size: 11px;
      color: #ef4444;
      font-weight: 500;
    }

    /* Bảng chọn quân cờ (Piece Palette for Board Editor) */
    .jv-cb-palette-wrap {
      margin-top: 10px;
      padding: 8px;
      background: var(--bg-subtle, #f8fafc);
      border: 1px solid var(--border-color, #cbd5e1);
      border-radius: 8px;
      display: flex;
      flex-direction: column;
      gap: 6px;
      max-width: min(354px, calc(100vw - 54px));
      box-sizing: border-box;
    }
    .dark .jv-cb-palette-wrap {
      background: #0f172a;
      border-color: #334155;
    }
    .jv-cb-palette-row {
      display: flex;
      gap: 4px;
      align-items: center;
      flex-wrap: wrap;
    }
    .jv-cb-palette-title {
      font-size: 11px;
      font-weight: bold;
      color: #64748b;
      margin-right: 4px;
      min-width: 38px;
    }
    .jv-cb-tool-btn {
      width: 30px;
      height: 30px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--bg-card, #ffffff);
      border: 1px solid var(--border-color, #cbd5e1);
      border-radius: 6px;
      cursor: pointer;
      padding: 2px;
      transition: all 0.12s ease;
      box-sizing: border-box;
    }
    .dark .jv-cb-tool-btn {
      background: #1e293b;
      border-color: #475569;
    }
    .jv-cb-tool-btn svg {
      width: 100%;
      height: 100%;
    }
    .jv-cb-tool-btn:hover {
      border-color: #3b82f6;
      background: #eff6ff;
    }
    .dark .jv-cb-tool-btn:hover {
      background: #1e3a8a;
    }
    .jv-cb-tool-btn.active {
      border-color: #2563eb;
      background: #dbeafe;
      box-shadow: 0 0 0 2px #3b82f6;
    }
    .dark .jv-cb-tool-btn.active {
      background: #1e40af;
      border-color: #60a5fa;
      box-shadow: 0 0 0 2px #60a5fa;
    }
  `;

  // Gắn CSS vào document head
  function injectStyles() {
    if (typeof document === "undefined") return;
    if (document.getElementById("jv-chessboard-styles")) return;
    var style = document.createElement("style");
    style.id = "jv-chessboard-styles";
    style.textContent = CHESS_CSS;
    document.head.appendChild(style);
  }

  // Parse FEN thành ma trận 8x8
  function parseFen(fen) {
    fen = String(fen || "").trim();
    if (!fen) fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
    var parts = fen.split(/\s+/);
    var boardPart = parts[0] || "";
    var turn = (parts[1] || "w").toLowerCase();
    var castling = parts[2] || "-";
    var ep = parts[3] || "-";
    var halfmove = parts[4] || "0";
    var fullmove = parts[5] || "1";

    var rows = boardPart.split("/");
    var grid = [];

    for (var r = 0; r < 8; r++) {
      var rowStr = rows[r] || "8";
      var row = [];
      for (var c = 0; c < rowStr.length; c++) {
        var ch = rowStr[c];
        if (/\d/.test(ch)) {
          var count = parseInt(ch, 10);
          for (var k = 0; k < count; k++) row.push(null);
        } else {
          row.push(ch);
        }
      }
      while (row.length < 8) row.push(null);
      grid.push(row.slice(0, 8));
    }
    while (grid.length < 8) grid.push([null,null,null,null,null,null,null,null]);

    return {
      fen: fen,
      grid: grid,
      board: grid,
      turn: turn,
      isWhiteTurn: turn === "w",
      castling: castling,
      ep: ep,
      halfmove: halfmove,
      fullmove: fullmove
    };
  }

  // Chuyển ma trận 8x8 ngược lại thành chuỗi FEN chuẩn
  function buildFen(grid, turn, castling, ep, halfmove, fullmove) {
    var rows = [];
    for (var r = 0; r < 8; r++) {
      var rowStr = "";
      var emptyCount = 0;
      for (var c = 0; c < 8; c++) {
        var p = grid[r][c];
        if (!p) {
          emptyCount++;
        } else {
          if (emptyCount > 0) {
            rowStr += emptyCount;
            emptyCount = 0;
          }
          rowStr += p;
        }
      }
      if (emptyCount > 0) rowStr += emptyCount;
      rows.push(rowStr || "8");
    }
    var boardPart = rows.join("/");
    var t = turn || "w";
    var cstl = castling || "-";
    var e = ep || "-";
    var hm = halfmove || "0";
    var fm = fullmove || "1";
    return boardPart + " " + t + " " + cstl + " " + e + " " + hm + " " + fm;
  }

  // Kiểm tra tính hợp lệ của chuỗi FEN
  function validateFen(fen) {
    fen = String(fen || "").trim();
    if (!fen) return { valid: false, error: "Chuỗi FEN rỗng" };
    var parts = fen.split(/\s+/);
    var rows = parts[0].split("/");
    if (rows.length !== 8) {
      return { valid: false, error: "FEN phải có đúng 8 hàng (ngăn cách bởi dấu /)" };
    }
    for (var i = 0; i < 8; i++) {
      var row = rows[i];
      var count = 0;
      for (var j = 0; j < row.length; j++) {
        var ch = row[j];
        if (/[1-8]/.test(ch)) {
          count += parseInt(ch, 10);
        } else if (/[pnbrqkPNBRQK]/.test(ch)) {
          count += 1;
        } else {
          return { valid: false, error: "Ký tự không hợp lệ '" + ch + "' ở hàng " + (8 - i) };
        }
      }
      if (count !== 8) {
        return { valid: false, error: "Hàng " + (8 - i) + " có tổng số ô là " + count + " (cần đúng 8 ô)" };
      }
    }
    return { valid: true };
  }

  // Tạo cây DOM bàn cờ tương tác đầy đủ
  function renderChessboard(container, fen, perspective, editState) {
    if (!container) return;
    perspective = perspective || container.getAttribute("data-perspective") || "white";
    fen = (fen != null ? fen : container.getAttribute("data-fen")) || "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

    var isEditMode = editState && editState.active;
    var currentGrid = (editState && editState.grid) ? editState.grid : parseFen(fen).grid;
    var currentTurn = (editState && editState.turn) ? editState.turn : parseFen(fen).turn;
    var selectedTool = (editState && editState.selectedTool) ? editState.selectedTool : "move"; // 'move', 'erase', or piece 'P','N',etc.
    var selectedSq = editState ? editState.selectedSq : null; // {r, c}
    var showFenDrawer = editState ? !!editState.showFenDrawer : false;

    var currentFen = isEditMode ? buildFen(currentGrid, currentTurn) : fen;
    var isWhite = perspective.toLowerCase() !== "black";
    var isWhiteTurn = currentTurn === "w";

    var wrap = document.createElement("div");
    wrap.className = "jv-cb-wrap";

    // Header & Turn badge
    var header = document.createElement("div");
    header.className = "jv-cb-header";

    var titleSpan = document.createElement("span");
    titleSpan.innerHTML = isEditMode ? "✏️ <b>Trình Xếp & Sửa Thế Cờ</b>" : "♟ <b>Bàn cờ Thế trận</b>";
    header.appendChild(titleSpan);

    var badgeSpan = document.createElement("span");
    badgeSpan.className = "jv-cb-badge" + (isEditMode ? " edit-active" : "");
    badgeSpan.innerHTML = isEditMode
      ? (isWhiteTurn ? "⚪ Chế độ Sửa (Trắng đi)" : "⚫ Chế độ Sửa (Đen đi)")
      : (isWhiteTurn ? "⚪ Lượt Trắng đi" : "⚫ Lượt Đen đi");
    header.appendChild(badgeSpan);
    wrap.appendChild(header);

    // Board Container (Coordinates + 8x8 Grid)
    var boardBox = document.createElement("div");
    boardBox.className = "jv-cb-board-box";

    var boardRow = document.createElement("div");
    boardRow.className = "jv-cb-board-row";

    // Ranks (1-8)
    var ranksDiv = document.createElement("div");
    ranksDiv.className = "jv-cb-ranks";
    var rankLabels = isWhite ? [8, 7, 6, 5, 4, 3, 2, 1] : [1, 2, 3, 4, 5, 6, 7, 8];
    rankLabels.forEach(function (rk) {
      var s = document.createElement("span");
      s.textContent = rk;
      ranksDiv.appendChild(s);
    });
    boardRow.appendChild(ranksDiv);

    // 8x8 Squares Grid
    var gridDiv = document.createElement("div");
    gridDiv.className = "jv-cb-grid";

    var rIndices = isWhite ? [0, 1, 2, 3, 4, 5, 6, 7] : [7, 6, 5, 4, 3, 2, 1, 0];
    var cIndices = isWhite ? [0, 1, 2, 3, 4, 5, 6, 7] : [7, 6, 5, 4, 3, 2, 1, 0];

    rIndices.forEach(function (r) {
      cIndices.forEach(function (c) {
        var sq = document.createElement("div");
        var isLightSq = (r + c) % 2 === 0;
        var classes = ["jv-cb-sq", isLightSq ? "light" : "dark"];
        if (isEditMode) classes.push("editable");
        if (selectedSq && selectedSq.r === r && selectedSq.c === c) classes.push("selected");
        sq.className = classes.join(" ");

        var piece = currentGrid[r][c];
        if (piece && PIECES_SVG[piece]) {
          sq.innerHTML = PIECES_SVG[piece];
        }

        // Xử lý Click trên ô cờ trong chế độ chỉnh sửa (Edit Mode)
        if (isEditMode) {
          sq.addEventListener("click", function () {
            if (selectedTool === "erase") {
              currentGrid[r][c] = null;
              renderChessboard(container, null, perspective, {
                active: true,
                grid: currentGrid,
                turn: currentTurn,
                selectedTool: selectedTool,
                selectedSq: null,
                showFenDrawer: showFenDrawer
              });
            } else if (selectedTool === "move") {
              if (selectedSq) {
                if (selectedSq.r === r && selectedSq.c === c) {
                  // Bỏ chọn nếu click lại chính ô đó
                  selectedSq = null;
                } else {
                  // Di chuyển quân từ selectedSq sang ô mới
                  var movingPiece = currentGrid[selectedSq.r][selectedSq.c];
                  currentGrid[r][c] = movingPiece;
                  currentGrid[selectedSq.r][selectedSq.c] = null;
                  selectedSq = null;
                }
                renderChessboard(container, null, perspective, {
                  active: true,
                  grid: currentGrid,
                  turn: currentTurn,
                  selectedTool: selectedTool,
                  selectedSq: selectedSq,
                  showFenDrawer: showFenDrawer
                });
              } else {
                if (currentGrid[r][c]) {
                  // Chọn quân để di chuyển
                  renderChessboard(container, null, perspective, {
                    active: true,
                    grid: currentGrid,
                    turn: currentTurn,
                    selectedTool: selectedTool,
                    selectedSq: { r: r, c: c },
                    showFenDrawer: showFenDrawer
                  });
                }
              }
            } else if (PIECES_SVG[selectedTool]) {
              // Đặt quân cờ được chọn từ bảng Palette vào ô
              currentGrid[r][c] = selectedTool;
              renderChessboard(container, null, perspective, {
                active: true,
                grid: currentGrid,
                turn: currentTurn,
                selectedTool: selectedTool,
                selectedSq: null,
                showFenDrawer: showFenDrawer
              });
            }
          });
        }

        gridDiv.appendChild(sq);
      });
    });
    boardRow.appendChild(gridDiv);
    boardBox.appendChild(boardRow);

    // Files (a-h)
    var filesDiv = document.createElement("div");
    filesDiv.className = "jv-cb-files";
    var fileLabels = isWhite ? ["a", "b", "c", "d", "e", "f", "g", "h"] : ["h", "g", "f", "e", "d", "c", "b", "a"];
    fileLabels.forEach(function (fl) {
      var s = document.createElement("span");
      s.textContent = fl;
      filesDiv.appendChild(s);
    });
    boardBox.appendChild(filesDiv);

    wrap.appendChild(boardBox);

    // Bảng chọn quân cờ khi ở Chế độ Xếp cờ (Piece Palette)
    if (isEditMode) {
      var paletteWrap = document.createElement("div");
      paletteWrap.className = "jv-cb-palette-wrap";

      // Hàng quân Trắng
      var whiteRow = document.createElement("div");
      whiteRow.className = "jv-cb-palette-row";
      var whiteTitle = document.createElement("span");
      whiteTitle.className = "jv-cb-palette-title";
      whiteTitle.textContent = "Trắng:";
      whiteRow.appendChild(whiteTitle);

      ["K", "Q", "R", "B", "N", "P"].forEach(function (pc) {
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "jv-cb-tool-btn" + (selectedTool === pc ? " active" : "");
        btn.innerHTML = PIECES_SVG[pc];
        btn.title = "Đặt quân Trắng: " + pc;
        btn.addEventListener("click", function () {
          renderChessboard(container, null, perspective, {
            active: true,
            grid: currentGrid,
            turn: currentTurn,
            selectedTool: pc,
            selectedSq: null,
            showFenDrawer: showFenDrawer
          });
        });
        whiteRow.appendChild(btn);
      });
      paletteWrap.appendChild(whiteRow);

      // Hàng quân Đen
      var blackRow = document.createElement("div");
      blackRow.className = "jv-cb-palette-row";
      var blackTitle = document.createElement("span");
      blackTitle.className = "jv-cb-palette-title";
      blackTitle.textContent = "Đen:";
      blackRow.appendChild(blackTitle);

      ["k", "q", "r", "b", "n", "p"].forEach(function (pc) {
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "jv-cb-tool-btn" + (selectedTool === pc ? " active" : "");
        btn.innerHTML = PIECES_SVG[pc];
        btn.title = "Đặt quân Đen: " + pc;
        btn.addEventListener("click", function () {
          renderChessboard(container, null, perspective, {
            active: true,
            grid: currentGrid,
            turn: currentTurn,
            selectedTool: pc,
            selectedSq: null,
            showFenDrawer: showFenDrawer
          });
        });
        blackRow.appendChild(btn);
      });
      paletteWrap.appendChild(blackRow);

      // Hàng Công cụ (Di chuyển, Xóa ô, Chọn lượt đi)
      var toolsRow = document.createElement("div");
      toolsRow.className = "jv-cb-palette-row";
      var toolsTitle = document.createElement("span");
      toolsTitle.className = "jv-cb-palette-title";
      toolsTitle.textContent = "Công cụ:";
      toolsRow.appendChild(toolsTitle);

      // Nút Di chuyển
      var btnMove = document.createElement("button");
      btnMove.type = "button";
      btnMove.className = "jv-cb-btn" + (selectedTool === "move" ? " active" : "");
      btnMove.innerHTML = "✋ Di chuyển";
      btnMove.title = "Bấm vào quân rồi bấm ô đích để chuyển";
      btnMove.addEventListener("click", function () {
        renderChessboard(container, null, perspective, {
          active: true,
          grid: currentGrid,
          turn: currentTurn,
          selectedTool: "move",
          selectedSq: null,
          showFenDrawer: showFenDrawer
        });
      });
      toolsRow.appendChild(btnMove);

      // Nút Xóa ô
      var btnErase = document.createElement("button");
      btnErase.type = "button";
      btnErase.className = "jv-cb-btn" + (selectedTool === "erase" ? " active" : "");
      btnErase.innerHTML = "🗑️ Xóa ô";
      btnErase.title = "Bấm vào ô để xóa quân cờ";
      btnErase.addEventListener("click", function () {
        renderChessboard(container, null, perspective, {
          active: true,
          grid: currentGrid,
          turn: currentTurn,
          selectedTool: "erase",
          selectedSq: null,
          showFenDrawer: showFenDrawer
        });
      });
      toolsRow.appendChild(btnErase);

      // Đổi lượt đi (Trắng / Đen)
      var btnToggleTurn = document.createElement("button");
      btnToggleTurn.type = "button";
      btnToggleTurn.className = "jv-cb-btn";
      btnToggleTurn.innerHTML = isWhiteTurn ? "⚪ Lượt: Trắng" : "⚫ Lượt: Đen";
      btnToggleTurn.title = "Đổi bên đi tiếp theo";
      btnToggleTurn.addEventListener("click", function () {
        var nextTurn = isWhiteTurn ? "b" : "w";
        renderChessboard(container, null, perspective, {
          active: true,
          grid: currentGrid,
          turn: nextTurn,
          selectedTool: selectedTool,
          selectedSq: selectedSq,
          showFenDrawer: showFenDrawer
        });
      });
      toolsRow.appendChild(btnToggleTurn);

      // Khởi tạo nhanh (Ban đầu / Xóa sạch)
      var btnStartPos = document.createElement("button");
      btnStartPos.type = "button";
      btnStartPos.className = "jv-cb-btn";
      btnStartPos.innerHTML = "⚡ Ban đầu";
      btnStartPos.title = "Đặt lại bàn cờ thi đấu tiêu chuẩn";
      btnStartPos.addEventListener("click", function () {
        var def = parseFen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
        renderChessboard(container, null, perspective, {
          active: true,
          grid: def.grid,
          turn: "w",
          selectedTool: selectedTool,
          selectedSq: null,
          showFenDrawer: showFenDrawer
        });
      });
      toolsRow.appendChild(btnStartPos);

      var btnClearAll = document.createElement("button");
      btnClearAll.type = "button";
      btnClearAll.className = "jv-cb-btn";
      btnClearAll.innerHTML = "🧹 Xóa trắng";
      btnClearAll.title = "Xóa toàn bộ quân cờ trên bàn";
      btnClearAll.addEventListener("click", function () {
        var emptyGrid = [];
        for (var i = 0; i < 8; i++) emptyGrid.push([null,null,null,null,null,null,null,null]);
        renderChessboard(container, null, perspective, {
          active: true,
          grid: emptyGrid,
          turn: currentTurn,
          selectedTool: selectedTool,
          selectedSq: null,
          showFenDrawer: showFenDrawer
        });
      });
      toolsRow.appendChild(btnClearAll);

      paletteWrap.appendChild(toolsRow);
      wrap.appendChild(paletteWrap);
    }

    // Drawer Xem & Sửa FEN trực tiếp
    if (showFenDrawer) {
      var fenDrawer = document.createElement("div");
      fenDrawer.className = "jv-cb-fen-drawer";

      var fenRow = document.createElement("div");
      fenRow.className = "jv-cb-fen-input-row";

      var fenInput = document.createElement("input");
      fenInput.className = "jv-cb-fen-input";
      fenInput.type = "text";
      fenInput.value = currentFen;
      fenInput.placeholder = "Dán hoặc nhập chuỗi FEN tại đây...";
      fenRow.appendChild(fenInput);

      var btnApplyFen = document.createElement("button");
      btnApplyFen.className = "jv-cb-btn btn-save";
      btnApplyFen.type = "button";
      btnApplyFen.innerHTML = "✓ Áp dụng";
      btnApplyFen.addEventListener("click", function () {
        var val = fenInput.value.trim();
        var v = validateFen(val);
        if (!v.valid) {
          errDiv.textContent = "⚠️ " + v.error;
          errDiv.style.display = "block";
          return;
        }
        container.setAttribute("data-fen", val);
        renderChessboard(container, val, perspective, {
          active: false,
          showFenDrawer: false
        });
      });
      fenRow.appendChild(btnApplyFen);
      fenDrawer.appendChild(fenRow);

      var errDiv = document.createElement("div");
      errDiv.className = "jv-cb-fen-err";
      errDiv.style.display = "none";
      fenDrawer.appendChild(errDiv);

      wrap.appendChild(fenDrawer);
    }

    // Action Toolbar (Flip, Copy, Sửa thế cờ, Xem FEN, Lichess)
    var actions = document.createElement("div");
    actions.className = "jv-cb-actions";

    if (isEditMode) {
      // Nút Lưu & Chuẩn hóa
      var btnSaveEdit = document.createElement("button");
      btnSaveEdit.className = "jv-cb-btn btn-save";
      btnSaveEdit.type = "button";
      btnSaveEdit.innerHTML = "💾 Lưu & Chuẩn hóa";
      btnSaveEdit.title = "Lưu lại thế cờ đã xếp";
      btnSaveEdit.addEventListener("click", function () {
        var newFen = buildFen(currentGrid, currentTurn);
        container.setAttribute("data-fen", newFen);
        renderChessboard(container, newFen, perspective, { active: false });
      });
      actions.appendChild(btnSaveEdit);

      // Nút Hủy / Đóng chế độ xếp cờ
      var btnCancelEdit = document.createElement("button");
      btnCancelEdit.className = "jv-cb-btn";
      btnCancelEdit.type = "button";
      btnCancelEdit.innerHTML = "❌ Hủy";
      btnCancelEdit.title = "Đóng chế độ xếp cờ";
      btnCancelEdit.addEventListener("click", function () {
        renderChessboard(container, fen, perspective, { active: false });
      });
      actions.appendChild(btnCancelEdit);
    } else {
      // Nút lật bàn cờ
      var btnFlip = document.createElement("button");
      btnFlip.className = "jv-cb-btn";
      btnFlip.type = "button";
      btnFlip.innerHTML = "🔄 Đổi góc nhìn";
      btnFlip.title = "Đảo góc nhìn Trắng / Đen";
      btnFlip.addEventListener("click", function () {
        var nextPersp = isWhite ? "black" : "white";
        container.setAttribute("data-perspective", nextPersp);
        renderChessboard(container, fen, nextPersp);
      });
      actions.appendChild(btnFlip);

      // Nút Bật/Tắt chế độ Xếp cờ (Board Editor)
      var btnEditBoard = document.createElement("button");
      btnEditBoard.className = "jv-cb-btn";
      btnEditBoard.type = "button";
      btnEditBoard.innerHTML = "✏️ Xếp / Sửa cờ";
      btnEditBoard.title = "Di chuyển, thêm hoặc xóa quân cờ trực quan";
      btnEditBoard.addEventListener("click", function () {
        var parsed = parseFen(fen);
        renderChessboard(container, null, perspective, {
          active: true,
          grid: parsed.grid,
          turn: parsed.turn,
          selectedTool: "move",
          selectedSq: null,
          showFenDrawer: false
        });
      });
      actions.appendChild(btnEditBoard);

      // Nút Xem / Sửa FEN
      var btnToggleFen = document.createElement("button");
      btnToggleFen.className = "jv-cb-btn" + (showFenDrawer ? " active" : "");
      btnToggleFen.type = "button";
      btnToggleFen.innerHTML = "📝 Xem / Sửa FEN";
      btnToggleFen.title = "Xem hoặc dán mã FEN trực tiếp";
      btnToggleFen.addEventListener("click", function () {
        renderChessboard(container, fen, perspective, {
          active: false,
          showFenDrawer: !showFenDrawer
        });
      });
      actions.appendChild(btnToggleFen);

      // Nút copy FEN
      var btnCopy = document.createElement("button");
      btnCopy.className = "jv-cb-btn";
      btnCopy.type = "button";
      btnCopy.innerHTML = "📋 Copy FEN";
      btnCopy.title = "Sao chép mã FEN vào bộ nhớ đệm";
      btnCopy.addEventListener("click", function () {
        if (navigator.clipboard) {
          navigator.clipboard.writeText(currentFen).then(function () {
            btnCopy.innerHTML = "✓ Đã chép!";
            setTimeout(function () { btnCopy.innerHTML = "📋 Copy FEN"; }, 2000);
          });
        }
      });
      actions.appendChild(btnCopy);

      // Nút Mở Lichess Analysis (GIỮ NGUYÊN DẤU / ĐỂ LICHESS PHÂN TÍCH ĐÚNG THẾ CỜ)
      var cleanFen = String(currentFen || "").trim().replace(/\s+/g, "_");
      var btnLichess = document.createElement("a");
      btnLichess.className = "jv-cb-btn";
      btnLichess.href = "https://lichess.org/analysis/fromPosition/" + cleanFen;
      btnLichess.target = "_blank";
      btnLichess.rel = "noopener noreferrer";
      btnLichess.innerHTML = "↗ Mở Lichess";
      btnLichess.title = "Phân tích thế cờ này trên Lichess";
      actions.appendChild(btnLichess);
    }

    wrap.appendChild(actions);

    container.innerHTML = "";
    container.appendChild(wrap);
  }

  // Quét và kích hoạt toàn bộ các thẻ .jv-chessboard trên trang
  function scanAndInitChessboards() {
    if (typeof document === "undefined") return;
    injectStyles();
    var elements = document.querySelectorAll(".jv-chessboard:not([data-cb-inited])");
    elements.forEach(function (el) {
      el.setAttribute("data-cb-inited", "true");
      var fen = el.getAttribute("data-fen") || el.textContent.trim();
      renderChessboard(el, fen);
    });
  }

  // Khởi động MutationObserver để tự động nhận diện bàn cờ khi tin nhắn chat mới xuất hiện
  if (typeof document !== "undefined") {
    injectStyles();
    document.addEventListener("DOMContentLoaded", scanAndInitChessboards);
    if (typeof MutationObserver !== "undefined") {
      var observer = new MutationObserver(function () {
        scanAndInitChessboards();
      });
      observer.observe(document.body, { childList: true, subtree: true });
    }
  }

  // Xuất ra phạm vi toàn cục cho Javis
  if (typeof window !== "undefined") {
    window.JavisChess = {
      parseFen: parseFen,
      buildFen: buildFen,
      validateFen: validateFen,
      renderChessboard: renderChessboard,
      scanAndInit: scanAndInitChessboards,
      PIECES_SVG: PIECES_SVG
    };
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = {
      parseFen: parseFen,
      buildFen: buildFen,
      validateFen: validateFen,
      PIECES_SVG: PIECES_SVG
    };
  }
})();
