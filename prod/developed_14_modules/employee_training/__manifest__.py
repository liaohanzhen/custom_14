# -*- coding: utf-8 -*-

{
    'name' : 'Employee Training & Certification',
    'version' : '0.1',
    "author": "Nikunj",
    "category" : "Human Resources",
    "description": """
This module will features for Employee training and certification.
    """,
    'depends' : ['hr','maintenance'], #, 'web_digital_sign'
    "data" : [
              "security/ir.model.access.csv",
              "data/email_template.xml",
              "data/ir_cron.xml",
              "views/training_menus.xml",
              "views/training_package_view.xml",
              "views/training_template.xml",
              "views/training_view.xml",
              "views/training_session_view.xml",
              "views/email_template_view.xml",
              "views/hr_employee_view.xml",
              "views/templates.xml",
              "wizard/signature_wizard_view.xml",
              "wizard/wiki_web_page_view.xml",
            ],
    'qweb': [
        'static/src/xml/*.xml',
    ],  
    'installable': True,
    'auto_install': False,
    'application': False,
}
