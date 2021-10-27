# -*- coding: utf-8 -*-

{
    'name' : 'Hr Employee Checklist',
    'version' : '0.1',
    "author": "Nikunj",
    "category" : "HR",
    "description": """
This module will add Employee checklist features in Employee App.
    """,
    'depends' : ['hr','helpdesk', 'employee_training'], #'web_readonly_bypass'
    "data" : [
              "security/ir.model.access.csv",  
              "views/menu.xml",
              "views/employee_checklists_view.xml",
              "views/hr_employee_view.xml",
              "views/web_kanban_templates.xml",
              "views/checklist_package_view.xml",
            ],
    'qweb': [
        'static/src/xml/*.xml',
    ],  
    'installable': True,
    'auto_install': False,
    'application': False,
}
