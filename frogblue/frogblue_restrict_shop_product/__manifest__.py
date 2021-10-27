# -*- coding: utf-8 -*-
##############################################################################
#
##############################################################################

{
    'name': 'Frogblue Restrict shop product',
    'version': '14.2',
    'description': ''' there is one field available and that is preview_product if it is true then it will show the product otherwise it can't show the product.
    ''',
    'category': 'Product',
    'author': 'Nilesh Sheliya',
    'website': 'sheliyainfotech.com',
    'depends': [
        'sale','website_sale'
    ],
    'data': [
        
        'views/product_template_view.xml',
        'views/res_users_view.xml',
    ],
    'application': False,
    'installable': True,
    'license': 'OPL-1',    
}
