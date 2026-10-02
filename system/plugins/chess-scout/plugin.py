"""
Plugin Chess Scout: Trinh sát đối thủ & phân tích phong cách kỳ thủ qua Lichess / Chess.com.
"""
from __future__ import annotations

import json
import os
import sys

_SERVER_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "server"))
if _SERVER_DIR not in sys.path:
    sys.path.insert(0, _SERVER_DIR)

from chess_core.scout import scout_player_profile


def _handle_player_scout(args: dict, ctx) -> str:
    args = args or {}
    username = args.get("username", "")
    platform = args.get("platform", "lichess")
    nb_games = int(args.get("nb_games", 25))

    if not username:
        return json.dumps({"error": "Thiếu tên kỳ thủ (username)."}, ensure_ascii=False)

    res = scout_player_profile(username=username, platform=platform, nb_games=nb_games)
    return json.dumps(res, ensure_ascii=False)


def register(ctx):
    ctx.register_tool(
        name="chess_player_scout",
        description=(
            "Lập hồ sơ trinh sát kỳ thủ qua Lichess / Chess.com: thống kê thói quen khai cuộc khi cầm Trắng & Đen, "
            "tỷ lệ thắng/thua, điểm số giải đố và các điểm yếu chiến thuật để chuẩn bị trước giải đấu."
        ),
        handler=_handle_player_scout,
        min_mode="readonly",
        schema={
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "Tên tài khoản Lichess hoặc Chess.com của kỳ thủ"},
                "platform": {"type": "string", "description": "Nền tảng: 'lichess' (mặc định) hoặc 'chesscom'"},
                "nb_games": {"type": "integer", "description": "Số lượng ván gần nhất cần quét (mặc định 25)"},
            },
            "required": ["username"],
        },
    )
