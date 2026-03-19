# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PhongHop(models.Model):
    _name = 'phong_hop'
    _description = 'Quản lý Phòng họp'
    _rec_name = 'ten_phong'

    ma_phong = fields.Char("Mã phòng", required=True)
    ten_phong = fields.Char("Tên phòng", required=True)
    vi_tri = fields.Char("Vị trí (tầng, tòa nhà)")
    suc_chua = fields.Integer("Sức chứa (người)", required=True)
    mo_ta = fields.Text("Mô tả")
    hinh_anh = fields.Binary("Hình ảnh")

    trang_thai = fields.Selection([
        ('san_sang', 'Sẵn sàng'),
        ('dang_su_dung', 'Đang sử dụng'),
        ('bao_tri', 'Đang bảo trì'),
    ], string="Trạng thái", default='san_sang', required=True)

    # Thiết bị phòng họp (liên kết với tài sản)
    thiet_bi_ids = fields.Many2many(
        'tai_san', string="Thiết bị trong phòng",
        help="Danh sách thiết bị (máy chiếu, bảng trắng, loa...) thuộc phòng này")

    # Lịch đặt phòng
    dat_phong_ids = fields.One2many('dat_phong', 'phong_hop_id', string="Lịch đặt phòng")

    _sql_constraints = [
        ('ma_phong_unique', 'unique(ma_phong)', 'Mã phòng đã tồn tại!')
    ]
