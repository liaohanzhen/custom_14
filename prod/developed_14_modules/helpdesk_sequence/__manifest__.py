# -*- coding: utf-8 -*-
# Author: Paulius Stundžia. Copyright: JSC Boolit.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Helpdesk Ticket Sequence',
    'version': '14.0',
    'category': 'Helpdesk',
    'summary': 'helpdesk, sequence',
    'description': """
    Implement sequence for helpdesk tickets.
    Added "Assign to me & Open" button to : Assign the user to the ticket + Move the ticket up to the next stage.
    """,
    'author': 'Nilesh Sheliya',
    'website': '',
    'depends': [
        'helpdesk'
    ],
    'data': [
        'views/helpdesk_ticket_views.xml',
        'data/sequence.xml',
    ],
    'license': 'LGPL-3',
}
