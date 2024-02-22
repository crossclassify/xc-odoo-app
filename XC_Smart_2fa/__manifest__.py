# -*- coding: utf-8 -*-
{
    'name': "Smart 2FA",

    'summary': """
        Secure your Odoo platform by using Smart 2FA.
    """,

    'description': """
        Secure your Odoo platform by using Smart 2FA.
    """,

    'author': "CrossClassify",
    'website': "https://www.crossclassify.com/",
    'category': '',
    'version': '1.0',
    'application': True,
    'installable': True,
    'depends': ['base', 'web'],

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/custome_login.xml',
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'XC_Smart_2FA/static/src/**/*',
        ],
    },
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3'
}
