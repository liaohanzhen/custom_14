# -*- coding: utf-8 -*-
{
    'name' : 'Project Requirement',
    'version' : '14.0',
    "author": "Nikunj",
    "category" : "Project",
    "description": """
This module will add below features in Project App.
- Project requirement
- Auto set Project stages based on selected template in project form.
- User can select more than one project requirement in its task.

    """,
    'depends' : ['project','sh_project_portfolio','project_kanban_background','crm_5b_erp_ext','mail'],
    "data" : [
              "security/ir.model.access.csv",  
              "views/project_task_type_template_view.xml",
              "views/project_task_view.xml",
              "views/project_view.xml",
              "views/project_requirement_view.xml",
              "views/project_template_view.xml",
              "views/templates.xml",
              "wizard/crm_project_wizard.xml",
              "wizard/select_project_name_view.xml",
            ],
    'qweb': [
        
    ],  
    'installable': True,
    'auto_install': False,
    'application': False,
    'uninstall_hook': '_remove_domain_in_task_action',
    'post_init_hook': '_set_domain_in_task_action',
}
