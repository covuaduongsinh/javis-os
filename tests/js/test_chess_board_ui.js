// test_chess_board_ui.js - Kiểm tra component hiển thị bàn cờ FEN
var assert = require("assert");
var chessBoard = require("../../dashboard/chess-board-ui.js");

console.log("--- Bắt đầu test Chess Board UI ---");

// Test 1: parseFen thế cờ ban đầu
var startFen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
var parsed1 = chessBoard.parseFen(startFen);
assert.strictEqual(parsed1.turn, "w", "Lượt đi phải là Trắng (w)");
assert.strictEqual(parsed1.board[0][0], "r", "Góc a8 phải là Xe đen (r)");
assert.strictEqual(parsed1.board[7][4], "K", "Ô e1 phải là Vua trắng (K)");
assert.strictEqual(parsed1.board[3][3], null, "Ô d5 phải rỗng");
console.log("ok   parseFen thế cờ ban đầu chính xác");

// Test 2: parseFen thế cờ tùy chỉnh
var customFen = "r1bqkb1r/pppp1ppp/2n5/4p3/2B1n3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 5";
var parsed2 = chessBoard.parseFen(customFen);
assert.strictEqual(parsed2.turn, "w");
assert.strictEqual(parsed2.board[4][4], "n", "Ô e4 phải là Mã đen (n)");
assert.strictEqual(parsed2.board[4][2], "B", "Ô c4 phải là Tượng trắng (B)");
console.log("ok   parseFen thế cờ phức tạp chính xác");

// Test 3: Bộ SVG đầy đủ cho cả 12 quân cờ
var pieces = ["P", "N", "B", "R", "Q", "K", "p", "n", "b", "r", "q", "k"];
pieces.forEach(function (p) {
  assert.ok(chessBoard.PIECES_SVG[p], "Thiếu SVG cho quân " + p);
  assert.ok(chessBoard.PIECES_SVG[p].indexOf("<svg") >= 0, "SVG của " + p + " phải hợp lệ");
});
console.log("ok   Bộ SVG 12 quân cờ đầy đủ và hợp lệ");

console.log("\nALL CHESS BOARD UI TESTS PASSED!");
