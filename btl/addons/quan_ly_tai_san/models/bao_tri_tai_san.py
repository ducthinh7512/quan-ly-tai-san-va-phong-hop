# -*- coding: utf-8 -*-
from odoo import models, fields, api


class BaoTriTaiSan(models.Model):
    _name = 'bao_tri_tai_san'
    _description = 'Bảo trì tài sản'
    _order = 'ngay_bao_tri desc'

    tai_san_id = fields.Many2one('tai_san', string="Tài sản", required=True)
    ngay_bao_tri = fields.Date("Ngày bảo trì", default=fields.Date.today, required=True)
    ngay_hoan_thanh = fields.Date("Ngày hoàn thành")
    chi_phi = fields.Float("Chi phí (VNĐ)")
    mo_ta = fields.Text("Mô tả công việc")
    nhan_vien_phu_trach = fields.Many2one('nhan_vien', string="Nhân viên phụ trách")

    trang_thai = fields.Selection([
        ('cho_xu_ly', 'Chờ xử lý'),
        ('dang_bao_tri', 'Đang bảo trì'),
        ('hoan_thanh', 'Hoàn thành'),
    ], string="Trạng thái", default='cho_xu_ly', required=True)

    def action_bat_dau(self):
        for rec in self:
            rec.trang_thai = 'dang_bao_tri'
            rec.tai_san_id.trang_thai = 'bao_tri'

    def action_hoan_thanh(self):
        for rec in self:
            rec.trang_thai = 'hoan_thanh'
            rec.ngay_hoan_thanh = fields.Date.today()
            rec.tai_san_id.trang_thai = 'san_sang'
