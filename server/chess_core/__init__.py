"""
Lõi xử lý & tính toán chuyên môn cờ vua cho JAVIS OS.
Được thiết kế hoàn toàn độc lập, không phụ thuộc vào mã nguồn lõi của upstream.
"""
from __future__ import annotations

from .evaluator import evaluate_fen, analyze_game, check_tablebase
from .openings import get_opening_info, explore_masters_opening
from .puzzles import get_tactical_puzzles, extract_blunder_puzzles
from .scout import scout_player_profile
from .renderer import render_board_ascii, render_board_svg, render_markdown_board

__all__ = [
    "evaluate_fen",
    "analyze_game",
    "check_tablebase",
    "get_opening_info",
    "explore_masters_opening",
    "get_tactical_puzzles",
    "extract_blunder_puzzles",
    "scout_player_profile",
    "render_board_ascii",
    "render_board_svg",
    "render_markdown_board",
]
