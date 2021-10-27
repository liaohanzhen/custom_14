# -*- coding: utf-8 -*-
{
    "name": "Show All Employee Information",
    "version": "14.0",
    "author": "Nilesh Sheliya",
    "category": "hr",
    "description": """
        This module will add the one group if user are add in this group show all tab of hr.employee other wise show only work information tab
    """,
    "depends": ["hr","hr_contract","hr_gamification","employee_training","employee_checklists"],
    
    "data": [
              "security/security.xml",
              'views/hide_menu.xml',
            ],
    
    "installable": True,
    "auto_install": False,
    "application": True,
}
