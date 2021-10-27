# -*- coding: utf-8 -*-
{
    'name': "5b NCR/Nonconformity",

    'summary': """
        5B Management System - > NCR/Nonconformity""",

    'description': """
        5B Management System - > NCR/Nonconformity extension
    """,

    'author': "5B",
    'website': "http://www.5b.co",

    'category': 'Management System',
    'version': '0.1',

    'depends': ['base','mgmtsystem_audit'],

    'data': [
        # 'security/ir.model.access.csv',
        'views/ncr_views.xml',
        #'views/templates.xml',
    ],
    'demo': [
        #'demo/demo.xml',
    ],
    "installable": True,
    "application": True,
}
