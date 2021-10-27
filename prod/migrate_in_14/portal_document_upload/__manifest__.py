# -*- coding: utf-8 -*-
{
    'name': "Upload attachments from website portal",
    'version': "14.1",
    'summary': """
        User can upload attachments/Documents from website portal""",
    'description': """
        
    """,

    'author': "Nilesh Sheliya",
    'company': "Sheliya Infotech",
    'website': "",
    'category': "Hidden",
    'depends': [
        "portal",
    ],
    'data': [
        'views/assets.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'demo': [],
    'license': "LGPL-3",
    'installable': True,
    'application': True
}
