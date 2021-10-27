# -*- coding: utf-8 -*-
{
    'name': 'Sync product information from Syscom',
    'version': '14.2',
    'description': ''' System will update product information when clicking on Buscar button in Product form, it will search product in syscom
    based on SKU or description entered in the 'Product a buscar' field.
    ''',
    'category': 'Product',
    'author': 'Nikunj Antala',
    'website': '',
    'depends': [
        'sale','account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_view.xml',
        'views/syscom_brand_view.xml',
        'views/syscom_categories_view.xml',
        'views/res_company_view.xml',
    ],
    'application': False,
    'installable': True,
    'license': 'OPL-1',    
}
