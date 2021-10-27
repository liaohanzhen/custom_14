# -*- coding: utf-8 -*-
{
    'name': "MVP Project 5B",

    'summary': """
        MVP Project 5B""",

    'description': """
        MVP Project 5B
    """,

    'author': "Lekha Paudel",
    'website': "http://www.5b.com.au",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Website',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website', 'mail', 'web', 'http_routing'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/projectapi.xml',
        'views/view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}