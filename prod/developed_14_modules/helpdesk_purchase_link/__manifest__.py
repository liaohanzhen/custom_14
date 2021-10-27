# -*- coding: utf-8 -*-

{'name': 'Link Ticket with Purchase order',
 'version': '14.0',
 'category': 'helpdesk',
 'depends': ['helpdesk','purchase'],
 'description': '''This module will create purchase order from ticket form.
 If user creates purchase order from ticket and that purchase order is shipment is done, than ticket status updated automatically to done. 
 ''',
 'author': "Nikunj",
 'license': 'AGPL-3',
 'website': '',
 'data': [
        'views/helpdesk_ticket_view.xml',
        'views/helpdesk_stage_view.xml',
        'views/purchase_order_view.xml',
        ],
 'installable': True,
 'application': False,
 }