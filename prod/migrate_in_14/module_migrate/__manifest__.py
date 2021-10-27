# -*- coding: utf-8 -*-

{
    'name' : 'Module Migration',
    'version' : '14.0.0.1',
    "author": "Nikunj",
    "category" : "Extra",
    "description": """
Added field in Module model to know that module need to migrate to 14 or not.
    """,
    'depends' : ['base'],
    "data" : [
              "views/ir_module_view.xml",
            ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
