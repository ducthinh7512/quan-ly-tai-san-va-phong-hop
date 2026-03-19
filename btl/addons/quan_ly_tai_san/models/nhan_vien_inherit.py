# -*- coding: utf-8 -*-
from odoo import models, fields


class NhanVienTaiSan(models.Model):
    _inherit = 'nhan_vien'

    muon_tai_san_ids = fields.One2many(
        'muon_tai_san', 'nhan_vien_id',
        string="Tài sản đang mượn")
