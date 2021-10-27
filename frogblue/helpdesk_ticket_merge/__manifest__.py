# -*- coding: utf-8 -*-
{
    'name': 'Helpdesk Ticket Merge',
    'version': '14.0.1.0',
    'author': 'Nilesh Sheliya',
    'category': 'Services/Helpdesk',
    'website': 'https://sheliyainfotech.com',
    'depends': [
        'helpdesk'
    ],
    'description': """User able to merge Helpdesk tickets.""",
    'data': [
             'security/ir.model.access.csv',
             'data/email_template.xml',
             'wizard/helpdesk_ticket_merge_views.xml',
        ],
    'active': False,
    'installable': True
}
