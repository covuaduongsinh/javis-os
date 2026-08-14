"""
Cầu nối Cờ vua Dương Sinh (transport "internal" trong catalog).

Lõi nghiệp vụ của Dương Sinh nằm ở một repo khác: Next.js 15 + Payload CMS 3 +
PostgreSQL (Supabase), phục vụ ở covuaduongsinh.com. Nó KHÔNG có MCP chính chủ,
nên Javis bọc REST của Payload thành một bộ tool MCP-tương-đương.

Ranh giới đã chốt với chủ hệ: **lõi giữ dữ liệu, Javis chỉ ĐỌC**. Javis là buồng
lái riêng của chủ (hỏi đáp, nhắc việc, báo cáo, soạn nháp), không phải nơi nhập
liệu. Vì vậy:

- Chỉ có ĐÚNG MỘT hàm gọi được Payload là `_get()`, và nó chỉ phát GET. Không có
  đường nào trong file này ghi được vào lõi, kể cả khi kết nối bị nâng lên Toàn
  quyền. Tài khoản đang dùng là tài khoản admin nên đây là lớp chặn thật, không
  phải lời dặn trong prompt.
- Hai ngoại lệ POST đều không đụng dữ liệu: `POST /api/users/login` (lấy JWT) và
  app bốc thăm (`/api/pair` là hàm thuần TRF vào cặp đấu ra; `/api/tournaments/
  {id}/pair` cũng chỉ đọc rồi chạy engine, không ghi).

spec["secrets"] (mcp_store.resolved cấp):
    core_url  - gốc lõi, vd https://covuaduongsinh.com
    email     - tài khoản nhân viên/admin
    password  - mật khẩu
    pair_url  - gốc app bốc thăm (tuỳ chọn, mặc định suy ra từ core_url)

Ba cái bẫy đã tính trước, đừng gỡ ra:

1. **JWT hết hạn.** Payload trả token có hạn. Nếu không tự đăng nhập lại thì sau
   vài giờ MỌI tool hỏng im lặng (401 trả về chuỗi lỗi, model tưởng không có dữ
   liệu). `_get()` bắt 401 và thử lại đúng một lần với token mới.
2. **Pool Postgres của lõi đặt max: 3.** Gọi dồn là nghẽn cả trang admin của nhân
   viên. Nên có cache TTL ngắn `_CACHE_TTL` và tuyệt đối không lặp truy vấn từng
   học viên một; tool nào cần nhiều bản ghi thì lấy một mẻ rồi ghép trong Python.
3. **depth=1 của Payload trả cả object quan hệ.** Để nguyên là một học viên ngốn
   vài nghìn token. `_pick()`/`_flat()` rút quan hệ về đúng cái tên, và `_DENY`
   chặn các collection chứa bí mật (băm mật khẩu nhân viên, token Lichess, OTP).
"""
import json
import time

import httpx

_CACHE_TTL = 45          # giây - đủ để một lượt chat hỏi lại vài lần mà không đập vào pool
_TIMEOUT = 30
_MAX_LIMIT = 100         # trần bản ghi mỗi lần gọi, chặn model xin cả bảng

# Collection KHÔNG được đọc qua cầu nối này. Đây là ranh giới bí mật, không phải
# ranh giới phạm vi: `users` chứa băm mật khẩu + salt của toàn bộ nhân viên,
# `lichess-tokens` là token đã mã hoá, `otp-codes` là mã đăng nhập của phụ huynh,
# `ai-config` giữ khoá API. Mọi thứ khác cho đọc.
_DENY = {
    "users", "lichess-tokens", "otp-codes", "ai-config",
    "payload-preferences", "payload-migrations",
}

# Cache token theo (core_url, email) - nhiều connection cùng lõi vẫn dùng chung được.
_TOKENS = {}
# Cache kết quả GET theo (core_url, path, query) trong _CACHE_TTL giây.
_CACHE = {}


def _clip(text, max_chars=8000):
    text = str(text)
    if len(text) <= max_chars:
        return text
    head = int(max_chars * 0.6)
    tail = max_chars - head
    return (text[:head] + f"\n… [KẾT QUẢ BỊ CẮT - bỏ {len(text) - head - tail:,} ký tự giữa] …\n"
            + text[-tail:])


def _t(name, description, props=None, required=None):
    return {"name": name, "description": description,
            "inputSchema": {"type": "object", "properties": props or {}, "required": required or []}}


def _flat(v):
    """Rút một giá trị Payload depth=1 về thứ đọc được.

    Quan hệ ở depth=1 là cả object; giữ nguyên thì một danh sách 20 học viên
    thành vài chục nghìn token. Lấy đúng trường tên theo thứ tự ưu tiên của lõi.
    """
    if isinstance(v, dict):
        for k in ("fullName", "tenDayDu", "title", "name", "tenTat", "code", "id"):
            if v.get(k) not in (None, ""):
                return v[k]
        return None
    if isinstance(v, list):
        return [x for x in (_flat(i) for i in v) if x not in (None, "", [], {})]
    return v


def _pick(doc, fields):
    """Giữ đúng các trường cần, bỏ giá trị rỗng (rỗng vẫn tốn token mà không nói gì)."""
    out = {}
    for f in fields:
        v = _flat((doc or {}).get(f))
        if v in (None, "", [], {}):
            continue
        out[f] = v
    return out


def _so(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


# ============================================================
# Tầng HTTP - chỗ DUY NHẤT chạm vào lõi
# ============================================================
def _base(spec):
    s = (spec or {}).get("secrets") or {}
    return (s.get("core_url") or "").strip().rstrip("/"), s


def _pair_base(spec):
    """Gốc app bốc thăm. Không khai thì suy ra pair.<domain lõi>."""
    core, s = _base(spec)
    pair = (s.get("pair_url") or "").strip().rstrip("/")
    if pair:
        return pair
    if not core:
        return ""
    return core.replace("://", "://pair.", 1)


async def _token(client, core, s, lam_moi=False):
    key = (core, s.get("email") or "")
    if not lam_moi:
        ent = _TOKENS.get(key)
        if ent and ent["het_han"] > time.time() + 60:
            return ent["token"]
    r = await client.post(f"{core}/api/users/login",
                          json={"email": s.get("email"), "password": s.get("password")})
    if r.status_code >= 400:
        raise RuntimeError(f"đăng nhập lõi thất bại {r.status_code}: {(r.text or '')[:200]}")
    data = r.json() or {}
    tok = data.get("token")
    if not tok:
        raise RuntimeError("lõi không trả token - kiểm tra lại email/mật khẩu ở trang Kết nối")
    # exp của Payload là epoch giây. Thiếu thì cho 1 giờ, _get vẫn tự cứu khi gặp 401.
    _TOKENS[key] = {"token": tok, "het_han": _so(data.get("exp")) or (time.time() + 3600)}
    return tok


async def _get(spec, path, params=None):
    """GET vào lõi. Đây là hàm DUY NHẤT gọi Payload, và nó không bao giờ ghi.

    Đừng thêm tham số `method` vào đây. Toàn bộ đảm bảo "Javis không sửa được dữ
    liệu trung tâm" của file này nằm ở chỗ hàm này chỉ biết GET.
    """
    core, s = _base(spec)
    if not core or not s.get("email") or not s.get("password"):
        raise RuntimeError("kết nối Dương Sinh thiếu địa chỉ lõi / email / mật khẩu - sửa ở trang Kết nối")

    ck = (core, path, json.dumps(params or {}, sort_keys=True, ensure_ascii=False))
    hit = _CACHE.get(ck)
    now = time.time()
    if hit and hit[0] > now:
        return hit[1]

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        tok = await _token(client, core, s)
        r = await client.get(f"{core}{path}", params=params or None,
                             headers={"Authorization": f"JWT {tok}"})
        if r.status_code == 401:
            # Token hết hạn giữa chừng. Không cứu ở đây thì mọi tool hỏng im lặng.
            tok = await _token(client, core, s, lam_moi=True)
            r = await client.get(f"{core}{path}", params=params or None,
                                 headers={"Authorization": f"JWT {tok}"})
        if r.status_code >= 400:
            raise RuntimeError(f"lõi trả {r.status_code} ở {path}: {(r.text or '')[:200]}")
        data = r.json()

    # Dọn cache cũ ngay tại đây cho khỏi phình theo phiên dài.
    if len(_CACHE) > 200:
        for k, v in list(_CACHE.items()):
            if v[0] <= now:
                _CACHE.pop(k, None)
    _CACHE[ck] = (now + _CACHE_TTL, data)
    return data


async def _docs(spec, bang, params):
    d = await _get(spec, f"/api/{bang}", params)
    return (d or {}).get("docs") or [], (d or {}).get("totalDocs")


def _gioi_han(args, mac_dinh=20):
    """Trần bản ghi mỗi lần gọi.

    0, rỗng và rác đều rơi về MẶC ĐỊNH chứ không về sàn 1: model hay truyền 0 với nghĩa
    "không giới hạn", mà trả đúng một bản ghi cho câu hỏi đó là im lặng giấu mất dữ liệu.
    Số âm thì mới kẹp về 1.
    """
    v = args.get("gioi_han")
    try:
        n = mac_dinh if v in (None, "", 0) else int(v)
    except (TypeError, ValueError):
        n = mac_dinh
    return max(1, min(n, _MAX_LIMIT))


# ============================================================
# Bộ tool
# ============================================================
_BANG_GOI_Y = ("students, parents, classes, class-sessions, attendance, enrollments, "
               "student-levels, levels, locations, coaches, curriculum-templates, "
               "progress-reports, payments, tuition-cycles, tuition-packages, refunds, "
               "expenses, renewal-requests, leads, care-interactions, complaints, "
               "survey-responses, books, book-issues, chess-games, chess-puzzles, "
               "practice-results, lichess-snapshots, pairing-tournaments, holidays")

TOOLS = [
    _t("ds_truy_van",
       "Đọc BẤT KỲ bảng nào của lõi Dương Sinh bằng cú pháp Payload REST. Dùng khi các tool "
       "chuyên biệt bên dưới không phủ hết. Bảng hay dùng: " + _BANG_GOI_Y + ". "
       "Tham số loc là chuỗi JSON theo cú pháp where của Payload, "
       'vd {"enrollmentStatus":{"equals":"dang_hoc"}}.',
       {"bang": {"type": "string", "description": "Tên bảng (collection slug)"},
        "loc": {"type": "string", "description": "Điều kiện where dạng JSON, tuỳ chọn"},
        "sap_xep": {"type": "string", "description": "Sắp xếp, vd -createdAt"},
        "truong": {"type": "string", "description": "Danh sách trường muốn lấy, cách nhau dấu phẩy"},
        "gioi_han": {"type": "integer", "description": "Số bản ghi, tối đa 100"},
        "trang": {"type": "integer", "description": "Trang, mặc định 1"}},
       ["bang"]),

    _t("ds_hoc_vien",
       "Tìm và xem hồ sơ học viên: cấp độ, cơ sở, trạng thái học, lý do nghỉ, tài khoản Lichess, "
       "phụ huynh. Tìm được theo tên hoặc mã học viên.",
       {"tim": {"type": "string", "description": "Tên hoặc mã học viên"},
        "trang_thai": {"type": "string", "description": "dang_hoc | tam_nghi | da_nghi"},
        "gioi_han": {"type": "integer"}}),

    _t("ds_hoc_phi",
       "Tình hình học phí. Không truyền hoc_vien thì trả danh sách em SẮP HẾT BUỔI (ưu tiên "
       "gia hạn). Truyền hoc_vien thì trả chu kỳ và lịch sử nộp của riêng em đó.",
       {"hoc_vien": {"type": "string", "description": "Tên hoặc mã học viên, tuỳ chọn"},
        "gioi_han": {"type": "integer"}}),

    _t("ds_diem_danh",
       "Điểm danh gần đây kèm thống kê: số buổi có mặt, vắng phép, vắng không phép, và điểm "
       "làm bài về nhà / ý thức. Lọc theo học viên hoặc theo khoảng ngày.",
       {"hoc_vien": {"type": "string", "description": "Tên hoặc mã học viên, tuỳ chọn"},
        "tu_ngay": {"type": "string", "description": "YYYY-MM-DD"},
        "den_ngay": {"type": "string", "description": "YYYY-MM-DD"},
        "gioi_han": {"type": "integer"}}),

    _t("ds_lop",
       "Danh sách lớp: cấp độ, cơ sở, huấn luyện viên, sĩ số, và lịch học từng buổi trong tuần.",
       {"tim": {"type": "string", "description": "Tên lớp, tuỳ chọn"},
        "trang_thai": {"type": "string", "description": "Lọc theo trạng thái lớp, tuỳ chọn"},
        "gioi_han": {"type": "integer"}}),

    _t("ds_bao_cao",
       "Bảng KPI tổng hợp sẵn của lõi: lead theo tuần và theo nguồn, phễu chuyển đổi, tỉ lệ gia "
       "hạn, tỉ lệ đi học, doanh thu và chi phí theo tuần. Cần tài khoản có quyền xem báo cáo.",
       {"so_tuan": {"type": "integer", "description": "Số tuần nhìn lại, 1 tới 52"}}),

    _t("ds_giai_dau",
       "Giải đấu trong hệ bốc thăm: danh sách giải, hoặc bảng xếp hạng một giải (điểm, Buchholz "
       "Cut-1, Buchholz) cùng kết quả từng vòng.",
       {"giai": {"type": "string", "description": "Mã giải (tid). Bỏ trống để liệt kê giải."},
        "gioi_han": {"type": "integer"}}),

    _t("ds_boc_tham",
       "Xin cặp đấu vòng kế tiếp từ app bốc thăm Dương Sinh (bbpPairings, hệ Thuỵ Sĩ). Chỉ tính "
       "toán rồi trả cặp đấu, KHÔNG ghi kết quả vào giải - việc chốt vòng vẫn làm trên app.",
       {"giai": {"type": "string", "description": "Mã giải (tid) trong hệ"},
        "trf": {"type": "string", "description": "Chuỗi TRF thay cho mã giải, tuỳ chọn"},
        "he": {"type": "string", "description": "--dutch (mặc định) hoặc --burstein"}}),
]

_HV_TRUONG = ["id", "code", "fullName", "nickname", "dob", "enrollmentStatus", "lyDoNghi",
              "ngayNghi", "ngayQuayLai", "capChinh", "location", "lichessUsername", "parents"]


async def _tim_hoc_vien(spec, tim, gioi_han=20, trang_thai=""):
    params = {"limit": gioi_han, "depth": 1, "sort": "fullName"}
    tim = (tim or "").strip()
    if tim:
        params["where[or][0][fullName][like]"] = tim
        params["where[or][1][code][like]"] = tim
        params["where[or][2][nickname][like]"] = tim
    if trang_thai:
        params["where[enrollmentStatus][equals]"] = trang_thai
    docs, tong = await _docs(spec, "students", params)
    return docs, tong


async def _mot_hoc_vien(spec, tim):
    docs, _ = await _tim_hoc_vien(spec, tim, gioi_han=5)
    if not docs:
        return None, f"không tìm thấy học viên nào khớp '{tim}'"
    if len(docs) > 1:
        ten = ", ".join(f"{d.get('fullName')} ({d.get('code')})" for d in docs[:5])
        return None, f"'{tim}' khớp nhiều em: {ten}. Hãy hỏi lại cho rõ hoặc dùng mã học viên."
    return docs[0], ""


def _lich_lop(lop):
    ra = []
    for b in lop.get("lichHoc") or []:
        thu = b.get("thu") or ""
        gio = f"{b.get('gioBatDau') or ''}-{b.get('gioKetThuc') or ''}".strip("-")
        phong = b.get("phong")
        ra.append(" ".join(x for x in (thu, gio, f"({phong})" if phong else "") if x))
    return ra


def _bang_xep_hang(state):
    """Xếp hạng theo đúng luật app bốc thăm: điểm, Buchholz Cut-1, Buchholz, hệ số.

    Bye cộng 1 điểm nhưng KHÔNG sinh đối thủ ảo - đây là đơn giản hoá có chủ ý của
    app, khác FIDE. Giữ y hệt để hai bên không bao giờ ra hai bảng khác nhau.
    """
    ky_thu = {p.get("id"): p for p in (state.get("players") or []) if p.get("id") is not None}
    diem = {i: 0.0 for i in ky_thu}
    doi_thu = {i: [] for i in ky_thu}

    for rnd in state.get("results") or []:
        for b in rnd.get("boards") or []:
            w, d, kq = b.get("white"), b.get("black"), b.get("w")
            if w not in ky_thu or d not in ky_thu:
                continue
            doi_thu[w].append(d)
            doi_thu[d].append(w)
            if kq == "1":
                diem[w] += 1
            elif kq == "0":
                diem[d] += 1
            elif kq == "=":
                diem[w] += 0.5
                diem[d] += 0.5
        by = rnd.get("bye")
        if by in ky_thu:
            diem[by] += 1

    hang = []
    for i, p in ky_thu.items():
        ds = [diem[o] for o in doi_thu[i]]
        bc = sum(ds)
        hang.append({"ten": p.get("name"), "he_so": p.get("rating"), "diem": diem[i],
                     "buchholz_cut1": round(bc - min(ds), 1) if ds else 0.0,
                     "buchholz": round(bc, 1), "so_van": len(ds)})
    hang.sort(key=lambda x: (-x["diem"], -x["buchholz_cut1"], -x["buchholz"], -_so(x["he_so"])))
    for n, x in enumerate(hang, 1):
        x["hang"] = n
    return hang


async def list_tools(spec):
    return TOOLS


async def call(tool, arguments, spec):
    args = arguments or {}
    try:
        # ---------------- truy vấn chung ----------------
        if tool == "ds_truy_van":
            bang = str(args.get("bang") or "").strip().strip("/")
            if not bang:
                return "ERROR: thiếu tên bảng"
            if bang in _DENY:
                return (f"ERROR: bảng '{bang}' không được phép đọc qua cầu nối này "
                        "(chứa mật khẩu, token hoặc mã OTP).")
            params = {"limit": _gioi_han(args), "depth": 1,
                      "page": max(1, int(args.get("trang") or 1))}
            if args.get("sap_xep"):
                params["sort"] = str(args["sap_xep"])
            if args.get("loc"):
                try:
                    loc = json.loads(args["loc"]) if isinstance(args["loc"], str) else args["loc"]
                except ValueError:
                    return "ERROR: 'loc' không phải JSON hợp lệ"
                for truong, dk in (loc or {}).items():
                    if isinstance(dk, dict):
                        for op, val in dk.items():
                            params[f"where[{truong}][{op}]"] = val
                    else:
                        params[f"where[{truong}][equals]"] = dk
            docs, tong = await _docs(spec, bang, params)
            truong = [x.strip() for x in str(args.get("truong") or "").split(",") if x.strip()]
            if truong:
                docs = [_pick(d, truong) for d in docs]
            else:
                docs = [{k: _flat(v) for k, v in d.items() if _flat(v) not in (None, "", [], {})}
                        for d in docs]
            return _clip(json.dumps({"tong": tong, "ket_qua": docs}, ensure_ascii=False))

        # ---------------- học viên ----------------
        if tool == "ds_hoc_vien":
            docs, tong = await _tim_hoc_vien(spec, args.get("tim"), _gioi_han(args),
                                             str(args.get("trang_thai") or "").strip())
            return _clip(json.dumps(
                {"tong": tong, "hoc_vien": [_pick(d, _HV_TRUONG) for d in docs]},
                ensure_ascii=False))

        # ---------------- học phí ----------------
        if tool == "ds_hoc_phi":
            gh = _gioi_han(args)
            tim = (args.get("hoc_vien") or "").strip()
            if tim:
                hv, loi = await _mot_hoc_vien(spec, tim)
                if loi:
                    return f"ERROR: {loi}"
                ky, _ = await _docs(spec, "tuition-cycles", {
                    "limit": gh, "depth": 1, "sort": "-startDate",
                    "where[student][equals]": hv.get("id")})
                nop, _ = await _docs(spec, "payments", {
                    "limit": gh, "depth": 1, "sort": "-ngayNop",
                    "where[student][equals]": hv.get("id")})
                return _clip(json.dumps({
                    "hoc_vien": _pick(hv, ["code", "fullName", "enrollmentStatus", "location"]),
                    "chu_ky": [dict(_pick(k, ["package", "sessionsTotal", "sessionsUsed",
                                              "startDate", "expectedEndDate", "status"]),
                                    con_lai=_so(k.get("sessionsTotal")) - _so(k.get("sessionsUsed")))
                               for k in ky],
                    "da_nop": [_pick(p, ["code", "ngayNop", "hocPhi", "tienSach", "muaKhac",
                                         "soBuoiNop", "tinhTrang", "coSo"]) for p in nop],
                }, ensure_ascii=False))

            ky, tong = await _docs(spec, "tuition-cycles", {
                "limit": gh, "depth": 1, "sort": "expectedEndDate",
                "where[status][equals]": "sap_het"})
            ra = []
            for k in ky:
                ra.append(dict(_pick(k, ["student", "package", "sessionsTotal", "sessionsUsed",
                                         "expectedEndDate", "status"]),
                               con_lai=_so(k.get("sessionsTotal")) - _so(k.get("sessionsUsed"))))
            ra.sort(key=lambda x: x["con_lai"])
            return _clip(json.dumps({"tong_sap_het": tong, "sap_het_buoi": ra}, ensure_ascii=False))

        # ---------------- điểm danh ----------------
        if tool == "ds_diem_danh":
            gh = _gioi_han(args, 50)
            params = {"limit": gh, "depth": 1, "sort": "-date"}
            tim = (args.get("hoc_vien") or "").strip()
            if tim:
                hv, loi = await _mot_hoc_vien(spec, tim)
                if loi:
                    return f"ERROR: {loi}"
                params["where[student][equals]"] = hv.get("id")
            if args.get("tu_ngay"):
                params["where[date][greater_than_equal]"] = str(args["tu_ngay"])
            if args.get("den_ngay"):
                params["where[date][less_than_equal]"] = str(args["den_ngay"])
            docs, tong = await _docs(spec, "attendance", params)
            thong_ke = {}
            for d in docs:
                tt = d.get("status") or "khong_ro"
                thong_ke[tt] = thong_ke.get(tt, 0) + 1
            return _clip(json.dumps({
                "tong": tong, "thong_ke": thong_ke,
                "buoi": [_pick(d, ["date", "student", "lop", "coach", "status", "lamBTVN",
                                   "yThuc", "nhanXet", "kienThucMoi", "giaoBTVN"]) for d in docs],
            }, ensure_ascii=False))

        # ---------------- lớp ----------------
        if tool == "ds_lop":
            params = {"limit": _gioi_han(args), "depth": 1, "sort": "title"}
            if args.get("tim"):
                params["where[title][like]"] = str(args["tim"])
            if args.get("trang_thai"):
                params["where[trangThai][equals]"] = str(args["trang_thai"])
            docs, tong = await _docs(spec, "classes", params)
            ra = [dict(_pick(d, ["title", "level", "track", "ageGroup", "location", "coach",
                                 "troGiang", "siSoHienTai", "siSoToiDa", "trangThai"]),
                       lich_hoc=_lich_lop(d)) for d in docs]
            return _clip(json.dumps({"tong": tong, "lop": ra}, ensure_ascii=False))

        # ---------------- báo cáo KPI ----------------
        if tool == "ds_bao_cao":
            params = {}
            if args.get("so_tuan"):
                params["weeks"] = max(1, min(int(args["so_tuan"]), 52))
            return _clip(json.dumps(await _get(spec, "/api/crm/report", params),
                                    ensure_ascii=False))

        # ---------------- giải đấu ----------------
        if tool == "ds_giai_dau":
            giai = (args.get("giai") or "").strip()
            if not giai:
                docs, tong = await _docs(spec, "pairing-tournaments", {
                    "limit": _gioi_han(args), "depth": 0, "sort": "-updatedAt"})
                return _clip(json.dumps({"tong": tong, "giai": [
                    {"ma": d.get("tid"), "ten": d.get("name"),
                     "cap_nhat": d.get("updatedAt"),
                     "so_ky_thu": len(((d.get("state") or {}).get("players")) or []),
                     "so_vong_da_dau": len(((d.get("state") or {}).get("results")) or []),
                     "tong_vong": (d.get("state") or {}).get("totalRounds")}
                    for d in docs]}, ensure_ascii=False))
            docs, _ = await _docs(spec, "pairing-tournaments", {
                "limit": 1, "depth": 0, "where[tid][equals]": giai})
            if not docs:
                return f"ERROR: không có giải nào mã '{giai}'"
            st = docs[0].get("state") or {}
            return _clip(json.dumps({
                "ma": docs[0].get("tid"), "ten": st.get("name"),
                "the_thuc": st.get("system"), "tong_vong": st.get("totalRounds"),
                "da_dau": len(st.get("results") or []), "ket_thuc": st.get("finished"),
                "bang_xep_hang": _bang_xep_hang(st),
            }, ensure_ascii=False))

        # ---------------- bốc thăm ----------------
        if tool == "ds_boc_tham":
            he = str(args.get("he") or "--dutch")
            if he not in ("--dutch", "--burstein"):
                return "ERROR: 'he' chỉ nhận --dutch hoặc --burstein"
            pair = _pair_base(spec)
            if not pair:
                return "ERROR: chưa khai địa chỉ app bốc thăm - sửa ở trang Kết nối"
            core, s = _base(spec)
            async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
                if (args.get("trf") or "").strip():
                    # Hàm thuần: TRF vào, cặp đấu ra. Không đụng dữ liệu, không cần đăng nhập.
                    r = await client.post(f"{pair}/api/pair",
                                          json={"system": he, "trf": args["trf"]})
                else:
                    giai = (args.get("giai") or "").strip()
                    if not giai:
                        return "ERROR: cần 'giai' (mã giải) hoặc 'trf'"
                    tok = await _token(client, core, s)
                    r = await client.post(
                        f"{pair}/api/tournaments/{giai}/pair", json={"system": he},
                        headers={"Authorization": f"JWT {tok}", "Cookie": f"payload-token={tok}"})
                if r.status_code >= 400:
                    return f"ERROR: app bốc thăm trả {r.status_code}: {(r.text or '')[:300]}"
                try:
                    return _clip(json.dumps(r.json(), ensure_ascii=False))
                except ValueError:
                    return _clip(r.text or "(rỗng)")

        return f"ERROR: tool '{tool}' không tồn tại trong cầu nối Dương Sinh"

    except RuntimeError as e:
        return f"ERROR: {e}"
    except httpx.HTTPError as e:
        return f"ERROR: không gọi được lõi Dương Sinh: {type(e).__name__}: {e}"
    except Exception as e:
        return f"ERROR: cầu nối Dương Sinh lỗi: {type(e).__name__}: {e}"
