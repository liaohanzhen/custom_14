# -*- coding: utf-8 -*-
{
    'name': "Slack Odoo Connector",

    'summary': """Slack Odoo Integration""",

    'description': """Odoo is a fully integrated suite of business modules that encompass the traditional ERP functionality. Odoo Slack allows you to send updates on your Slack.
    """,
    
    'author': "Nilesh Sheliya",
    'website': "http://sheliyainfotech.com",
 
   
    'category': 'Discuss',
    'version': '14.0.0.1.0',
    'price': 349,
    'currency': 'EUR',
     "license": "OPL-1", 


    # any module necessary for this one to work correctly
    'depends': ['mail'],
    
    'images': [
        'static/description/banner1.png',
    ],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_company.xml',
        'views/mail_channel_view.xml',
        'views/templates.xml',
        'views/slack_view.xml'
    ],
    
}
