# -*- coding: utf-8 -*-
from odoo import models, fields, api


class KiemTraPhong(models.Model):
    _name = 'kiem_tra_phong'
    _description = 'Kiểm tra phòng sau khi trả'
    _order = 'ngay_kiem_tra desc'

    dat_phong_id = fields.Many2one('dat_phong', string="Đặt phòng liên quan", required=True)
    phong_hop_id = fields.Many2one(
        'phong_hop', string="Phòng họp",
        related='dat_phong_id.phong_hop_id', store=True)
    nhan_vien_kiem_tra = fields.Many2one('nhan_vien', string="Người kiểm tra", required=True)
    ngay_kiem_tra = fields.Datetime("Ngày kiểm tra", default=fields.Datetime.now, required=True)
    ghi_chu = fields.Text("Ghi chú chung")

    ket_qua = fields.Selection([
        ('dat', 'Đạt - Đầy đủ thiết bị'),
        ('thieu', 'Thiếu thiết bị'),
        ('hong', 'Có thiết bị hỏng'),
    ], string="Kết quả kiểm tra", required=True, default='dat')

    chi_tiet_ids = fields.One2many('kiem_tra_phong_chi_tiet', 'kiem_tra_id', string="Chi tiết kiểm tra")


class KiemTraPhongChiTiet(models.Model):
    _name = 'kiem_tra_phong_chi_tiet'
    _description = 'Chi tiết kiểm tra từng thiết bị'

    kiem_tra_id = fields.Many2one('kiem_tra_phong', string="Biên bản kiểm tra", required=True)
    tai_san_id = fields.Many2one('tai_san', string="Thiết bị", required=True)

    trang_thai = fields.Selection([
        ('tot', 'Tốt'),
        ('hong', 'Hỏng'),
        ('mat', 'Mất'),
    ], string="Tình trạng", required=True, default='tot')

    ghi_chu = fields.Char("Ghi chú")
