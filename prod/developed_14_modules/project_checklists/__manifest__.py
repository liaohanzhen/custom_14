# -*- coding: utf-8 -*-

{
    'name' : 'Project & Task Checklist',
    'version' : '14.0',
    "author": "Nikunj",
    "category" : "Project",
    "description": """
This module will add Project checklist features in Project App.
    """,
    'depends' : ['project','helpdesk'],
    "data" : [
              "security/ir.model.access.csv",  
              "views/project_checklists_view.xml",
              "views/project_task_view.xml",
              "views/project_view.xml",
              "views/web_kanban_templates.xml",
              "views/ir_model_view.xml",
            ],
    'qweb': [
        'static/src/xml/*.xml',
    ],  
    'installable': True,
    'auto_install': False,
    'application': False,
}
