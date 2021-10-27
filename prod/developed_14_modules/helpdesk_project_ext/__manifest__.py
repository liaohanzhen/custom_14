# -*- coding: utf-8 -*-

{'name': 'Link Ticket with Project task & Management Action',
 'version': '14.0',
 'category': 'helpdesk',
 'depends': ['helpdesk','project','mgmtsystem_action'],
 'description': '''This module will create reference of task with helpdesk ticket''',
 'author': "Nikunj",
 'license': 'AGPL-3',
 'website': '',
 'data': [
        'views/helpdesk_view.xml',
        'views/project_task_view.xml',
        'views/mgmtsystem_action_view.xml',
        ],
 'installable': True,
 'application': True,
 }