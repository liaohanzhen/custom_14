# -*- coding: utf-8 -*-
{
    'name': 'Helpdesk Mail Auto Stage Change',
    'version': '14.0.1.0',
    'category': 'Helpdesk',
    'author': 'Nilesh Sheliya',
    'description': """
Auto change stage of ticket based on configuration when system receive mail response for that ticket.
    """,
    'website': 'https://sheliyainfotech.com',
    'depends': [
        'helpdesk',
    ],
    'data': [
             'views/res_config_settings_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
