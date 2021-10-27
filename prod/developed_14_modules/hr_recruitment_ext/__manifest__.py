# -*- coding: utf-8 -*-
{
    'name' : 'Job Recruitment WYSIWYG Editor',
    'version' : '14.0',
    "author": "Nikunj",
    "category" : "Human Resources",
    "description": """
This module will add html widget in Description field. 

    """,
    'depends' : ['hr'],
    "data" : [
              "views/hr_job_view.xml",
            ],
    'qweb': [
        
    ],  
    'installable': True,
    'auto_install': False,
    'application': False,
}
