# -*- coding: utf-8 -*-
{
    'name': "Quản lý Nhân sự",

    'summary': "Quản lý thông tin nhân viên, phòng ban, chức vụ",

    'description': """
        Module quản lý nhân sự bao gồm:
        - Quản lý thông tin nhân viên
        - Quản lý phòng ban
        - Quản lý chức vụ
        - Tích hợp với module Tài sản và Phòng họp
    """,

    'author': "BTL Nhóm",
    'website': "",
    'category': 'Human Resources',
    'version': '15.0.1.0.0',

    'depends': ['base'],

    'data': [
        'security/ir.model.access.csv',
        'views/phong_ban.xml',
        'views/chuc_vu.xml',
        'views/nhan_vien.xml',
        'views/menu.xml',
        'data/demo_data.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
}
