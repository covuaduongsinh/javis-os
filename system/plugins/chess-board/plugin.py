"""
Plugin Chess Board: Hiển thị & render bàn cờ trực quan (ASCII, Markdown, SVG).
"""
from __future__ import annotations

import json
import os
import sys

_SERVER_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "server"))
if _SERVER_DIR not in sys.path:
    sys.path.insert(0, _SERVER_DIR)

from chess_core.renderer import render_board_ascii, render_board_svg


def _handle_render_board(args: dict, ctx) -> str:
    args = args or {}
    fen = args.get("fen", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    perspective = args.get("perspective", "white")
    fmt = args.get("format", "ascii")

    if fmt == "svg":
        svg_str = render_board_svg(fen, last_move=args.get("last_move"))
        return svg_str
    
    board_text = render_board_ascii(fen, perspective=perspective)
    fen_block = f"```fen\n{fen}\n```"
    return json.dumps({
        "fen": fen,
        "perspective": perspective,
        "fen_block": fen_block,
        "board_display": board_text
    }, ensure_ascii=False)


def register(ctx):
    ctx.register_tool(
        name="chess_render_board",
        description=(
            "Vẽ và hiển thị hình ảnh bàn cờ trực quan (ASCII / Markdown / SVG) từ mã FEN để học viên và HLV nhìn rõ thế cờ."
        ),
        handler=_handle_render_board,
        min_mode="readonly",
        schema={
            "type": "object",
            "properties": {
                "fen": {"type": "string", "description": "Mã FEN của bàn cờ"},
                "perspective": {"type": "string", "description": "'white' (Trắng nhìn lên) hoặc 'black' (Đen nhìn lên)"},
                "format": {"type": "string", "description": "'ascii' (mặc định) hoặc 'svg'"},
                "last_move": {"type": "string", "description": "Nước đi vừa đi (dạng UCI, vd e2e4) để highlight"},
            },
            "required": ["fen"],
        },
    )
