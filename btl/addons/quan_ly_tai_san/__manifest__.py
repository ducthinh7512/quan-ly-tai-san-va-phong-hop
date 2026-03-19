# -*- coding: utf-8 -*-
{
    'name': "Quản lý Tài sản",

    'summary': "Quản lý tài sản, cho mượn thiết bị, bảo trì và báo sự cố",

    'description': """
        Module quản lý tài sản bao gồm:
        - Hồ sơ tài sản (danh mục, thông tin chi tiết, trạng thái)
        - Lập lịch mượn tài sản (workflow: Yêu cầu → Duyệt → Đang mượn → Đã trả)
        - Bảo trì tài sản
        - Báo mất/hỏng tài sản
        - Tích hợp với module Nhân sự và Phòng họp
    """,

    'author': "BTL Nhóm",
    'website': "",
    'category': 'Inventory',
    'version': '15.0.1.0.0',

    'depends': ['base', 'nhan_su'],

    'data': [
        'security/ir.model.access.csv',
        'views/danh_muc_tai_san.xml',
        'views/tai_san.xml',
        'views/muon_tai_san.xml',
        'views/bao_tri_tai_san.xml',
        'views/su_co_tai_san.xml',
        'views/nhan_vien_inherit.xml',
        'views/menu.xml',
        'data/demo_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
}
