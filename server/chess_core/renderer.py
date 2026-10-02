"""
Render & Biểu diễn Bàn cờ trực quan (ASCII, Unicode, Markdown, SVG).
"""
from __future__ import annotations

from typing import Optional
import chess
import chess.svg

_PIECE_UNICODE = {
    "R": "♖", "N": "♘", "B": "♗", "Q": "♕", "K": "♔", "P": "♙",
    "r": "♜", "n": "♞", "b": "♝", "q": "♛", "k": "♚", "p": "♟",
    ".": "·",
}


def render_board_ascii(fen: str, perspective: str = "white") -> str:
    """Render bàn cờ dạng text/unicode có tọa độ rõ ràng."""
    try:
        board = chess.Board(fen)
    except Exception as e:
        return f"Lỗi FEN: {str(e)}"

    is_white = perspective.lower() != "black"
    ranks = range(7, -1, -1) if is_white else range(0, 8)
    files = range(0, 8) if is_white else range(7, -1, -1)

    lines = []
    lines.append("   +-----------------+")
    for r in ranks:
        row_str = f" {r+1} | "
        for f in files:
            sq = chess.square(f, r)
            p = board.piece_at(sq)
            if p:
                sym = p.symbol()
                row_str += _PIECE_UNICODE.get(sym, sym) + " "
            else:
                row_str += "· "
        row_str += f"| {r+1}"
        lines.append(row_str)
    lines.append("   +-----------------+")
    file_labels = "     a b c d e f g h" if is_white else "     h g f e d c b a"
    lines.append(file_labels)

    turn_str = "Trắng đi (White to move)" if board.turn == chess.WHITE else "Đen đi (Black to move)"
    lines.append(f"   Lượt: {turn_str}")
    return "\n".join(lines)


def render_markdown_board(fen: str, perspective: str = "white") -> str:
    """Render bàn cờ bao bọc trong code block Markdown."""
    ascii_board = render_board_ascii(fen, perspective=perspective)
    return f"```\n{ascii_board}\n```"


def render_board_svg(fen: str, last_move: Optional[str] = None, check_sq: Optional[str] = None, size: int = 400) -> str:
    """Sinh chuỗi SVG chất lượng cao của bàn cờ."""
    try:
        board = chess.Board(fen)
    except Exception:
        board = chess.Board()

    move_obj = None
    if last_move:
        try:
            move_obj = chess.Move.from_uci(last_move)
        except Exception:
            pass

    svg_data = chess.svg.board(
        board,
        lastmove=move_obj,
        size=size,
    )
    return svg_data
