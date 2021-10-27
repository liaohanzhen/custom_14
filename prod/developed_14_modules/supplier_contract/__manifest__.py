# -*- coding: utf-8 -*-

{
    'name' : 'Supplier Contract',
    'version' : '14.0',
    "author": "Nikunj",
    "category" : "Purchase",
    "description": """
This module with add contract feature in Supplier form.
    """,
    'depends' : ['purchase'],
    "data" : [
              "security/ir.model.access.csv",  
              "views/res_partner_view.xml",
              "views/product_supplierinfo_view.xml",
              "views/template.xml",
            ],
      
    'installable': True,
    'auto_install': False,
    'application': False,
}
