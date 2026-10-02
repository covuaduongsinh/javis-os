/* chess-board-ui.js - Component Bàn Cờ Trực Quan Sắc Nét cho Javis OS (Cờ Vua Dương Sinh)
   Thuần SVG/CSS/JS, không phụ thuộc CDN, hỗ trợ Light/Dark mode, lật bàn cờ, copy FEN,
   mở Lichess Analysis và phân tích trực tiếp với Javis.
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

  // CSS Stylesheet tự động gắn cho bàn cờ
  var CHESS_CSS = `
    .jv-cb-wrap {
      display: inline-block;
      margin: 12px 0;
      padding: 10px;
      background: var(--bg-card, #ffffff);
      border: 1px solid var(--border-color, #e2e8f0);
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.06);
      max-width: 100%;
      font-family: inherit;
    }
    .dark .jv-cb-wrap {
      background: #1e293b;
      border-color: #334155;
      box-shadow: 0 4px 12px rgba(0,0,0,0.25);
    }
    .jv-cb-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 8px;
      font-size: 13px;
      font-weight: 600;
      color: var(--text-color, #1e293b);
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
    }
    .dark .jv-cb-badge { background: #334155; color: #cbd5e1; }
    .jv-cb-board-container {
      display: grid;
      grid-template-columns: 20px auto;
      grid-template-rows: auto 20px;
      gap: 2px;
    }
    .jv-cb-ranks {
      display: flex;
      flex-direction: column;
      justify-content: space-around;
      align-items: center;
      font-size: 11px;
      font-weight: bold;
      color: #64748b;
    }
    .jv-cb-files {
      grid-column: 2;
      display: flex;
      justify-content: space-around;
      font-size: 11px;
      font-weight: bold;
      color: #64748b;
      padding-top: 2px;
    }
    .jv-cb-grid {
      grid-column: 2;
      display: grid;
      grid-template-columns: repeat(8, minmax(28px, 42px));
      grid-template-rows: repeat(8, minmax(28px, 42px));
      border: 2px solid #475569;
      border-radius: 4px;
      overflow: hidden;
      aspect-ratio: 1 / 1;
    }
    .jv-cb-sq {
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      user-select: none;
    }
    .jv-cb-sq.light { background-color: #f0d9b5; }
    .jv-cb-sq.dark { background-color: #b58863; }
    .jv-cb-sq svg {
      width: 85%;
      height: 85%;
      filter: drop-shadow(0 1px 2px rgba(0,0,0,0.2));
    }
    .jv-cb-actions {
      display: flex;
      gap: 6px;
      margin-top: 10px;
      flex-wrap: wrap;
    }
    .jv-cb-btn {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      padding: 4px 10px;
      background: var(--bg-subtle, #f1f5f9);
      border: 1px solid var(--border-color, #cbd5e1);
      border-radius: 6px;
      font-size: 12px;
      color: var(--text-color, #334155);
      cursor: pointer;
      transition: all 0.15s ease;
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
      ep: ep
    };
  }

  // Tạo cây DOM bàn cờ
  function renderChessboard(container, fen, perspective) {
    if (!container) return;
    perspective = perspective || container.getAttribute("data-perspective") || "white";
    var data = parseFen(fen);
    var isWhite = perspective.toLowerCase() !== "black";

    var wrap = document.createElement("div");
    wrap.className = "jv-cb-wrap";

    // Header & Turn badge
    var turnText = data.isWhiteTurn ? "⚪ Trắng đi (White)" : "⚫ Đen đi (Black)";
    var header = document.createElement("div");
    header.className = "jv-cb-header";
    header.innerHTML = `
      <span>♟ Bàn cờ Thế trận</span>
      <span class="jv-cb-badge">${turnText}</span>
    `;
    wrap.appendChild(header);

    // Board Container (Coordinates + 8x8 Grid)
    var boardContainer = document.createElement("div");
    boardContainer.className = "jv-cb-board-container";

    // Ranks (1-8)
    var ranksDiv = document.createElement("div");
    ranksDiv.className = "jv-cb-ranks";
    var rankLabels = isWhite ? [8, 7, 6, 5, 4, 3, 2, 1] : [1, 2, 3, 4, 5, 6, 7, 8];
    rankLabels.forEach(function (rk) {
      var s = document.createElement("span");
      s.textContent = rk;
      ranksDiv.appendChild(s);
    });
    boardContainer.appendChild(ranksDiv);

    // 8x8 Squares Grid
    var gridDiv = document.createElement("div");
    gridDiv.className = "jv-cb-grid";

    var rIndices = isWhite ? [0, 1, 2, 3, 4, 5, 6, 7] : [7, 6, 5, 4, 3, 2, 1, 0];
    var cIndices = isWhite ? [0, 1, 2, 3, 4, 5, 6, 7] : [7, 6, 5, 4, 3, 2, 1, 0];

    rIndices.forEach(function (r) {
      cIndices.forEach(function (c) {
        var sq = document.createElement("div");
        var isLightSq = (r + c) % 2 === 0;
        sq.className = "jv-cb-sq " + (isLightSq ? "light" : "dark");

        var piece = data.grid[r][c];
        if (piece && PIECES_SVG[piece]) {
          sq.innerHTML = PIECES_SVG[piece];
        }
        gridDiv.appendChild(sq);
      });
    });
    boardContainer.appendChild(gridDiv);

    // Files (a-h)
    var filesDiv = document.createElement("div");
    filesDiv.className = "jv-cb-files";
    var fileLabels = isWhite ? ["a", "b", "c", "d", "e", "f", "g", "h"] : ["h", "g", "f", "e", "d", "c", "b", "a"];
    fileLabels.forEach(function (fl) {
      var s = document.createElement("span");
      s.textContent = fl;
      filesDiv.appendChild(s);
    });
    boardContainer.appendChild(filesDiv);

    wrap.appendChild(boardContainer);

    // Action Toolbar (Flip, Copy, Analyze, Lichess)
    var actions = document.createElement("div");
    actions.className = "jv-cb-actions";

    // Nút lật bàn cờ
    var btnFlip = document.createElement("button");
    btnFlip.className = "jv-cb-btn";
    btnFlip.type = "button";
    btnFlip.innerHTML = "🔄 Đổi góc nhìn";
    btnFlip.title = "Đảo góc nhìn Trắng / Đen";
    btnFlip.addEventListener("click", function () {
      var nextPersp = isWhite ? "black" : "white";
      container.setAttribute("data-perspective", nextPersp);
      container.innerHTML = "";
      renderChessboard(container, data.fen, nextPersp);
    });
    actions.appendChild(btnFlip);

    // Nút copy FEN
    var btnCopy = document.createElement("button");
    btnCopy.className = "jv-cb-btn";
    btnCopy.type = "button";
    btnCopy.innerHTML = "📋 Copy FEN";
    btnCopy.title = "Sao chép mã FEN";
    btnCopy.addEventListener("click", function () {
      if (navigator.clipboard) {
        navigator.clipboard.writeText(data.fen).then(function () {
          btnCopy.innerHTML = "✓ Đã chép!";
          setTimeout(function () { btnCopy.innerHTML = "📋 Copy FEN"; }, 2000);
        });
      }
    });
    actions.appendChild(btnCopy);

    // Nút Mở Lichess Analysis
    var btnLichess = document.createElement("a");
    btnLichess.className = "jv-cb-btn";
    btnLichess.href = "https://lichess.org/analysis/" + encodeURIComponent(data.fen.replace(/\s+/g, "_"));
    btnLichess.target = "_blank";
    btnLichess.rel = "noopener noreferrer";
    btnLichess.innerHTML = "↗ Mở Lichess";
    btnLichess.title = "Phân tích trên Lichess";
    actions.appendChild(btnLichess);

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
      renderChessboard: renderChessboard,
      scanAndInit: scanAndInitChessboards,
      PIECES_SVG: PIECES_SVG
    };
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { parseFen: parseFen, PIECES_SVG: PIECES_SVG };
  }
})();
