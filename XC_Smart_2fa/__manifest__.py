# -*- coding: utf-8 -*-
{
    'name': "XC Smart 2fa",

    'summary': """
        Secure your Odoo platform by using Smart 2FA.
    """,

    'description': """
        Secure your Odoo platform by using Smart 2FA.
    """,

    'author': "CrossClassify",
    'website': "https://www.crossclassify.com/",
    'category': 'Tutorials/AwesomeDashboard',
    'version': '3.0',
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
            'smart_2fa/static/src/**/*',
        ],
    },
    'license': 'Apache-2.0'
}
