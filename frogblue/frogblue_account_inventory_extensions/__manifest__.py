# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Frogblue Acc.Inventory Extensions",
    "version": "14.0",
    "depends": [
        'account',
        'account_accountant',
        'stock',
        'stock_account'
    ],
    "author": "Openfellas",
    "website": "http://www.openfellas.com",
    "category": "Extensions",
    "summary": "Account Inventory Extensions",
    "description": """
        This module provides account inventory extensions for Frogblue project
    """,
    "data": [
        'translations.sql',
        "views/account_move_view.xml",
        "views/account_move_line_view.xml",
    ],
    "qweb": [
    ]
}
