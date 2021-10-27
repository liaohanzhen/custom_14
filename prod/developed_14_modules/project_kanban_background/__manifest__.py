# -*- coding: utf-8 -*-

{
    'name' : 'Project Type for Project Background Image',
    'version' : '14.0',
    "author": "Nikunj Antala",
    "category" : "Project",
    "description": """
This module will show background image in Project kanban based on Project type set in Project.
-> Added Project code unique constraints.
-> Project search by Project code
-> Added Project open link and Documents link in Project Kanban view.
    """,
    'depends' : ['project','project_code_in_task'],
    "data" : [
              "security/ir.model.access.csv",
              "views/project_view.xml",
              "views/project_type_view.xml",
            ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
