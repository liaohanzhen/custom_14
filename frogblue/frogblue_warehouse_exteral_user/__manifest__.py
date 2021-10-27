# -*- coding: utf-8 -*-
{
    'name': 'Frogblue warehouse Exteral User',
    'version': '14.0.0.1',
    'author': 'Nilesh Sheliya',
    'license': 'OPL-1',
    'depends': [
        'base','stock',
    ],
    'description': """Hide Menu for Exteral User Group""",
    'data': [
        'security/frogblue_warehouse_exteral_user_security.xml',
        'views/view_users_form.xml',
        ],
    'installable': True
}
