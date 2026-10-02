"""
Plugin Chess Puzzles: Sinh bài tập chiến thuật theo chủ đề & trích xuất bài tập sửa lỗi từ ván đấu.
"""
from __future__ import annotations

import json
import os
import sys

_SERVER_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "server"))
if _SERVER_DIR not in sys.path:
    sys.path.insert(0, _SERVER_DIR)

from chess_core.puzzles import get_tactical_puzzles, extract_blunder_puzzles


def _handle_puzzles(args: dict, ctx) -> str:
    args = args or {}
    theme = args.get("theme", "")
    min_rating = int(args.get("min_rating", 1000))
    max_rating = int(args.get("max_rating", 2000))
    count = int(args.get("count", 3))

    pgn = args.get("pgn")
    if pgn:
        res = extract_blunder_puzzles(pgn, target_player=args.get("player", ""))
    else:
        res = get_tactical_puzzles(theme=theme, min_rating=min_rating, max_rating=max_rating, count=count)

    return json.dumps(res, ensure_ascii=False)


def register(ctx):
    ctx.register_tool(
        name="chess_puzzles",
        description=(
            "Tìm bài tập chiến thuật theo chủ đề (pin/ghim, fork/bắt đôi, skewer/xiên, deflection, mateIn1, mateIn2, endgame...) "
            "theo mức Elo, hoặc tự động trích xuất bài tập sửa sai từ ván cờ (PGN) của học viên."
        ),
        handler=_handle_puzzles,
        min_mode="readonly",
        schema={
            "type": "object",
            "properties": {
                "theme": {"type": "string", "description": "Chủ đề chiến thuật: pin, fork, skewer, mateIn1, mateIn2, endgame..."},
                "min_rating": {"type": "integer", "description": "Rating tối thiểu (mặc định 1000)"},
                "max_rating": {"type": "integer", "description": "Rating tối đa (mặc định 2000)"},
                "count": {"type": "integer", "description": "Số lượng bài tập (mặc định 3)"},
                "pgn": {"type": "string", "description": "Chuỗi PGN ván cờ học viên nếu muốn trích bài tập sửa lỗi"},
                "player": {"type": "string", "description": "Tên học viên trong PGN nếu trích bài tập"},
            },
        },
    )
