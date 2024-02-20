# -*- coding: utf-8 -*-
{
    'name': "XC Smart 2fa",

    'summary': """
        Starting module for "Discover the JS framework, chapter 2: Build a dashboard"
    """,

    'description': """
        Starting module for "Discover the JS framework, chapter 2: Build a dashboard"
    """,

    'author': "Odoo",
    'website': "https://www.odoo.com/",
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
    'license': 'AGPL-3'
}
