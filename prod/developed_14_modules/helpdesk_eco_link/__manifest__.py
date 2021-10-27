# -*- coding: utf-8 -*-

{
 'name': 'Link Ticket with ECO order',
 'version': '12.0.1.0.0',
 'category': 'helpdesk',
 'depends': ['helpdesk','mrp_plm'],
 'description': '''This module will create ECO order from ticket form.
  
 ''',
 'author': "Nikunj",
 'license': 'AGPL-3',
 'website': '',
 'data': [
        'views/mrp_eco_view.xml',
        'views/helpdesk_ticket_view.xml',
        
        ],
 'installable': True,
 'application': False,
 }