# -*- coding: utf-8 -*-
{
    'name': "Show Documents of different models in Portal",
    'version': "1.1",
    'summary': """
        Base module for showing different models documents in user portal view""",
    'description': """
        
    """,

    'author': "Nilesh Sheliya",
    'company': "Sheliya Infotech",
    'website': "",
    'category': "Hidden",
    'depends': [
        "portal",'documents'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/portal_user_attachment.xml',
        'wizard/attachment_wizard_view.xml',
    ],
    'demo': [],
    'license': "LGPL-3",
    'installable': True,
    'application': True
}
