{
    'name': "Custom Sale",
    'summary': "Add a field in sales..",
    'description': """Custom Sale.""",
    'category': 'Extra Tools',
    'version': '1.0',
    'depends': ['sale', 'stock', 'project', 'account', ],
    'data': [
        'views/sale_order_line_inherit.xml',
        'views/sale_order_view.xml',
        'views/stock_picking_sscc_view.xml',
        # 'report/report_invoice.xml',
    ],
    'demo': [],
    'installable': True,
}
