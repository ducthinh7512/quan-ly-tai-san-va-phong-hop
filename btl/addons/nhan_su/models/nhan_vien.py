from odoo import models, fields, api


class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Quản lý thông tin nhân viên'
    _rec_name = 'ho_ten'

    # Thông tin cơ bản
    ma_dinh_danh = fields.Char("Mã định danh", required=True)
    ho_ten = fields.Char("Họ và tên", required=True)
    ngay_sinh = fields.Date("Ngày sinh")
    gioi_tinh = fields.Selection([
        ('nam', 'Nam'),
        ('nu', 'Nữ'),
        ('khac', 'Khác'),
    ], string="Giới tính")
    hinh_anh = fields.Binary("Hình ảnh")
    que_quan = fields.Char("Quê quán")
    dia_chi = fields.Char("Địa chỉ")

    # Liên hệ
    email = fields.Char("Email")
    so_dien_thoai = fields.Char("Số điện thoại")

    # Tổ chức
    phong_ban_id = fields.Many2one('phong_ban', string="Phòng ban")
    chuc_vu_id = fields.Many2one('chuc_vu', string="Chức vụ")

    # Liên kết với module Tài sản và Phòng họp
    # (fields được thêm tự động khi cài module tương ứng qua _inherit)

    _sql_constraints = [
        ('ma_dinh_danh_unique', 'unique(ma_dinh_danh)', 'Mã định danh đã tồn tại!')
    ]
