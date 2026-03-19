# -*- coding: utf-8 -*-
from odoo import models, fields


class NhanVienPhongHop(models.Model):
    _inherit = 'nhan_vien'

    dat_phong_ids = fields.One2many(
        'dat_phong', 'nhan_vien_id',
        string="Lịch đặt phòng")
