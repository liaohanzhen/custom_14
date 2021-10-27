# -*- coding: utf-8 -*-

{
    'name' : 'Supplier Approval/Not Approval',
    'version' : '14.0',
    "author": "Nikunj",
    "category" : "Purchase",
    "description": """
This module with add Approval/Not Approval feature in Supplier form.
    """,
    'depends' : ['purchase'],
    "data" : [
              "security/ir.model.access.csv",  
              "views/res_partner_view.xml",
              "views/product_supplierinfo_view.xml",
              "views/purchase_order_view.xml",
              'wizard/approval_wizard_view.xml',
              "views/template.xml",
              
            ],
    'qweb': [
        'static/src/xml/*.xml',
    ],  
    'installable': True,
    'auto_install': False,
    'application': False,
}
