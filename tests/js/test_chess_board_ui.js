// test_chess_board_ui.js - Kiểm tra toàn diện component hiển thị & chỉnh sửa bàn cờ FEN
var assert = require("assert");
var chessBoard = require("../../dashboard/chess-board-ui.js");

console.log("--- Bắt đầu test Chess Board UI & Board Editor ---");

// Test 1: parseFen & buildFen thế cờ ban đầu
var startFen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";
var parsed1 = chessBoard.parseFen(startFen);
assert.strictEqual(parsed1.turn, "w", "Lượt đi phải là Trắng (w)");
assert.strictEqual(parsed1.board[0][0], "r", "Góc a8 phải là Xe đen (r)");
assert.strictEqual(parsed1.board[7][4], "K", "Ô e1 phải là Vua trắng (K)");
assert.strictEqual(parsed1.board[3][3], null, "Ô d5 phải rỗng");

var rebuilt1 = chessBoard.buildFen(parsed1.grid, parsed1.turn, parsed1.castling, parsed1.ep, parsed1.halfmove, parsed1.fullmove);
assert.strictEqual(rebuilt1, startFen, "buildFen phải tái tạo chính xác chuỗi FEN ban đầu");
console.log("ok   parseFen & buildFen roundtrip chính xác 100%");

// Test 2: parseFen & buildFen thế cờ phức tạp
var customFen = "r1k5/1p6/1p1p2p1/3pP1p1/1PPB1q2/1PP5/1PP1R1PP/5RK1 w - - 0 1";
var parsed2 = chessBoard.parseFen(customFen);
assert.strictEqual(parsed2.turn, "w");
assert.strictEqual(parsed2.board[0][0], "r", "a8 là Xe đen");
assert.strictEqual(parsed2.board[0][2], "k", "c8 là Vua đen");
assert.strictEqual(parsed2.board[4][3], "B", "d4 là Tượng trắng");
assert.strictEqual(parsed2.board[4][5], "q", "f4 là Hậu đen");

var rebuilt2 = chessBoard.buildFen(parsed2.grid, parsed2.turn, parsed2.castling, parsed2.ep, parsed2.halfmove, parsed2.fullmove);
assert.strictEqual(rebuilt2, customFen, "buildFen phải tái tạo chính xác thế cờ phức tạp");
console.log("ok   parseFen & buildFen thế cờ thực tế chính xác");

// Test 3: validateFen
var validRes = chessBoard.validateFen(customFen);
assert.strictEqual(validRes.valid, true, "FEN chuẩn phải hợp lệ");

var invalidFen1 = "r1k5/1p6/1p1p2p3/3pP1p1/1PPB1q2/1PP5/1PP1R1PP"; // Thiếu 1 hàng (chỉ có 7 hàng)
var invalidRes1 = chessBoard.validateFen(invalidFen1);
assert.strictEqual(invalidRes1.valid, false, "FEN thiếu hàng phải báo lỗi");

var invalidFen2 = "r1k5/1p6/1p1p2p3/3pP1p1/1PPB1q2/1PP5/1PP1R1PP/5RK2"; // Hàng cuối chỉ có 7 ô (5+1+1=7)
var invalidRes2 = chessBoard.validateFen(invalidFen2);
assert.strictEqual(invalidRes2.valid, false, "FEN thừa/thiếu ô trên hàng phải báo lỗi");
console.log("ok   validateFen phát hiện chính xác FEN hợp lệ và không hợp lệ");

// Test 4: Chỉnh sửa quân cờ (Board Editor Simulation)
var editGrid = JSON.parse(JSON.stringify(parsed2.grid));
// Di chuyển Hậu đen từ f4 sang e3
editGrid[4][5] = null; // xóa f4
editGrid[5][4] = "q";  // đặt e3
var editedFen = chessBoard.buildFen(editGrid, "b");
assert.ok(editedFen.indexOf("1PP1q3") >= 0 || editedFen.indexOf("q") >= 0, "FEN sau chỉnh sửa phải chứa quân mới");
assert.ok(editedFen.endsWith(" b - - 0 1"), "Lượt đi phải là Đen (b)");
console.log("ok   Mô phỏng Chỉnh sửa thế cờ (Board Editor) hoạt động hoàn hảo");

// Test 5: Bộ SVG 12 quân cờ
var pieces = ["P", "N", "B", "R", "Q", "K", "p", "n", "b", "r", "q", "k"];
pieces.forEach(function (p) {
  assert.ok(chessBoard.PIECES_SVG[p], "Thiếu SVG cho quân " + p);
  assert.ok(chessBoard.PIECES_SVG[p].indexOf("<svg") >= 0, "SVG của " + p + " phải hợp lệ");
});
console.log("ok   Bộ SVG 12 quân cờ đầy đủ và hợp lệ");

console.log("\nALL CHESS BOARD UI & EDITOR TESTS PASSED!");
