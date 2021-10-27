# -*- coding: utf-8 -*-
{
    'name': 'Stock Force Date',
    'version': '14.0.1.0',
    'summary': 'Force Date in Stock Picking',
    'description': """
    This module will give you a way to record stock picking to a specific date. 
    this will effect on related stock quants, moves and stock journal entries.
    """,
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'website': "https://cybrosys.com/",
    'category': 'Warehouse',
    'depends': ['stock', 'stock_account'],
    'data': [
        'security/security.xml',
        'views/stock_view.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.jpg'],
    'license': 'LGPL-3',
    'installable': True,
    'application': False
}
