# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Price-list Selection Popup',
    'version': '1.0',
    'author': 'Odoo Ps',
    'summary': "To make price-list popup in the website page on load.",
    'depends': ['website', 'website_sale'],
    'data': [
        'views/assets.xml',
        'views/templates_popup.xml',
        'views/product_pricelist.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],

    'installable': True,
    'application': False,
    'auto_install': False,
}
