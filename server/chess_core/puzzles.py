"""
Sinh & Tìm kiếm Bài tập Chiến thuật (Chess Puzzles & Blunder Training).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import httpx
import chess
import chess.pgn
import io

_TIMEOUT = 10.0

# Ngân hàng bài tập chiến thuật mẫu kinh điển theo chủ đề khi offline
_CURATED_PUZZLES = [
    {
        "id": "pin_01",
        "theme": "pin",
        "theme_vn": "Ghim quân (Pin)",
        "rating": 1200,
        "fen": "r1b1k2r/pppp1ppp/2n5/4p3/2B1n2q/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 6",
        "turn": "white",
        "solution": ["Qe2", "Nd6", "d3"],
        "description": "Trắng ghim mã e4 của Đen vào Hậu d8 hoặc Vua e8.",
    },
    {
        "id": "fork_01",
        "theme": "fork",
        "theme_vn": "Bắt đôi (Knight Fork)",
        "rating": 1350,
        "fen": "r1bqk2r/pp1p1ppp/2n1pn2/8/1bPN4/2N1P3/PP3PPP/R1BQKB1R w KQkq - 1 7",
        "turn": "white",
        "solution": ["Ndb5", "d5", "a3"],
        "description": "Trắng tạo thế bắt đôi vào các điểm yếu.",
    },
    {
        "id": "mate2_01",
        "theme": "mateIn2",
        "theme_vn": "Chiếu hết 2 nước (Mate in 2)",
        "rating": 1400,
        "fen": "6k1/5ppp/8/8/8/8/5PPP/1Q4K1 w - - 0 1",
        "turn": "white",
        "solution": ["Qb8#"],
        "description": "Đòn chiếu hết hàng cuối (Back-rank mate).",
    },
    {
        "id": "discovered_01",
        "theme": "discoveredAttack",
        "theme_vn": "Tấn công mở (Discovered Attack)",
        "rating": 1500,
        "fen": "r1b1k2r/ppp2ppp/2n5/3qp3/1b6/2N2N2/PPPP1PPP/R1BQK2R w KQkq - 0 8",
        "turn": "white",
        "solution": ["Nxd5"],
        "description": "Trắng ăn Hậu Đen d5.",
    },
    {
        "id": "endgame_01",
        "theme": "endgame",
        "theme_vn": "Tàn cuộc Tốt cơ bản (Pawn Endgame)",
        "rating": 1300,
        "fen": "8/8/8/4k3/4P3/4K3/8/8 w - - 0 1",
        "turn": "white",
        "solution": ["Kd3", "Ke6", "Kd4", "Kd6", "e5+"],
        "description": "Kỹ thuật chiếm ô đối diện (Opposition) để phong cấp Tốt.",
    }
]


def get_tactical_puzzles(theme: str = "", min_rating: int = 1000, max_rating: int = 2000, count: int = 3) -> Dict[str, Any]:
    """
    Lấy danh sách bài tập chiến thuật theo chủ đề (pin, fork, skewer, mateIn1, mateIn2, endgame...)
    và khoảng Elo yêu cầu.
    """
    theme = (theme or "").strip().lower()
    
    # 1. Thử lấy bài tập hàng ngày từ Lichess Daily Puzzle
    daily_puzzle = None
    try:
        with httpx.Client(timeout=5.0) as client:
            r = client.get("https://lichess.org/api/puzzle/daily")
            if r.status_code == 200:
                data = r.json()
                p = data.get("puzzle", {})
                g = data.get("game", {})
                daily_puzzle = {
                    "id": p.get("id"),
                    "rating": p.get("rating"),
                    "themes": p.get("themes", []),
                    "solution_moves": p.get("solution", []),
                    "fen": p.get("fen") or g.get("tree", {}).get("fen"),
                    "url": f"https://lichess.org/training/{p.get('id')}",
                    "source": "Lichess Daily Puzzle"
                }
    except Exception:
        pass

    # 2. Lọc từ kho bài tập tuyển chọn
    results = []
    for p in _CURATED_PUZZLES:
        if theme and theme not in p["theme"].lower() and theme not in p["theme_vn"].lower():
            continue
        if p["rating"] < min_rating - 200 or p["rating"] > max_rating + 200:
            continue
        results.append(p)

    if not results and _CURATED_PUZZLES:
        results = _CURATED_PUZZLES[:count]

    return {
        "requested_theme": theme or "Tất cả chủ đề",
        "rating_range": f"{min_rating} - {max_rating}",
        "daily_puzzle": daily_puzzle,
        "puzzles": results[:count],
        "total_returned": len(results[:count]),
    }


def extract_blunder_puzzles(pgn_text: str, target_player: str = "") -> Dict[str, Any]:
    """
    Trích xuất các thế cờ có Blunder (nước đi sai lầm) trong ván đấu thành bài tập sửa lỗi cho học viên.
    """
    from .evaluator import analyze_game
    analysis = analyze_game(pgn_text, max_moves_to_eval=60)
    if "error" in analysis:
        return analysis

    target_player_lower = (target_player or "").strip().lower()
    headers = analysis.get("headers", {})
    white_name = headers.get("white", "")
    black_name = headers.get("black", "")

    puzzles = []
    critical_moments = analysis.get("critical_moments", [])

    for idx, cm in enumerate(critical_moments):
        fen = cm.get("fen")
        bad_move = cm.get("move")
        loss = cm.get("loss", 0)

        # Lấy đánh giá nước đi tối ưu thay thế
        from .evaluator import evaluate_fen
        best_eval = evaluate_fen(fen)
        top_line = (best_eval.get("top_lines") or [{}])[0]
        best_move_san = top_line.get("moves_san", "")

        puzzles.append({
            "puzzle_number": idx + 1,
            "fen": fen,
            "played_bad_move": bad_move,
            "loss_eval": f"-{loss/100:.1f} điểm",
            "best_move_solution": best_move_san,
            "question": "Thế cờ trước khi đi sai. Hãy tìm nước đi tối ưu nhất để giữ/tăng ưu thế?",
        })

    return {
        "game_info": f"{white_name} vs {black_name} ({headers.get('result')})",
        "total_blunder_puzzles": len(puzzles),
        "student_puzzles": puzzles,
    }
