# -*- coding: utf-8 -*-

{
    'name' : 'Quality Control check based on serial number.',
    'version' : '14.0',
    "author": "Nikunj",
    "category" : "Manufacturing",
    "description": """
If product with tracking = Serial number, than system will create Quality checks more than one for the same product based on Quantity of
that product in picking. By default system create only 1 Quality check.\n
For example, Product Orange with Tacking = Serial Number. Its Quality Check point is created.
Now User create Picking of Orange product with Quantity = 10 and confirm it,
than system will create 10 Quality checks for Orange product instead of only 1 Quality check.
    """,
    'depends' : ['quality_control'],
    "data" : [
            'views/quality_view.xml',
            'views/quality_point_view.xml',
            ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
