# -*- coding: utf-8 -*-
{
    'name': 'Frogblue webshop',
    'version': '14.05',
    'description': '''If product have package with quantity, than system will auto increment/decrement quantity based on package quantity when user click on + or - button in webshop product page.
    ''',
    'author': 'Nilesh Sheliya',
    'website': '',
    'depends': [
        'website_sale','product',
    ],
    'data': [
            'views/product_packaging.xml',
            'views/template.xml',
            'views/package_qty.xml',
    ],
    'qweb': [],
    'application': False,
    'installable': True,   
}

