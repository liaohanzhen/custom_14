# -*- encoding: utf-8 -*-
{
    'name': "Website sign extension",
    'version': '14.0.0.1',
    'summary': 'This module will remove Odoo ad in website sign Thank you popup. Add Sequence for sending sign one by one to each user.',
    'category': 'Other',
    'description': """""",
    'author': 'Nilesh Sheliya',
    "depends" : ['sign', 'hr_contract'],
    'data': [
             'security/security.xml',
             'security/ir.model.access.csv',
             'wizard/assign_contract_wizard_view.xml',
             'views/signature_view.xml',
             'views/template.xml',
             'wizard/send_sign_request_view.xml',
             'wizard/saign_send_seq_dialog.xml',
             ],
    'license': 'LGPL-3',
    'qweb': [
           'static/src/xml/website_sign.xml',
            ],  
    
    'installable': True,
    'application'   : False,
    'auto_install'  : False,
}
