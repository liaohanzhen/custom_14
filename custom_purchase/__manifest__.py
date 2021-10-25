{
    'name': 'Custom Purchase',
    'version': '1.0',
    'summary': '   Extended Purchase Module ',
    'description': '   Extended Purchase Module ',
    'category': 'Extra Tools',
    'depends': ['purchase_stock', 'purchase', 'stock', 'sale'],
    'data': [
        'views/purchase_view.xml',
        'report/report_invoice_extend.xml',
    ],
    'installable': True,
}