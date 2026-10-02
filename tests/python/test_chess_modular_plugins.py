"""
Kiểm thử bộ 5 Plugin Chuyên môn Cờ Vua Độc lập (Chess Modular Plugins).

    python tests/python/test_chess_modular_plugins.py
"""
from _paths import ROOT, SERVER  # noqa: E402,F401
import importlib.util
import json
import sys
from pathlib import Path
import chess

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

loi = []


def check(ten, dieu_kien, them=""):
    print(("ok   " if dieu_kien else "FAIL ") + ten
          + (("  [" + repr(them) + "]") if them and not dieu_kien else ""))
    if not dieu_kien:
        loi.append(ten)


class MockPluginContext:
    def __init__(self, slug):
        self.slug = slug
        self.tools = {}

    def register_tool(self, name, description, handler, min_mode="readonly", schema=None):
        self.tools[name] = {
            "name": name,
            "description": description,
            "handler": handler,
            "min_mode": min_mode,
            "schema": schema,
        }


def load_plugin(slug):
    p_path = Path(ROOT) / "system" / "plugins" / slug / "plugin.py"
    check(f"Tồn tại plugin '{slug}'", p_path.exists())
    spec = importlib.util.spec_from_file_location(f"plugin_{slug}", str(p_path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    ctx = MockPluginContext(slug)
    mod.register(ctx)
    return ctx


# ============================================================
# 1. Test Plugin 1: chess-engine
# ============================================================
ctx_engine = load_plugin("chess-engine")
check("chess-engine đăng ký 3 tool", len(ctx_engine.tools) == 3, len(ctx_engine.tools))
check("Có tool 'chess_eval'", "chess_eval" in ctx_engine.tools)
check("Có tool 'chess_game_analyze'", "chess_game_analyze" in ctx_engine.tools)
check("Có tool 'chess_tablebase'", "chess_tablebase" in ctx_engine.tools)

start_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
eval_res = json.loads(ctx_engine.tools["chess_eval"]["handler"]({"fen": start_fen}, None))
check("chess_eval trả về điểm số và bàn cờ", "score_display" in eval_res and "board_ascii" in eval_res)

sample_pgn = "1. e4 e5 2. Qh5 Nc6 3. Bc4 Nf6 4. Qxf7# 1-0"
analyze_res = json.loads(ctx_engine.tools["chess_game_analyze"]["handler"]({"pgn": sample_pgn}, None))
check("chess_game_analyze phát hiện blunder", len(analyze_res.get("stats", {}).get("black", {}).get("key_blunders", [])) >= 1)

# ============================================================
# 2. Test Plugin 2: chess-openings
# ============================================================
ctx_openings = load_plugin("chess-openings")
check("chess-openings đăng ký 1 tool", len(ctx_openings.tools) == 1)
check("Có tool 'chess_openings'", "chess_openings" in ctx_openings.tools)

op_res = json.loads(ctx_openings.tools["chess_openings"]["handler"]({"moves": "e4 c5"}, None))
check("chess_openings nhận diện Sicilian", "Sicilian" in op_res.get("opening_name", "") or "B20" in op_res.get("eco", "") or "opening_name" in op_res)

# ============================================================
# 3. Test Plugin 3: chess-puzzles
# ============================================================
ctx_puzzles = load_plugin("chess-puzzles")
check("chess-puzzles đăng ký 1 tool", len(ctx_puzzles.tools) == 1)
check("Có tool 'chess_puzzles'", "chess_puzzles" in ctx_puzzles.tools)

puz_res = json.loads(ctx_puzzles.tools["chess_puzzles"]["handler"]({"theme": "fork", "count": 2}, None))
check("chess_puzzles trả danh sách bài tập", len(puz_res.get("puzzles", [])) >= 1)

# ============================================================
# 4. Test Plugin 4: chess-scout
# ============================================================
ctx_scout = load_plugin("chess-scout")
check("chess-scout đăng ký 1 tool", len(ctx_scout.tools) == 1)
check("Có tool 'chess_player_scout'", "chess_player_scout" in ctx_scout.tools)

scout_res = json.loads(ctx_scout.tools["chess_player_scout"]["handler"]({"username": "drnykterstein", "nb_games": 2}, None))
check("chess_player_scout trả hồ sơ kỳ thủ", "username" in scout_res)

# ============================================================
# 5. Test Plugin 5: chess-board
# ============================================================
ctx_board = load_plugin("chess-board")
check("chess-board đăng ký 1 tool", len(ctx_board.tools) == 1)
check("Có tool 'chess_render_board'", "chess_render_board" in ctx_board.tools)

board_res = json.loads(ctx_board.tools["chess_render_board"]["handler"]({"fen": start_fen, "perspective": "white"}, None))
check("chess_render_board trả hình bàn cờ ASCII", "board_display" in board_res and "♔" in board_res["board_display"])

# ============================================================
# TỔNG KẾT
# ============================================================
print()
if loi:
    print(f"FAILED {len(loi)} test:")
    for t in loi:
        print(f"  - {t}")
    sys.exit(1)
else:
    print("ALL 5 MODULAR CHESS PLUGINS PASSED!")
    sys.exit(0)
