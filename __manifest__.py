# -*- coding: utf-8 -*-
{
    'name': "Smart 2FA",

    'summary': """
        Smarter two factor authentication (2FA) using AI without any SMS, email or third party app!
    """,

    'description': """
        Smarter two factor authentication (2FA) using AI without any SMS, email or third party app!
    """,

    'author': "CrossClassify",
    'website': "https://www.crossclassify.com/",
    'category': '',
    'version': '1.5',
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
            'cc_smart_2fa/static/src/**/*',
        ],
    },
    'external_dependencies': {
        'python': ['pyotp', 'pyqrcode', 'io'],
    },
    'images': ['static/description/banner.png'],
    'license': 'LGPL-3'
}
