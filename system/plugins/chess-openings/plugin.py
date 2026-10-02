"""
Plugin Chess Openings: Tra cứu khai cuộc ECO và Grandmasters Explorer.
"""
from __future__ import annotations

import json
import os
import sys

_SERVER_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "server"))
if _SERVER_DIR not in sys.path:
    sys.path.insert(0, _SERVER_DIR)

from chess_core.openings import get_opening_info


def _handle_openings(args: dict, ctx) -> str:
    args = args or {}
    moves_or_fen = args.get("fen") or args.get("moves") or "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    res = get_opening_info(moves_or_fen)
    return json.dumps(res, ensure_ascii=False)


def register(ctx):
    ctx.register_tool(
        name="chess_openings",
        description=(
            "Tra cứu bách khoa toàn thư khai cuộc ECO & thống kê ván đấu của các Đại kiện tướng (Lichess Masters Explorer). "
            "Trả về tên khai cuộc, mã ECO, tỷ lệ Thắng/Hòa/Thua và các nước đi phổ biến nhất của Grandmasters."
        ),
        handler=_handle_openings,
        min_mode="readonly",
        schema={
            "type": "object",
            "properties": {
                "fen": {"type": "string", "description": "Mã FEN thế cờ khai cuộc"},
                "moves": {"type": "string", "description": "Chuỗi nước đi khai cuộc, vd: 'e4 c5 Nf3 d6'"},
            },
        },
    )
