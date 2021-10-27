# -*- coding: utf-8 -*-

{
    'name' : 'Quality Control Points iframe',
    'version' : '14.0',
    "author": "Nikunj",
    "category" : "Manufacturing",
    "description": """
This module will add iframe in Quality control point.
    """,
    'depends' : ['quality_control'],
    "data" : [
              "views/quality_point_view.xml",
              "views/quality_check_view.xml",
              "views/quality_alert_view.xml",
              "views/templates.xml",
            ],
#     'qweb': [
#         'static/src/xml/*.xml',
#     ],  
    'installable': True,
    'auto_install': False,
    'application': False,
}
