# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Frogblue Reports",
    "version": "14.0.0.0.7",
    "depends": [
        'base',
        'sale',
        'account',
        'purchase',
        'frogblue_extensions'
    ],
    "author": "Openfellas",
    "website": "http://www.openfellas.com",
    "category": "Reports",
    "description": """
        This module provides custom reports for Frogblue project
    """,
    "data": [
        'views/frogblue_reports.xml',
        'views/layouts.xml',
        'views/sale_order_report.xml',
        'views/sale_order_proforma_report.xml',
        'views/delivery_note_report.xml',
        'views/pick_list_report.xml',
        'views/account_invoice_report.xml',
        'views/purchase_order_report.xml',
        'views/stock_picking_view.xml',
        'views/account_fiscal_position_view.xml',
        'views/res_company_view.xml',
    ],
    "qweb": [
    ]
}
