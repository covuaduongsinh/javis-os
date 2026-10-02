"""
Đánh giá thế cờ (Engine Evaluation) & Phân tích ván đấu (Game Analysis).
Sử dụng Lichess Cloud Eval API, Syzygy Tablebase API và giải thuật phân tích PGN.
"""
from __future__ import annotations

import io
import math
import re
from typing import Any, Dict, List, Optional, Tuple
import chess
import chess.pgn
import httpx

_TIMEOUT = 10.0

# Bảng điểm quân cờ cơ bản (cho fallback offline)
_PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000,
}


def _count_pieces(board: chess.Board) -> int:
    return len(board.piece_map())


def _simple_material_eval(board: chess.Board) -> int:
    """Tính điểm chênh lệch quân cờ (Centipawns) từ góc nhìn Trắng kèm tìm nước chiếu hết nhanh."""
    if board.is_checkmate():
        return -20000 if board.turn == chess.WHITE else 20000
    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
        return 0

    # Kiểm tra nếu bên đi có nước chiếu hết ngay lập tức (Mate in 1)
    for move in board.legal_moves:
        board.push(move)
        is_mate = board.is_checkmate()
        board.pop()
        if is_mate:
            return 15000 if board.turn == chess.WHITE else -15000

    val = 0
    for sq, piece in board.piece_map().items():
        score = _PIECE_VALUES.get(piece.piece_type, 0)
        val += score if piece.color == chess.WHITE else -score

    # Thưởng nhẹ cho kiểm soát trung tâm
    for sq in [chess.D4, chess.E4, chess.D5, chess.E5]:
        p = board.piece_at(sq)
        if p:
            val += 20 if p.color == chess.WHITE else -20

    return val



def check_tablebase(fen: str) -> Optional[Dict[str, Any]]:
    """Tra cứu kết quả cờ tàn hoàn hảo từ Syzygy Endgame Tablebase (tối đa 7 quân)."""
    try:
        board = chess.Board(fen)
    except Exception:
        return None

    if _count_pieces(board) > 7:
        return None

    url = f"https://tablebase.lichess.ovh/standard?fen={fen.replace(' ', '_')}"
    try:
        with httpx.Client(timeout=5.0) as client:
            r = client.get(url)
            if r.status_code == 200:
                data = r.json()
                wdl = data.get("wdl")
                dtm = data.get("dtm")
                dtz = data.get("dtz")

                # wdl: 2 (Win), 1 (Cursed Win), 0 (Draw), -1 (Blessed Loss), -2 (Loss)
                status_str = "Hòa lý thuyết (Draw)"
                if wdl is not None:
                    if wdl > 0:
                        status_str = f"Trắng thắng tuyệt đối (White Win) - Chiếu hết sau {abs(dtm or 0)} nước" if board.turn == chess.WHITE else f"Trắng thắng tuyệt đối"
                    elif wdl < 0:
                        status_str = f"Đen thắng tuyệt đối (Black Win) - Chiếu hết sau {abs(dtm or 0)} nước" if board.turn == chess.BLACK else f"Đen thắng tuyệt đối"

                moves = []
                for m in data.get("moves", [])[:5]:
                    moves.append({
                        "san": m.get("san"),
                        "uci": m.get("uci"),
                        "wdl": m.get("wdl"),
                        "dtm": m.get("dtm"),
                        "category": "Nước tối ưu (Best)" if m.get("wdl") == wdl else "Nước phụ"
                    })

                return {
                    "source": "Syzygy Tablebase 7-piece",
                    "pieces_count": _count_pieces(board),
                    "wdl": wdl,
                    "dtm": dtm,
                    "dtz": dtz,
                    "result_summary": status_str,
                    "best_moves": moves,
                }
    except Exception:
        pass
    return None


def evaluate_fen(fen: str, multi_pv: int = 3) -> Dict[str, Any]:
    """
    Đánh giá thế cờ từ FEN:
    1. Kiểm tra Syzygy Tablebase nếu <= 7 quân.
    2. Gọi Lichess Cloud Eval API.
    3. Fallback ChessDB API.
    4. Fallback Static Material Eval.
    """
    try:
        board = chess.Board(fen)
    except Exception as e:
        return {"error": f"Mã FEN không hợp lệ: {str(e)}"}

    # 1. Tablebase Check
    tb_res = check_tablebase(fen)
    if tb_res and tb_res.get("wdl") is not None:
        return {
            "fen": fen,
            "turn": "Trắng" if board.turn == chess.WHITE else "Đen",
            "is_game_over": board.is_game_over(),
            "tablebase": tb_res,
            "eval_source": "Syzygy Tablebase",
            "score_display": tb_res.get("result_summary"),
        }

    # 2. Lichess Cloud Eval
    url = f"https://lichess.org/api/cloud-eval?fen={fen.replace(' ', '_')}&multiPv={multi_pv}"
    try:
        with httpx.Client(timeout=_TIMEOUT) as client:
            r = client.get(url, headers={"Accept": "application/json"})
            if r.status_code == 200:
                data = r.json()
                pvs = data.get("pvs", [])
                lines = []
                for pv in pvs:
                    moves_uci = pv.get("moves", "").split()
                    score_cp = pv.get("cp")
                    mate = pv.get("mate")

                    # Chuyển UCI sang SAN cho dễ đọc
                    san_line = []
                    temp_board = board.copy()
                    for uci in moves_uci[:6]:
                        try:
                            m = chess.Move.from_uci(uci)
                            san_line.append(temp_board.san(m))
                            temp_board.push(m)
                        except Exception:
                            san_line.append(uci)

                    lines.append({
                        "moves_uci": moves_uci[:6],
                        "moves_san": " ".join(san_line),
                        "cp": score_cp,
                        "mate": mate,
                        "eval_text": f"M+{mate}" if mate and mate > 0 else (f"M{mate}" if mate else f"{score_cp/100:+.2f}"),
                    })

                main_cp = lines[0]["cp"] if lines and lines[0]["cp"] is not None else None
                main_mate = lines[0]["mate"] if lines else None

                eval_str = f"Chiếu hết sau {main_mate} nước" if main_mate else (f"{main_cp/100:+.2f} pawns" if main_cp is not None else "0.00")

                return {
                    "fen": fen,
                    "turn": "Trắng" if board.turn == chess.WHITE else "Đen",
                    "depth": data.get("depth", 0),
                    "eval_source": "Lichess Stockfish Cloud",
                    "score_cp": main_cp,
                    "score_mate": main_mate,
                    "score_display": eval_str,
                    "top_lines": lines,
                    "is_game_over": board.is_game_over(),
                }
    except Exception:
        pass

    # 3. Fallback Static Material & Positional Eval
    score_cp = _simple_material_eval(board)
    legal_moves = list(board.legal_moves)
    sample_moves = []
    for m in legal_moves[:3]:
        sample_moves.append({"san": board.san(m), "uci": m.uci()})

    return {
        "fen": fen,
        "turn": "Trắng" if board.turn == chess.WHITE else "Đen",
        "eval_source": "Static Heuristic (Offline)",
        "score_cp": score_cp,
        "score_display": f"{score_cp/100:+.2f} pawns",
        "legal_moves_count": len(legal_moves),
        "sample_moves": sample_moves,
        "is_game_over": board.is_game_over(),
    }


def _win_percentage(cp: Optional[int], mate: Optional[int]) -> float:
    """Tính win percentage từ centipawn loss (công thức Lichess)."""
    if mate is not None:
        return 100.0 if mate > 0 else 0.0
    if cp is None:
        return 50.0
    # Lichess win% formula: 50 + 50 * (2 / (1 + exp(-0.00368208 * cp)) - 1)
    return 100.0 / (1.0 + math.exp(-0.00368208 * cp))


def analyze_game(pgn_text: str, max_moves_to_eval: int = 50) -> Dict[str, Any]:
    """
    Phân tích toàn diện một ván cờ từ định dạng PGN:
    - Trích xuất thông tin ván đấu (Trắng, Đen, Kết quả, Ngày đấu, Giải, ECO).
    - Duyệt từng nước đi, đánh giá chênh lệch thế cờ để phát hiện Blunder, Mistake, Inaccuracy.
    - Tính Average Centipawn Loss (ACPL) và ước lượng Accuracy % cho cả hai bên.
    """
    try:
        game = chess.pgn.read_game(io.StringIO(pgn_text))
    except Exception as e:
        return {"error": f"Định dạng PGN không hợp lệ: {str(e)}"}

    if not game:
        return {"error": "Không đọc được ván đấu từ PGN được cung cấp."}

    headers = dict(game.headers)
    white_player = headers.get("White", "Trắng")
    black_player = headers.get("Black", "Đen")
    result = headers.get("Result", "*")
    eco = headers.get("ECO", "")
    opening = headers.get("Opening", "")

    board = game.board()
    move_nodes = list(game.mainline())

    white_blunders = []
    white_mistakes = []
    white_inaccuracies = []

    black_blunders = []
    black_mistakes = []
    black_inaccuracies = []

    white_cp_losses = []
    black_cp_losses = []

    annotated_moves = []
    prev_eval_cp = 0

    # Lấy đánh giá đầu trận
    first_eval = evaluate_fen(board.fen())
    prev_eval_cp = first_eval.get("score_cp") or 0

    for idx, node in enumerate(move_nodes[:max_moves_to_eval]):
        move = node.move
        is_white = (board.turn == chess.WHITE)
        move_number = (idx // 2) + 1
        san = board.san(move)

        # Thế cờ trước khi đi
        fen_before = board.fen()
        board.push(move)
        fen_after = board.fen()

        # Đánh giá sau nước đi
        curr_eval = evaluate_fen(fen_after)
        curr_mate = curr_eval.get("score_mate")
        if curr_mate is not None:
            curr_cp = (20000 - abs(curr_mate) * 100) if curr_mate > 0 else (-20000 + abs(curr_mate) * 100)
        else:
            curr_cp = curr_eval.get("score_cp") or 0

        # Tính toán biến động lợi thế
        if is_white:
            # Đối với Trắng: cp giảm là xấu
            cp_diff = prev_eval_cp - curr_cp
            loss = max(0, cp_diff)
            white_cp_losses.append(loss)
        else:
            # Đối với Đen: cp tăng là xấu
            cp_diff = curr_cp - prev_eval_cp
            loss = max(0, cp_diff)
            black_cp_losses.append(loss)

        classification = "Good"
        comment = ""

        # Phân loại nước đi
        if loss >= 200 or (curr_mate is not None and ((is_white and curr_mate < 0) or (not is_white and curr_mate > 0))):
            classification = "Blunder"
            comment = f"Sai lầm nghiêm trọng (-{loss/100:.1f} điểm)" if curr_mate is None else "Sai lầm nghiêm trọng (Bị chiếu hết)"
            if is_white:
                white_blunders.append({"move": f"{move_number}. {san}", "fen": fen_before, "loss": loss})
            else:
                black_blunders.append({"move": f"{move_number}... {san}", "fen": fen_before, "loss": loss})
        elif loss >= 100:
            classification = "Mistake"
            comment = f"Sai sót (-{loss/100:.1f} điểm)"
            if is_white:
                white_mistakes.append({"move": f"{move_number}. {san}", "fen": fen_before, "loss": loss})
            else:
                black_mistakes.append({"move": f"{move_number}... {san}", "fen": fen_before, "loss": loss})
        elif loss >= 50:
            classification = "Inaccuracy"
            comment = f"Thiếu chính xác (-{loss/100:.1f} điểm)"
            if is_white:
                white_inaccuracies.append({"move": f"{move_number}. {san}", "fen": fen_before, "loss": loss})
            else:
                black_inaccuracies.append({"move": f"{move_number}... {san}", "fen": fen_before, "loss": loss})


        annotated_moves.append({
            "ply": idx + 1,
            "move_number": move_number,
            "turn": "white" if is_white else "black",
            "san": san,
            "eval": curr_eval.get("score_display", ""),
            "classification": classification,
            "loss_cp": loss,
            "comment": comment
        })

        prev_eval_cp = curr_cp

    # Tính ACPL & Accuracy
    white_acpl = round(sum(white_cp_losses) / max(1, len(white_cp_losses)), 1)
    black_acpl = round(sum(black_cp_losses) / max(1, len(black_cp_losses)), 1)

    # Accuracy % theo chuẩn Lichess
    white_accuracy = max(0.0, min(100.0, round(103.1668 * math.exp(-0.04354 * (white_acpl / 10.0)) - 3.1669, 1)))
    black_accuracy = max(0.0, min(100.0, round(103.1668 * math.exp(-0.04354 * (black_acpl / 10.0)) - 3.1669, 1)))

    return {
        "headers": {
            "white": white_player,
            "black": black_player,
            "result": result,
            "eco": eco,
            "opening": opening,
            "event": headers.get("Event", "Casual Game"),
            "date": headers.get("Date", ""),
        },
        "stats": {
            "white": {
                "player": white_player,
                "acpl": white_acpl,
                "accuracy": white_accuracy,
                "blunders": len(white_blunders),
                "mistakes": len(white_mistakes),
                "inaccuracies": len(white_inaccuracies),
                "key_blunders": white_blunders[:3],
            },
            "black": {
                "player": black_player,
                "acpl": black_acpl,
                "accuracy": black_accuracy,
                "blunders": len(black_blunders),
                "mistakes": len(black_mistakes),
                "inaccuracies": len(black_inaccuracies),
                "key_blunders": black_blunders[:3],
            },
            "total_moves_analyzed": len(annotated_moves),
        },
        "critical_moments": (white_blunders + black_blunders)[:5],
        "annotated_moves_sample": annotated_moves[:15],
    }
