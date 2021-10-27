# -*- coding: utf-8 -*-
{
    'name': "Purchase Agreement - Auto generated RFQs",

    'summary': """
        Purchase Agreement - Auto generated RFQs""",

    'description': """
        Purchase Agreement - Auto generated RFQs
    """,

    'author': "Lekha Paudel",
    'website': "http://www.5b.com.au",
    'category': 'Purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase','purchase_requisition'],

    # always loaded
    'data': [
        'views/purchase_auto_rfqs.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}