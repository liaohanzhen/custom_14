# -*- coding: utf-8 -*-
{
    'name': "Send SMS for Ticket & Quality Alert",
    'version': "14.0.1",
    'author': "Nikunj",
    'category': "Tools",
    'support': "nikunj.antala@gmail.com",
    'summary':'System will auto send smses for Quality Alert & Tickets, if its priority is Urgent(3 stars) to its related followers.',
    'description':'System will auto send smses for Quality Alert & Tickets, if its priority is Urgent(3 stars) to its related followers.',    
    'license':'LGPL-3',
    'data': [
        'data/sms_template.xml',
        'views/template.xml',
        'views/quality_alert_team_view.xml',
        'views/helpdesk_view.xml',
       # 'views/base_config_settings_view.xml',
    ],
    'qweb': [
           'static/src/xml/thread.xml',
            ],
    'demo': [],
    'depends': ['sms_frame','helpdesk', 'quality_control','mail', 'sale_stock'],
 
    'installable': True,
}