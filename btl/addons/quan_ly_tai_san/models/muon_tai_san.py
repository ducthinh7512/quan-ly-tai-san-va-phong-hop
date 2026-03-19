# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class MuonTaiSan(models.Model):
    _name = 'muon_tai_san'
    _description = 'Lập lịch mượn tài sản'
    _order = 'ngay_muon desc'

    tai_san_id = fields.Many2one('tai_san', string="Tài sản", required=True)
    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân viên mượn", required=True)
    ngay_muon = fields.Date("Ngày mượn", default=fields.Date.today, required=True)
    ngay_tra_du_kien = fields.Date("Ngày trả dự kiến", required=True)
    ngay_tra_thuc_te = fields.Date("Ngày trả thực tế")
    ghi_chu = fields.Text("Ghi chú")

    trang_thai = fields.Selection([
        ('yeu_cau', 'Yêu cầu'),
        ('da_duyet', 'Đã duyệt'),
        ('dang_muon', 'Đang mượn'),
        ('da_tra', 'Đã trả'),
        ('huy', 'Hủy'),
    ], string="Trạng thái", default='yeu_cau', required=True)

    @api.constrains('ngay_muon', 'ngay_tra_du_kien')
    def _check_ngay(self):
        for rec in self:
            if rec.ngay_tra_du_kien and rec.ngay_muon and rec.ngay_tra_du_kien < rec.ngay_muon:
                raise ValidationError("Ngày trả dự kiến phải sau ngày mượn!")

    def action_duyet(self):
        for rec in self:
            if rec.tai_san_id.trang_thai != 'san_sang':
                raise ValidationError("Tài sản không ở trạng thái sẵn sàng!")
            rec.trang_thai = 'da_duyet'

    def action_giao(self):
        for rec in self:
            rec.trang_thai = 'dang_muon'
            rec.tai_san_id.trang_thai = 'dang_muon'

    def action_tra(self):
        for rec in self:
            rec.trang_thai = 'da_tra'
            rec.ngay_tra_thuc_te = fields.Date.today()
            rec.tai_san_id.trang_thai = 'san_sang'

    def action_huy(self):
        for rec in self:
            if rec.trang_thai == 'dang_muon':
                rec.tai_san_id.trang_thai = 'san_sang'
            rec.trang_thai = 'huy'
