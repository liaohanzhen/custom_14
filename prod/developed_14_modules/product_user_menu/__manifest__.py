# -*- coding: utf-8 -*-

{
    'name' : 'Menu for Product & Users',
    'version' : '14.0',
    "author": "Nikunj",
    "category" : "Other",
    "description": """
This module will add Users and Product menu in the first screen.
    """,
    'depends' : ['product','base'],
    "data" : [
              "views/product.xml",
              "views/menu.xml",
            ],
    'qweb': [
        
    ],  
    'installable': True,
    'auto_install': False,
    'application': False,
}
