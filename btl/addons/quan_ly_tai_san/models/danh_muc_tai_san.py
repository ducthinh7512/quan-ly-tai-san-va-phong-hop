# -*- coding: utf-8 -*-
from odoo import models, fields, api


class DanhMucTaiSan(models.Model):
    _name = 'danh_muc_tai_san'
    _description = 'Danh mục tài sản'
    _rec_name = 'ten_danh_muc'

    ma_danh_muc = fields.Char("Mã danh mục", required=True)
    ten_danh_muc = fields.Char("Tên danh mục", required=True)
    mo_ta = fields.Text("Mô tả")
    tai_san_ids = fields.One2many('tai_san', 'danh_muc_id', string="Danh sách tài sản")

    _sql_constraints = [
        ('ma_danh_muc_unique', 'unique(ma_danh_muc)', 'Mã danh mục đã tồn tại!')
    ]
