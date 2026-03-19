# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DatPhong(models.Model):
    _name = 'dat_phong'
    _description = 'Đặt phòng họp'
    _order = 'thoi_gian_bat_dau desc'

    phong_hop_id = fields.Many2one('phong_hop', string="Phòng họp", required=True)
    nhan_vien_id = fields.Many2one('nhan_vien', string="Người đặt", required=True)
    thoi_gian_bat_dau = fields.Datetime("Thời gian bắt đầu", required=True)
    thoi_gian_ket_thuc = fields.Datetime("Thời gian kết thúc", required=True)
    so_nguoi = fields.Integer("Số người tham gia", required=True)
    muc_dich = fields.Char("Mục đích sử dụng")
    ghi_chu = fields.Text("Ghi chú")

    trang_thai = fields.Selection([
        ('nhap', 'Nháp'),
        ('da_duyet', 'Đã duyệt'),
        ('dang_su_dung', 'Đang sử dụng'),
        ('hoan_thanh', 'Hoàn thành'),
        ('huy', 'Hủy'),
    ], string="Trạng thái", default='nhap', required=True)

    canh_bao_suc_chua = fields.Char(
        "Cảnh báo sức chứa", compute='_compute_canh_bao', store=False)

    @api.depends('so_nguoi', 'phong_hop_id', 'phong_hop_id.suc_chua')
    def _compute_canh_bao(self):
        for rec in self:
            if rec.phong_hop_id and rec.so_nguoi:
                suc_chua = rec.phong_hop_id.suc_chua
                if rec.so_nguoi > suc_chua:
                    rec.canh_bao_suc_chua = "⚠️ Phòng chỉ chứa %d người, bạn cần %d!" % (suc_chua, rec.so_nguoi)
                elif rec.so_nguoi < suc_chua * 0.3:
                    rec.canh_bao_suc_chua = "💡 Phòng quá rộng (%d chỗ) cho %d người. Nên chọn phòng nhỏ hơn." % (suc_chua, rec.so_nguoi)
                else:
                    rec.canh_bao_suc_chua = ""
            else:
                rec.canh_bao_suc_chua = ""

    @api.constrains('thoi_gian_bat_dau', 'thoi_gian_ket_thuc')
    def _check_thoi_gian(self):
        for rec in self:
            if rec.thoi_gian_ket_thuc <= rec.thoi_gian_bat_dau:
                raise ValidationError("Thời gian kết thúc phải sau thời gian bắt đầu!")

    @api.constrains('so_nguoi', 'phong_hop_id')
    def _check_suc_chua(self):
        for rec in self:
            if rec.phong_hop_id and rec.so_nguoi > rec.phong_hop_id.suc_chua:
                raise ValidationError(
                    "Số người (%d) vượt quá sức chứa phòng %s (%d người)!" %
                    (rec.so_nguoi, rec.phong_hop_id.ten_phong, rec.phong_hop_id.suc_chua))

    @api.constrains('phong_hop_id', 'thoi_gian_bat_dau', 'thoi_gian_ket_thuc', 'trang_thai')
    def _check_xung_dot_lich(self):
        for rec in self:
            if rec.trang_thai in ('huy', 'hoan_thanh'):
                continue
            trung_lich = self.search([
                ('phong_hop_id', '=', rec.phong_hop_id.id),
                ('id', '!=', rec.id),
                ('trang_thai', 'not in', ['huy', 'hoan_thanh']),
                ('thoi_gian_bat_dau', '<', rec.thoi_gian_ket_thuc),
                ('thoi_gian_ket_thuc', '>', rec.thoi_gian_bat_dau),
            ])
            if trung_lich:
                raise ValidationError(
                    "Phòng %s đã được đặt trong khoảng thời gian này! "
                    "Trùng với đặt phòng của: %s" %
                    (rec.phong_hop_id.ten_phong,
                     ', '.join(trung_lich.mapped('nhan_vien_id.ho_ten'))))

    def action_duyet(self):
        for rec in self:
            rec.trang_thai = 'da_duyet'

    def action_bat_dau(self):
        for rec in self:
            rec.trang_thai = 'dang_su_dung'
            rec.phong_hop_id.trang_thai = 'dang_su_dung'

    def action_hoan_thanh(self):
        for rec in self:
            rec.trang_thai = 'hoan_thanh'
            # Kiểm tra xem còn đặt phòng đang sử dụng không
            other_active = self.search([
                ('phong_hop_id', '=', rec.phong_hop_id.id),
                ('id', '!=', rec.id),
                ('trang_thai', '=', 'dang_su_dung'),
            ])
            if not other_active:
                rec.phong_hop_id.trang_thai = 'san_sang'

    def action_huy(self):
        for rec in self:
            rec.trang_thai = 'huy'
