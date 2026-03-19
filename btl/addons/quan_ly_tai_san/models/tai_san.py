# -*- coding: utf-8 -*-
from odoo import models, fields, api


class TaiSan(models.Model):
    _name = 'tai_san'
    _description = 'Hồ sơ tài sản'
    _rec_name = 'ten_tai_san'

    ma_tai_san = fields.Char("Mã tài sản", required=True)
    ten_tai_san = fields.Char("Tên tài sản", required=True)
    danh_muc_id = fields.Many2one('danh_muc_tai_san', string="Danh mục", required=True)
    hinh_anh = fields.Binary("Hình ảnh")
    ngay_mua = fields.Date("Ngày mua")
    gia_tri = fields.Float("Giá trị (VNĐ)")
    vi_tri = fields.Char("Vị trí lưu trữ")
    mo_ta = fields.Text("Mô tả chi tiết")

    trang_thai = fields.Selection([
        ('san_sang', 'Sẵn sàng'),
        ('dang_muon', 'Đang cho mượn'),
        ('bao_tri', 'Đang bảo trì'),
        ('hong', 'Hỏng'),
        ('mat', 'Mất'),
    ], string="Trạng thái", default='san_sang', required=True)

    # Liên kết
    muon_tai_san_ids = fields.One2many('muon_tai_san', 'tai_san_id', string="Lịch sử mượn")
    bao_tri_ids = fields.One2many('bao_tri_tai_san', 'tai_san_id', string="Lịch sử bảo trì")
    su_co_ids = fields.One2many('su_co_tai_san', 'tai_san_id', string="Sự cố")

    _sql_constraints = [
        ('ma_tai_san_unique', 'unique(ma_tai_san)', 'Mã tài sản đã tồn tại!')
    ]
