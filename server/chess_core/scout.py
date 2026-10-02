"""
Trinh sát kỳ thủ (Player Scouting & Repertoire Analysis) qua Lichess và Chess.com.
"""
from __future__ import annotations

import io
from typing import Any, Dict, List, Optional
import httpx
import chess
import chess.pgn

_TIMEOUT = 12.0


def _fetch_lichess_user(username: str) -> Optional[Dict[str, Any]]:
    url = f"https://lichess.org/api/user/{username}"
    try:
        with httpx.Client(timeout=_TIMEOUT) as client:
            r = client.get(url)
            if r.status_code == 200:
                return r.json()
    except Exception:
        pass
    return None


def _fetch_lichess_games(username: str, max_games: int = 30) -> List[str]:
    """Tải danh sách ván đấu định dạng PGN từ Lichess."""
    url = f"https://lichess.org/api/games/user/{username}?max={max_games}&perfType=blitz,rapid,classical&pgnInJson=false"
    try:
        with httpx.Client(timeout=15.0) as client:
            r = client.get(url, headers={"Accept": "application/x-chess-pgn"})
            if r.status_code == 200:
                # Tách các ván PGN
                raw_text = r.text
                games = []
                current = []
                for line in raw_text.splitlines():
                    if line.startswith("[Event ") and current:
                        games.append("\n".join(current))
                        current = [line]
                    else:
                        current.append(line)
                if current:
                    games.append("\n".join(current))
                return games
    except Exception:
        pass
    return []


def scout_player_profile(username: str, platform: str = "lichess", nb_games: int = 25) -> Dict[str, Any]:
    """
    Lập hồ sơ trinh sát kỳ thủ:
    - Elo hiện tại các thể loại (Blitz, Rapid, Classical, Puzzle).
    - Thói quen khai cuộc khi cầm Trắng & Đen.
    - Tỷ lệ thắng/thua theo từng hệ thống khai cuộc.
    - Đánh giá điểm mạnh/yếu chuẩn bị cho học viên trước trận đấu.
    """
    username = (username or "").strip()
    if not username:
        return {"error": "Thiếu tên kỳ thủ (username)."}

    user_info = _fetch_lichess_user(username)
    perfs = (user_info or {}).get("perfs", {})

    ratings_summary = {
        "blitz": (perfs.get("blitz") or {}).get("rating"),
        "rapid": (perfs.get("rapid") or {}).get("rating"),
        "classical": (perfs.get("classical") or {}).get("rating"),
        "puzzle": (perfs.get("puzzle") or {}).get("rating"),
    }

    raw_games = _fetch_lichess_games(username, max_games=nb_games)
    
    white_openings = {}
    black_vs_e4 = {}
    black_vs_d4 = {}
    black_other = {}

    wins_as_white = 0
    draws_as_white = 0
    losses_as_white = 0

    wins_as_black = 0
    draws_as_black = 0
    losses_as_black = 0

    for pgn_str in raw_games:
        try:
            game = chess.pgn.read_game(io.StringIO(pgn_str))
            if not game:
                continue

            headers = game.headers
            white_p = headers.get("White", "").lower()
            black_p = headers.get("Black", "").lower()
            res = headers.get("Result", "*")
            opening = headers.get("Opening", "Khai cuộc không tên")

            is_white = (username.lower() in white_p)
            is_black = (username.lower() in black_p)

            # Thu thập nước đi đầu tiên
            board = game.board()
            first_moves = []
            for node in list(game.mainline())[:4]:
                first_moves.append(board.san(node.move))
                board.push(node.move)

            first_move_str = " ".join(first_moves[:2]) if len(first_moves) >= 2 else " ".join(first_moves)

            if is_white:
                if res == "1-0":
                    wins_as_white += 1
                elif res == "1/2-1/2":
                    draws_as_white += 1
                elif res == "0-1":
                    losses_as_white += 1

                op_key = f"{first_move_str} ({opening.split(':')[0]})"
                white_openings[op_key] = white_openings.get(op_key, 0) + 1

            elif is_black:
                if res == "0-1":
                    wins_as_black += 1
                elif res == "1/2-1/2":
                    draws_as_black += 1
                elif res == "1-0":
                    losses_as_black += 1

                if first_moves and first_moves[0] == "e4":
                    resp = first_moves[1] if len(first_moves) > 1 else "e4"
                    black_vs_e4[resp] = black_vs_e4.get(resp, 0) + 1
                elif first_moves and first_moves[0] == "d4":
                    resp = first_moves[1] if len(first_moves) > 1 else "d4"
                    black_vs_d4[resp] = black_vs_d4.get(resp, 0) + 1
                else:
                    black_other[first_move_str] = black_other.get(first_move_str, 0) + 1

        except Exception:
            continue

    total_white = wins_as_white + draws_as_white + losses_as_white
    total_black = wins_as_black + draws_as_black + losses_as_black

    # Top khai cuộc khi cầm Trắng
    sorted_white_ops = sorted(white_openings.items(), key=lambda x: -x[1])
    top_white = [{"opening": k, "count": v, "pct": f"{round((v/max(1, total_white))*100, 1)}%"} for k, v in sorted_white_ops[:3]]

    # Phản ứng của Đen chống e4 / d4
    top_black_e4 = [{"response": k, "count": v} for k, v in sorted(black_vs_e4.items(), key=lambda x: -x[1])]
    top_black_d4 = [{"response": k, "count": v} for k, v in sorted(black_vs_d4.items(), key=lambda x: -x[1])]

    return {
        "username": username,
        "platform": platform,
        "profile_url": f"https://lichess.org/@/{username}",
        "ratings": ratings_summary,
        "games_analyzed": len(raw_games),
        "as_white": {
            "total_games": total_white,
            "record": f"{wins_as_white} Thắng - {draws_as_white} Hòa - {losses_as_white} Thua",
            "win_rate": f"{round((wins_as_white/max(1, total_white))*100, 1)}%",
            "favorite_openings": top_white,
        },
        "as_black": {
            "total_games": total_black,
            "record": f"{wins_as_black} Thắng - {draws_as_black} Hòa - {losses_as_black} Thua",
            "win_rate": f"{round((wins_as_black/max(1, total_black))*100, 1)}%",
            "responses_to_1_e4": top_black_e4,
            "responses_to_1_d4": top_black_d4,
        },
        "scout_recommendations": [
            f"Khi đối thủ cầm Trắng: Thường khai cuộc với '{top_white[0]['opening'] if top_white else 'e4/d4'}'. Nên chuẩn bị biến phòng thủ chắc chắn.",
            f"Khi đối thủ cầm Đen chống 1.e4: Thường đáp trả bằng '{top_black_e4[0]['response'] if top_black_e4 else 'e5/c5'}'.",
            f"Điểm số giải đố (Puzzle Rating): {ratings_summary.get('puzzle') or 'N/A'} Elo.",
        ]
    }
