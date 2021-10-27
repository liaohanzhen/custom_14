# -*- coding: utf-8 -*-
{
    'name': "Avm Inventory Module",
    'version': "14.0.1.0",
    'author': "Admin",
    'category': "",
    'description': 'Add new field date_confirmed in stock.picking model',
    'depends': [
        'stock'
    ],
    'data': [
        'views/stock_picking_views.xml',
        ],
    'installable': True,
}