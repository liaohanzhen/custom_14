# -*- coding: utf-8 -*-

{
    'name' : 'Maintenance Equipment iframe',
    'version' : '14.0',
    "author": "Nikunj",
    "category" : "Manufacturing",
    "description": """
This module will add iframe in Maintenance Equipment.
    """,
    'depends' : ['maintenance','hr'],
    "data" : [
              "data/sequence.xml",
              "views/maintenance_equipment_view.xml",
              'views/hr_employee_view.xml',
              "views/templates.xml",
            ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
