# -*- encoding: utf-8 -*-
{
    'name': "Website Sale Shop only for portal users.",
    'version': '14.0',
    'summary': 'This module will show shop products to portal users only. .',
    'category': 'Other',
    'description': """Products are not visible for public on the website shop.
- Hide shop menu for not logged in user.
- User can only see products of ecommerce categories those are allowed to him. 

    """,
    'author': 'Nilesh Sheliya',
    "depends" : ['website_sale'],
    'data': [
             'views/res_partner_view.xml',
             'views/templates.xml',
             ],
    'license': 'LGPL-3',
    'qweb': [
           
            ],  
    
    'installable': True,
    'application'   : False,
    'auto_install'  : False,
}
