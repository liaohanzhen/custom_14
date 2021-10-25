# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2020 - Today O4ODOO (Omal Bastin)
#    For more details, check COPYRIGHT and LICENSE files
#
##############################################################################
{
    'name': 'POS Taxable Invoice',
    'version': '12.0.1.1.0',
    'category': 'Custom',
    'summary': "POS Taxable Invoice",
    'author': 'Omal Bastin / O4ODOO',
    'license': 'OPL-1',
    'website': 'http://o4odoo.com',
    'depends': ['base', 'point_of_sale', 'account'],
    'data': [
        'views/template.xml',
    ],
    'qweb': [
        'static/src/xml/texable_button.xml',
    ],
    'demo': [],
    'application': False,
    'installable': True,
    'auto_install': False,
}
