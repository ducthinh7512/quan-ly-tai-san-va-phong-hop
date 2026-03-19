# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import re
import json
import logging

_logger = logging.getLogger(__name__)

# API Key Gemini - thay bằng key của bạn
GEMINI_API_KEY = "AIzaSyA8NlDl-kUDRPWTYiWTmAEATZYyce18rdg"

# Fallback: Từ khóa tiếng Việt (dùng khi không có API key hoặc lỗi mạng)
TU_KHOA_THIET_BI = {
    'học bài': ['máy chiếu', 'bảng'],
    'học': ['máy chiếu', 'bảng'],
    'thuyết trình': ['máy chiếu', 'loa', 'micro'],
    'trình bày': ['máy chiếu', 'loa', 'micro'],
    'seminar': ['máy chiếu', 'loa', 'micro'],
    'hội thảo': ['máy chiếu', 'loa', 'micro'],
    'họp nhóm': ['bảng'],
    'họp': ['máy chiếu'],
    'thảo luận': ['bảng'],
    'brainstorm': ['bảng'],
    'đào tạo': ['máy chiếu', 'loa', 'micro', 'bảng'],
    'training': ['máy chiếu', 'loa', 'micro', 'bảng'],
    'tập huấn': ['máy chiếu', 'loa', 'micro'],
    'phỏng vấn': [],
    'interview': [],
    'video call': ['camera', 'loa', 'micro'],
    'online': ['camera', 'loa', 'micro'],
    'zoom': ['camera', 'loa', 'micro'],
    'meet': ['camera', 'loa', 'micro'],
    'chiếu phim': ['máy chiếu', 'loa'],
    'xem phim': ['máy chiếu', 'loa'],
}


def _goi_gemini(yeu_cau, danh_sach_phong_info):
    """Gọi Google Gemini API để phân tích yêu cầu đặt phòng"""
    import urllib.request
    import urllib.error

    prompt = """Bạn là AI trợ lý đặt phòng họp. Phân tích yêu cầu sau và trả về JSON.

YÊU CẦU: "%s"

DANH SÁCH PHÒNG HIỆN CÓ:
%s

Trả về JSON (KHÔNG markdown, KHÔNG giải thích, CHỈ JSON):
{
    "muc_dich": "mô tả ngắn gọn mục đích",
    "so_nguoi": <số người cần, 0 nếu không nói>,
    "thiet_bi_can": ["tên thiết bị cần"...],
    "phan_tich": "phân tích chi tiết yêu cầu (2-3 câu tiếng Việt)",
    "goi_y_phong": ["tên phòng gợi ý theo thứ tự ưu tiên"...],
    "ly_do": "lý do chọn phòng đầu tiên (1 câu tiếng Việt)"
}""" % (yeu_cau, danh_sach_phong_info)

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=%s" % GEMINI_API_KEY

    data = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 1000,
        }
    }).encode('utf-8')

    req = urllib.request.Request(url, data=data, headers={
        'Content-Type': 'application/json',
    })

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode('utf-8'))
            text = result['candidates'][0]['content']['parts'][0]['text']
            # Xóa markdown code block nếu có
            text = text.strip()
            if text.startswith('```'):
                text = re.sub(r'^```\w*\n?', '', text)
                text = re.sub(r'\n?```$', '', text)
            return json.loads(text.strip())
    except Exception as e:
        _logger.warning("Gemini API error: %s", str(e))
        return None


class GoiYPhongWizard(models.TransientModel):
    _name = 'goi_y_phong_wizard'
    _description = 'AI Gợi ý phòng họp thông minh'

    yeu_cau = fields.Text(
        "Nhập yêu cầu của bạn",
        help="Ví dụ: 'Phòng thuyết trình 25 người có máy chiếu', 'Tôi cần không gian yên tĩnh phỏng vấn 3 người'")

    so_nguoi = fields.Integer("Số người", default=1)
    thoi_gian_bat_dau = fields.Datetime("Thời gian bắt đầu")
    thoi_gian_ket_thuc = fields.Datetime("Thời gian kết thúc")

    ket_qua_ids = fields.Many2many('phong_hop', string="Phòng gợi ý")
    phong_chon_id = fields.Many2one('phong_hop', string="📌 Phòng đã chọn",
        help="Phòng được AI gợi ý tốt nhất. Bạn có thể đổi sang phòng khác.")
    phan_tich = fields.Text("Phân tích AI", readonly=True)
    da_tim = fields.Boolean("Đã tìm kiếm", default=False)

    def _lay_thong_tin_phong(self):
        """Lấy thông tin tất cả phòng để gửi cho AI"""
        all_phong = self.env['phong_hop'].search([])
        info_lines = []
        for p in all_phong:
            tb = ', '.join(p.thiet_bi_ids.mapped('ten_tai_san')) or 'Không có'
            info_lines.append(
                "- %s: sức chứa %d người, vị trí %s, trạng thái %s, thiết bị: %s" % (
                    p.ten_phong, p.suc_chua, p.vi_tri or 'N/A',
                    dict(p._fields['trang_thai'].selection).get(p.trang_thai, p.trang_thai),
                    tb))
        return '\n'.join(info_lines)

    def _phan_tich_fallback(self, yeu_cau_lower):
        """Phân tích bằng keyword matching (fallback khi không có AI)"""
        thiet_bi_can = set()
        muc_dich_found = []
        for tu_khoa, thiet_bi_list in TU_KHOA_THIET_BI.items():
            if tu_khoa in yeu_cau_lower:
                muc_dich_found.append(tu_khoa)
                for tb in thiet_bi_list:
                    thiet_bi_can.add(tb)
        so_nguoi = self.so_nguoi or 1
        so_match = re.findall(r'(\d+)\s*(?:người|nguoi|ng)', yeu_cau_lower)
        if so_match:
            so_nguoi = int(so_match[0])
        return muc_dich_found, thiet_bi_can, so_nguoi

    def _tinh_diem(self, phong, so_nguoi, thiet_bi_can):
        """Tính điểm phù hợp 0-100"""
        diem = 100
        chenh = phong.suc_chua - so_nguoi
        if chenh > 30:
            diem -= 40
        elif chenh > 20:
            diem -= 25
        elif chenh > 10:
            diem -= 10
        if thiet_bi_can:
            ten_tb = [tb.ten_tai_san.lower() for tb in phong.thiet_bi_ids]
            match_tb = sum(1 for tb in thiet_bi_can if any(tb in ten for ten in ten_tb))
            diem_tb = int(match_tb / len(thiet_bi_can) * 100)
            diem = int((diem + diem_tb) / 2)
        return max(10, min(100, diem))

    def action_goi_y(self):
        """Phân tích yêu cầu và gợi ý phòng — ưu tiên dùng Gemini AI"""
        self.ensure_one()
        if not self.yeu_cau:
            raise UserError("Vui lòng nhập yêu cầu!")

        yeu_cau_lower = self.yeu_cau.lower()
        lines = []
        thiet_bi_can = set()
        so_nguoi = self.so_nguoi or 1
        ai_goi_y_ten = []
        su_dung_ai = False

        # === THỬ GỌI GEMINI AI ===
        if GEMINI_API_KEY and GEMINI_API_KEY != "AIzaSyDemoKeyHere":
            phong_info = self._lay_thong_tin_phong()
            ai_result = _goi_gemini(self.yeu_cau, phong_info)

            if ai_result:
                su_dung_ai = True
                lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                lines.append("🤖  PHÂN TÍCH BỞI GOOGLE GEMINI AI")
                lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                lines.append("")
                lines.append("📝  Yêu cầu: \"%s\"" % self.yeu_cau)
                lines.append("")

                muc_dich = ai_result.get('muc_dich', '')
                phan_tich_text = ai_result.get('phan_tich', '')
                ly_do = ai_result.get('ly_do', '')
                thiet_bi_can = set(ai_result.get('thiet_bi_can', []))
                ai_goi_y_ten = ai_result.get('goi_y_phong', [])

                ai_so_nguoi = ai_result.get('so_nguoi', 0)
                if ai_so_nguoi and ai_so_nguoi > 0:
                    so_nguoi = ai_so_nguoi
                    self.so_nguoi = so_nguoi

                lines.append("📋  Mục đích:      %s" % muc_dich)
                if thiet_bi_can:
                    lines.append("🔧  Thiết bị cần:  %s" % ', '.join(sorted(thiet_bi_can)))
                lines.append("👥  Số người:      %d người" % so_nguoi)
                lines.append("")
                lines.append("🧠  Phân tích AI:")
                lines.append("    %s" % phan_tich_text)
                if ly_do:
                    lines.append("")
                    lines.append("💡  Lý do gợi ý:   %s" % ly_do)

        # === FALLBACK: KEYWORD MATCHING ===
        if not su_dung_ai:
            muc_dich_found, thiet_bi_can, so_nguoi = self._phan_tich_fallback(yeu_cau_lower)
            self.so_nguoi = so_nguoi

            lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            lines.append("🔍  PHÂN TÍCH TỪ KHÓA")
            lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            lines.append("")
            lines.append("📝  Yêu cầu: \"%s\"" % self.yeu_cau)
            if muc_dich_found:
                lines.append("📋  Mục đích:      %s" % ' → '.join(muc_dich_found))
            if thiet_bi_can:
                lines.append("🔧  Thiết bị cần:  %s" % ', '.join(sorted(thiet_bi_can)))
            lines.append("👥  Số người:      %d người" % so_nguoi)
            lines.append("")
            lines.append("⚠️  Đang dùng phân tích từ khóa (chưa cấu hình Gemini API Key)")

        # === TÌM PHÒNG ===
        domain = [
            ('trang_thai', '=', 'san_sang'),
            ('suc_chua', '>=', so_nguoi),
        ]
        phong_list = self.env['phong_hop'].search(domain, order='suc_chua asc')

        # Lọc theo thời gian
        if self.thoi_gian_bat_dau and self.thoi_gian_ket_thuc:
            phong_trong = self.env['phong_hop']
            for phong in phong_list:
                trung = self.env['dat_phong'].search([
                    ('phong_hop_id', '=', phong.id),
                    ('trang_thai', 'not in', ['huy', 'hoan_thanh']),
                    ('thoi_gian_bat_dau', '<', self.thoi_gian_ket_thuc),
                    ('thoi_gian_ket_thuc', '>', self.thoi_gian_bat_dau),
                ])
                if not trung:
                    phong_trong |= phong
            phong_list = phong_trong
            lines.append("🕐  Thời gian:     %s → %s" % (
                str(self.thoi_gian_bat_dau)[:16], str(self.thoi_gian_ket_thuc)[:16]))

        # Xếp hạng phòng
        phong_diem = []
        for phong in phong_list:
            diem = self._tinh_diem(phong, so_nguoi, thiet_bi_can)
            # Bonus nếu AI gợi ý phòng này
            if su_dung_ai and ai_goi_y_ten:
                for idx, ten in enumerate(ai_goi_y_ten):
                    if ten.lower() in phong.ten_phong.lower() or phong.ten_phong.lower() in ten.lower():
                        diem = min(100, diem + 20 - idx * 5)
                        break
            phong_diem.append((phong, diem))

        phong_diem.sort(key=lambda x: x[1], reverse=True)
        phong_sorted_ids = [p.id for p, d in phong_diem]

        # === KẾT QUẢ ===
        lines.append("")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("📊  KẾT QUẢ GỢI Ý")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")

        if phong_diem:
            lines.append("✅ Tìm thấy %d phòng phù hợp:" % len(phong_diem))
            lines.append("")

            for i, (phong, diem) in enumerate(phong_diem[:10], 1):
                tb_names = ', '.join(phong.thiet_bi_ids.mapped('ten_tai_san')) or 'Không có'
                if diem >= 80:
                    rank = "🥇"
                elif diem >= 60:
                    rank = "🥈"
                elif diem >= 40:
                    rank = "🥉"
                else:
                    rank = "▫️"

                lines.append("%s  %d. %s" % (rank, i, phong.ten_phong))
                lines.append("       📍 %s  |  👥 %d chỗ  |  Phù hợp: %d%%" % (
                    phong.vi_tri or 'N/A', phong.suc_chua, diem))
                lines.append("       🔧 %s" % tb_names)
                lines.append("")

            best = phong_diem[0][0]
            lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            lines.append("💡 Gợi ý: Nên chọn \"%s\"" % best.ten_phong)
            lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        else:
            lines.append("❌ Không tìm thấy phòng phù hợp.")
            lines.append("💡 Thử giảm số người hoặc thay đổi thời gian.")

        phong_mac_dinh = phong_sorted_ids[0] if phong_sorted_ids else False

        self.write({
            'ket_qua_ids': [(6, 0, phong_sorted_ids[:10])],
            'phong_chon_id': phong_mac_dinh,
            'phan_tich': '\n'.join(lines),
            'da_tim': True,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'goi_y_phong_wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_dat_phong(self):
        """Tạo đặt phòng từ phòng đã chọn"""
        self.ensure_one()
        if not self.phong_chon_id:
            raise UserError("Vui lòng chọn phòng trước khi đặt!")
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'dat_phong',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_phong_hop_id': self.phong_chon_id.id,
                'default_thoi_gian_bat_dau': self.thoi_gian_bat_dau,
                'default_thoi_gian_ket_thuc': self.thoi_gian_ket_thuc,
                'default_so_nguoi': self.so_nguoi,
                'default_muc_dich': self.yeu_cau,
            },
        }
