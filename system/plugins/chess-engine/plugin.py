"""
Plugin Chess Engine: Đánh giá thế cờ (Stockfish Cloud, Syzygy Tablebase) & Phân tích ván đấu PGN.
"""
from __future__ import annotations

import json
import os
import sys

_SERVER_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "server"))
if _SERVER_DIR not in sys.path:
    sys.path.insert(0, _SERVER_DIR)

from chess_core.evaluator import evaluate_fen, analyze_game, check_tablebase
from chess_core.renderer import render_board_ascii


def _handle_eval(args: dict, ctx) -> str:
    args = args or {}
    fen = args.get("fen")
    pgn = args.get("pgn")
    multi_pv = int(args.get("multi_pv", 3))

    if pgn and not fen:
        res = analyze_game(pgn)
        return json.dumps(res, ensure_ascii=False)

    if not fen:
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    res = evaluate_fen(fen, multi_pv=multi_pv)
    res["board_ascii"] = render_board_ascii(fen)
    return json.dumps(res, ensure_ascii=False)


def _handle_game_analyze(args: dict, ctx) -> str:
    args = args or {}
    pgn = args.get("pgn", "")
    max_moves = int(args.get("max_moves", 50))
    if not pgn:
        return json.dumps({"error": "Vui lòng cung cấp nội dung ván đấu dạng chuỗi PGN (pgn)."}, ensure_ascii=False)
    res = analyze_game(pgn, max_moves_to_eval=max_moves)
    return json.dumps(res, ensure_ascii=False)


def _handle_tablebase(args: dict, ctx) -> str:
    args = args or {}
    fen = args.get("fen", "")
    if not fen:
        return json.dumps({"error": "Vui lòng cung cấp mã FEN cờ tàn (tối đa 7 quân)."}, ensure_ascii=False)
    
    res = check_tablebase(fen)
    if not res:
        return json.dumps({"error": "Thế cờ có nhiều hơn 7 quân hoặc không thể tra cứu Syzygy Tablebase."}, ensure_ascii=False)
    return json.dumps(res, ensure_ascii=False)


def register(ctx):
    ctx.register_tool(
        name="chess_eval",
        description=(
            "Đánh giá thế cờ chuyên sâu bằng Stockfish & Cloud Eval: điểm số (centipawns/mate in X), "
            "nước đi tối ưu (best lines), biến thể gợi ý và hiển thị bàn cờ ASCII. Nhận đầu vào FEN hoặc PGN."
        ),
        handler=_handle_eval,
        min_mode="readonly",
        schema={
            "type": "object",
            "properties": {
                "fen": {"type": "string", "description": "Mã FEN thế cờ cần phân tích"},
                "pgn": {"type": "string", "description": "Chuỗi PGN nếu muốn phân tích cả ván"},
                "multi_pv": {"type": "integer", "description": "Số lượng biến tối ưu muốn xem (mặc định 3)"},
            },
        },
    )

    ctx.register_tool(
        name="chess_game_analyze",
        description=(
            "Phân tích toàn bộ ván đấu từ chuỗi PGN: phát hiện lỗi Blunder (nghiêm trọng), Mistake (sai sót), "
            "Inaccuracy (thiếu chính xác), tính điểm ACPL và độ chính xác (Accuracy %) cho cả Trắng và Đen."
        ),
        handler=_handle_game_analyze,
        min_mode="readonly",
        schema={
            "type": "object",
            "properties": {
                "pgn": {"type": "string", "description": "Nội dung ván đấu định dạng PGN"},
                "max_moves": {"type": "integer", "description": "Số nước đi tối đa cần phân tích (mặc định 50)"},
            },
            "required": ["pgn"],
        },
    )

    ctx.register_tool(
        name="chess_tablebase",
        description=(
            "Tra cứu kết quả cờ tàn 7 quân tuyệt đối (Syzygy Endgame Tablebase): xác định Thắng/Hòa/Thua lý thuyết 100% "
            "và số nước đến chiếu hết (DTM) cùng các nước đi tối ưu."
        ),
        handler=_handle_tablebase,
        min_mode="readonly",
        schema={
            "type": "object",
            "properties": {
                "fen": {"type": "string", "description": "Mã FEN cờ tàn (<= 7 quân)"},
            },
            "required": ["fen"],
        },
    )
