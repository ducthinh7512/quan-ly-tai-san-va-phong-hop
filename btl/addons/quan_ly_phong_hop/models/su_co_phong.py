# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SuCoPhong(models.Model):
    _name = 'su_co_phong'
    _description = 'Sự cố phòng họp khi đang sử dụng'
    _order = 'ngay_bao_cao desc'

    dat_phong_id = fields.Many2one('dat_phong', string="Đặt phòng liên quan", required=True)
    phong_hop_id = fields.Many2one(
        'phong_hop', string="Phòng họp",
        related='dat_phong_id.phong_hop_id', store=True)
    nhan_vien_bao_cao = fields.Many2one('nhan_vien', string="Người báo cáo", required=True)
    ngay_bao_cao = fields.Datetime("Ngày báo cáo", default=fields.Datetime.now, required=True)
    mo_ta = fields.Text("Mô tả sự cố", required=True)

    thiet_bi_hong = fields.Many2one('tai_san', string="Thiết bị bị hỏng")

    xu_ly = fields.Selection([
        ('doi_phong', 'Đổi phòng'),
        ('sua_chua', 'Gọi nhân viên sửa chữa'),
    ], string="Cách xử lý")

    trang_thai = fields.Selection([
        ('moi', 'Mới báo'),
        ('dang_xu_ly', 'Đang xử lý'),
        ('da_xu_ly', 'Đã xử lý'),
    ], string="Trạng thái", default='moi', required=True)

    phong_moi_id = fields.Many2one('phong_hop', string="Phòng đổi sang")
    nhan_vien_sua = fields.Many2one('nhan_vien', string="Nhân viên sửa chữa")

    def action_doi_phong(self):
        """Đổi sang phòng mới - mở wizard gợi ý phòng"""
        for rec in self:
            rec.xu_ly = 'doi_phong'
            rec.trang_thai = 'dang_xu_ly'

    def action_goi_sua_chua(self):
        """Gọi nhân viên sửa chữa"""
        for rec in self:
            rec.xu_ly = 'sua_chua'
            rec.trang_thai = 'dang_xu_ly'
            # Tạo yêu cầu bảo trì cho thiết bị
            if rec.thiet_bi_hong:
                self.env['bao_tri_tai_san'].create({
                    'tai_san_id': rec.thiet_bi_hong.id,
                    'mo_ta': 'Sự cố tại phòng %s: %s' % (rec.phong_hop_id.ten_phong, rec.mo_ta),
                    'nhan_vien_phu_trach': rec.nhan_vien_sua.id if rec.nhan_vien_sua else False,
                })
                rec.thiet_bi_hong.trang_thai = 'hong'

    def action_hoan_thanh(self):
        for rec in self:
            rec.trang_thai = 'da_xu_ly'
