"""Cầu nối Cờ vua Dương Sinh: chỉ đọc, chặn đúng bảng bí mật, xếp hạng giải khớp app bốc thăm.

    python tests/python/test_duongsinh_mcp.py

Không cần pytest, KHÔNG chạm mạng. Mọi test ở đây hoặc là hàm thuần, hoặc là nhánh lỗi
bật ra TRƯỚC khi mở kết nối HTTP.

Ba thứ file này canh, theo thứ tự quan trọng:

1. **Lời hứa chỉ đọc.** Kết nối này dùng tài khoản nhân viên của lõi covuaduongsinh, và
   trong thực tế chủ hệ dán tài khoản admin vào. Lời hứa "Javis không sửa được dữ liệu
   trung tâm" phải là một sự thật về MÃ chứ không phải một câu trong mô tả connector: chỉ
   `_get()` chạm Payload và nó chỉ biết GET. Test soi thẳng mã nguồn vì đây là loại luật
   mà một dòng thêm vào sau này sẽ phá lặng lẽ, không test nào khác bắt được.

2. **Bảng bí mật bị chặn.** `users` chứa băm mật khẩu toàn bộ nhân viên, `lichess-tokens`
   là token đã mã hoá của học viên, `otp-codes` là mã đăng nhập của phụ huynh. Tool truy
   vấn chung mở ra mọi collection nên phải có danh sách cấm, và nó phải chặn TRƯỚC khi gọi.

3. **Xếp hạng khớp app bốc thăm.** Hai nơi cùng tính bảng xếp hạng một giải mà ra hai kết
   quả khác nhau là cách nhanh nhất để mất lòng tin vào cả hệ. Luật phải y hệt: điểm,
   Buchholz Cut-1, Buchholz, hệ số; bye cộng 1 điểm nhưng KHÔNG sinh đối thủ ảo.
"""
from _paths import ROOT, SERVER  # noqa: E402,F401  - nạp server/ vào sys.path
import asyncio
import json
import sys
from pathlib import Path

import duongsinh_mcp as ds
import mcp_client

loi = []


def check(ten, dieu_kien, them=""):
    print(("ok   " if dieu_kien else "FAIL ") + ten
          + (("  [" + repr(them) + "]") if them and not dieu_kien else ""))
    if not dieu_kien:
        loi.append(ten)


def goi(tool, args=None, spec=None):
    return asyncio.run(ds.call(tool, args or {}, spec if spec is not None else {"secrets": {}}))


TEN_TOOL = [t["name"] for t in ds.TOOLS]


# ---- 1. Bộ tool đúng hình dạng ----

check("có đúng 8 tool", len(ds.TOOLS) == 8, TEN_TOOL)
check("tên tool không trùng", len(set(TEN_TOOL)) == len(TEN_TOOL), TEN_TOOL)
check("tên tool đều dạng ds_snake_case",
      all(t.startswith("ds_") and t.replace("_", "").isalnum() and t.islower() for t in TEN_TOOL),
      TEN_TOOL)
check("tool nào cũng có mô tả tử tế",
      all(len(t.get("description") or "") >= 40 for t in ds.TOOLS),
      [t["name"] for t in ds.TOOLS if len(t.get("description") or "") < 40])
check("tool nào cũng khai inputSchema kiểu object",
      all((t.get("inputSchema") or {}).get("type") == "object" for t in ds.TOOLS))
check("trường required đều nằm trong properties",
      all(set(t["inputSchema"].get("required") or [])
          <= set((t["inputSchema"].get("properties") or {}).keys()) for t in ds.TOOLS))
check("list_tools trả đúng bộ TOOLS", asyncio.run(ds.list_tools({})) == ds.TOOLS)


# ---- 2. Lời hứa CHỈ ĐỌC, soi thẳng mã nguồn ----

NGUON = (Path(SERVER) / "duongsinh_mcp.py").read_text(encoding="utf-8")
DONG = NGUON.split("\n")
DONG_MA = [d for d in DONG if not d.strip().startswith("#")]


def cua_so(i, n=3):
    """Gộp dòng i với vài dòng sau - lời gọi httpx hay bị xuống dòng giữa chừng."""
    return " ".join(x.strip() for x in DONG[i:i + n])


for dong_lenh in (".put(", ".patch(", ".delete(", ".request("):
    con = [d.strip() for d in DONG_MA if "client" + dong_lenh in d]
    check(f"không có lời gọi client{dong_lenh} nào", not con, con)

posts = [i for i, d in enumerate(DONG) if "client.post(" in d and not d.strip().startswith("#")]
check("có đúng 3 lời gọi POST (login + 2 đường bốc thăm)", len(posts) == 3, len(posts))
xau = [cua_so(i) for i in posts
       if "/api/users/login" not in cua_so(i) and "{pair}" not in cua_so(i)]
check("mọi POST đều là đăng nhập hoặc gọi app bốc thăm, không POST nào vào lõi", not xau, xau)

than_get = NGUON.split("async def _get(")[1].split("\nasync def ")[0]
check("_get chỉ phát GET", "client.get(" in than_get
      and not any(x in than_get for x in ("client.post(", "client.put(", "client.patch(",
                                          "client.delete(", "client.request(")))
check("_get không nhận tham số method (thêm vào là phá lời hứa chỉ đọc)",
      "method" not in NGUON.split("async def _get(")[1].split(")")[0])
check("_get tự đăng nhập lại khi gặp 401", "== 401" in than_get and "lam_moi=True" in than_get)
check("catalog KHÔNG khai tool ghi nào cho cầu nối này",
      not any(x in NGUON for x in ('"write"', '"danger"')))


# ---- 3. Bảng bí mật bị chặn, và chặn TRƯỚC khi ra mạng ----

check("_DENY phủ đủ bốn kho bí mật",
      {"users", "lichess-tokens", "otp-codes", "ai-config"} <= ds._DENY, sorted(ds._DENY))

for bang in ("users", "lichess-tokens", "otp-codes", "ai-config"):
    kq = goi("ds_truy_van", {"bang": bang})
    check(f"ds_truy_van chặn bảng '{bang}'",
          kq.startswith("ERROR:") and "không được phép" in kq, kq[:120])

# Chặn phải xảy ra khi CHƯA có thông tin đăng nhập nào - tức là chặn ở tầng luật, không
# phải may mắn vì mạng lỗi. Bảng hợp lệ với spec rỗng thì rơi vào lỗi thiếu cấu hình.
kq = goi("ds_truy_van", {"bang": "students"})
check("bảng hợp lệ + spec rỗng thì báo thiếu cấu hình, không phải báo cấm",
      kq.startswith("ERROR:") and "thiếu" in kq, kq[:160])
check("ds_truy_van thiếu tên bảng thì báo rõ",
      goi("ds_truy_van", {}).startswith("ERROR: thiếu tên bảng"))


# ---- 4. Nhánh lỗi không được ném ra ngoài, và không được chạm mạng ----

for tool in TEN_TOOL:
    kq = goi(tool, {"bang": "students", "giai": "x", "hoc_vien": "y"})
    check(f"{tool}: spec rỗng trả chuỗi ERROR gọn, không nổ",
          isinstance(kq, str) and kq.startswith("ERROR:"), kq[:120])

check("tool lạ báo đúng tên cầu nối",
      goi("ds_khong_co_that").startswith("ERROR: tool 'ds_khong_co_that' không tồn tại"))
check("ds_boc_tham chặn hệ đấu lạ",
      goi("ds_boc_tham", {"he": "--rm -rf"}).startswith("ERROR: 'he' chỉ nhận"))


# ---- 5. Hàm thuần: cắt bớt, trần bản ghi, suy ra địa chỉ app bốc thăm ----

check("_gioi_han chặn trần", ds._gioi_han({"gioi_han": 9999}) == ds._MAX_LIMIT)
check("_gioi_han chặn sàn với số âm", ds._gioi_han({"gioi_han": -5}) == 1)
check("_gioi_han bỏ qua rác", ds._gioi_han({"gioi_han": "abc"}) == 20)
# 0 nghĩa là "không giới hạn" trong đầu model, không phải "cho tôi 1 bản ghi". Trả 1 cho câu
# đó là giấu mất dữ liệu mà không báo gì.
check("_gioi_han: 0 rơi về mặc định chứ không về 1", ds._gioi_han({"gioi_han": 0}) == 20)
check("_gioi_han: bỏ trống rơi về mặc định", ds._gioi_han({}) == 20)

check("_flat rút quan hệ về tên",
      ds._flat({"id": 7, "fullName": "Nguyễn An"}) == "Nguyễn An")
check("_flat rút quan hệ không tên về id", ds._flat({"id": 7, "khac": 1}) == 7)
check("_flat rút danh sách quan hệ",
      ds._flat([{"fullName": "A"}, {"name": "B"}]) == ["A", "B"])
check("_pick bỏ trường rỗng",
      ds._pick({"a": 1, "b": "", "c": None, "d": []}, ["a", "b", "c", "d"]) == {"a": 1})

check("_pair_base suy ra từ tên miền lõi",
      ds._pair_base({"secrets": {"core_url": "https://covuaduongsinh.com"}})
      == "https://pair.covuaduongsinh.com")
check("_pair_base ưu tiên địa chỉ khai tay",
      ds._pair_base({"secrets": {"core_url": "https://a.com", "pair_url": "https://b.com/"}})
      == "https://b.com")
check("_pair_base rỗng khi chưa khai lõi", ds._pair_base({"secrets": {}}) == "")

check("_clip cắt chuỗi dài và nói rõ đã cắt",
      len(ds._clip("x" * 50000, 1000)) < 1200 and "BỊ CẮT" in ds._clip("x" * 50000, 1000))


# ---- 6. Bảng xếp hạng phải khớp luật của app bốc thăm ----

GIAI = {
    "name": "Giải thử", "totalRounds": 2,
    "players": [{"id": 1, "name": "A", "rating": 1600}, {"id": 2, "name": "B", "rating": 1500},
                {"id": 3, "name": "C", "rating": 1400}, {"id": 4, "name": "D", "rating": 1300}],
    "results": [
        {"boards": [{"white": 1, "black": 2, "w": "1"}, {"white": 3, "black": 4, "w": "="}]},
        {"boards": [{"white": 1, "black": 3, "w": "="}, {"white": 2, "black": 4, "w": "0"}]},
    ],
}
hang = ds._bang_xep_hang(GIAI)
theo_ten = {x["ten"]: x for x in hang}

check("điểm tính đúng cho thắng, thua, hoà",
      [theo_ten[t]["diem"] for t in "ABCD"] == [1.5, 0.0, 1.0, 1.5],
      [(x["ten"], x["diem"]) for x in hang])
check("Buchholz là tổng điểm đối thủ đã gặp",
      [theo_ten[t]["buchholz"] for t in "ABCD"] == [1.0, 3.0, 3.0, 1.0],
      [(x["ten"], x["buchholz"]) for x in hang])
check("Buchholz Cut-1 bỏ đối thủ điểm thấp nhất",
      [theo_ten[t]["buchholz_cut1"] for t in "ABCD"] == [1.0, 1.5, 1.5, 1.0],
      [(x["ten"], x["buchholz_cut1"]) for x in hang])
# A và D bằng điểm, bằng cả hai Buchholz -> hệ số phân định, A (1600) đứng trên D (1300).
check("bằng mọi tiêu chí thì hệ số phân định",
      [x["ten"] for x in hang] == ["A", "D", "C", "B"], [x["ten"] for x in hang])
check("thứ hạng đánh số liên tục từ 1",
      [x["hang"] for x in hang] == [1, 2, 3, 4])
check("số ván đếm đúng, không tính bye", all(x["so_van"] == 2 for x in hang))

BYE = {"players": [{"id": 1, "name": "Một mình", "rating": 1200}],
       "results": [{"boards": [], "bye": 1}]}
mot = ds._bang_xep_hang(BYE)[0]
check("bye cộng 1 điểm", mot["diem"] == 1.0, mot)
check("bye KHÔNG sinh đối thủ ảo (giống app, khác FIDE)",
      mot["so_van"] == 0 and mot["buchholz"] == 0.0 and mot["buchholz_cut1"] == 0.0, mot)

check("giải chưa đấu vòng nào vẫn ra bảng, không nổ",
      len(ds._bang_xep_hang({"players": GIAI["players"], "results": []})) == 4)
check("state rỗng ra bảng rỗng", ds._bang_xep_hang({}) == [])
# Bản ghi hỏng (kỳ thủ đã bị xoá khỏi danh sách) không được làm sập cả bảng xếp hạng.
check("bàn đấu trỏ vào kỳ thủ không tồn tại thì bỏ qua bàn đó",
      ds._bang_xep_hang({"players": [{"id": 1, "name": "A", "rating": 1}],
                         "results": [{"boards": [{"white": 1, "black": 99, "w": "1"}]}]})[0]["diem"] == 0.0)


# ---- 7. Danh mục connector khớp với mã ----

CAT = json.loads((Path(ROOT) / "system" / "mcp-catalog.json").read_text(encoding="utf-8"))
con = next((c for c in CAT["connectors"] if c["id"] == "duongsinh"), None)
check("có mục connector 'duongsinh' trong danh mục", con is not None)

if con:
    check("transport internal", con.get("transport") == "internal")
    check("khai đúng tên module", con.get("internal") == "duongsinh")
    check("module đã đăng ký trong _INTERNAL của mcp_client",
          mcp_client._INTERNAL.get("duongsinh") == "duongsinh_mcp", mcp_client._INTERNAL)
    check("mặc định CHỈ ĐỌC", con.get("default_perm") == "readonly")

    tm = con.get("tool_meta") or {}
    check("tool_meta.read liệt kê đúng 8 tool của mã",
          set(tm.get("read") or []) == set(TEN_TOOL),
          sorted(set(tm.get("read") or []) ^ set(TEN_TOOL)))
    check("tool_meta KHÔNG khai write/danger (cầu nối không có tool ghi)",
          not tm.get("write") and not tm.get("danger"), tm)

    val = con.get("validate") or {}
    check("tool dùng để Kiểm tra là tool có thật", val.get("tool") in TEN_TOOL, val.get("tool"))

    khoa = {f["key"] for f in ((con.get("auth") or {}).get("fields") or [])}
    check("hỏi đủ địa chỉ lõi, email, mật khẩu",
          {"core_url", "email", "password"} <= khoa, sorted(khoa))
    check("có phần hướng dẫn cho người dùng",
          len(((con.get("auth") or {}).get("guide") or "")) >= 80)
    check("phần rủi ro nói rõ đây là kết nối chỉ đọc",
          "CHỈ ĐỌC" in (con.get("risk") or ""))

    # Connection dạng internal phải qua được câu chặn "có server để dial không", nếu không
    # thì trang Kết nối báo xanh mà hộp công cụ trống - đúng con bọ của Substack/Botcake.
    check("qua được câu chặn co_server_de_dial",
          mcp_client.co_server_de_dial({"transport": "internal", "internal": "duongsinh",
                                        "url": "", "command": ""}))


print()
if loi:
    print(f"{len(loi)} test ĐỎ: " + ", ".join(loi))
    sys.exit(1)
print("Tất cả test xanh.")
