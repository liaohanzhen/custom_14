# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Frogblue multi serials scan",
    "version": "14.0",
    "depends": ['stock_barcode'],
    "author": "Openfellas",
    "website": "http://www.openfellas.com",
    "category": "Extensions",
    "description": """This module provides base extensions for Frogblue project""",
    "data": [
        'translations.sql',
        'stock_barcode/security/ir.model.access.csv',
        'stock_barcode/data/parameters.xml',
        'stock_barcode/wizard/stock_barcode_lot.xml',
    ],
    "qweb": [
    ]
}
