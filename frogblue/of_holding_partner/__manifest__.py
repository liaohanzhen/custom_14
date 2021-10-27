# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'openfellas Holding partner',
    'author': 'openfellas',
    'version': '14.0',
    'summary': 'openfellas extension to link companies',
    'description': """openfellas extension to link companies and report sale revenue based on holdings""",
    'category': 'All',
    'website': 'http://openfellas.com/',
    'depends': ['sale_management'],
    'data': [
        "translations.sql",
        'views/res_partner_views.xml',
        'views/sale_report_views.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
}
