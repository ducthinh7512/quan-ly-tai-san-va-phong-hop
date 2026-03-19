# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SuCoTaiSan(models.Model):
    _name = 'su_co_tai_san'
    _description = 'Báo mất / hỏng tài sản'
    _order = 'ngay_bao_cao desc'

    tai_san_id = fields.Many2one('tai_san', string="Tài sản", required=True)
    nhan_vien_bao_cao = fields.Many2one('nhan_vien', string="Người báo cáo", required=True)
    ngay_bao_cao = fields.Date("Ngày báo cáo", default=fields.Date.today, required=True)
    mo_ta = fields.Text("Mô tả sự cố")

    loai_su_co = fields.Selection([
        ('hong', 'Hỏng'),
        ('mat', 'Mất'),
    ], string="Loại sự cố", required=True)

    trang_thai = fields.Selection([
        ('moi', 'Mới báo'),
        ('dang_xu_ly', 'Đang xử lý'),
        ('da_xu_ly', 'Đã xử lý'),
    ], string="Trạng thái", default='moi', required=True)

    hanh_dong = fields.Selection([
        ('sua_chua', 'Gửi sửa chữa'),
        ('thay_the', 'Thay thế mới'),
        ('thanh_ly', 'Thanh lý'),
    ], string="Hành động xử lý")

    def action_xu_ly(self):
        for rec in self:
            rec.trang_thai = 'dang_xu_ly'
            if rec.loai_su_co == 'hong':
                rec.tai_san_id.trang_thai = 'hong'
            elif rec.loai_su_co == 'mat':
                rec.tai_san_id.trang_thai = 'mat'

    def action_hoan_thanh(self):
        for rec in self:
            rec.trang_thai = 'da_xu_ly'
            if rec.hanh_dong == 'sua_chua':
                rec.tai_san_id.trang_thai = 'san_sang'
