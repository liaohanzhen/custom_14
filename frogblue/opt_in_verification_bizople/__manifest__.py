# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Double Opt-In',
    'category': 'Marketing',
    'version': '14.0.0.0',
    'author': 'Bizople Solutions Pvt. Ltd.',
    'website': 'https://www.bizople.com',
    'summary': 'Double Opt In Verification For Email Marketing',
    'description': """Opt In Verification as needed in GDPR""",
    'depends': [
        'base',
        'mass_mailing',
        'website'
    ],
    'data': [
        'data/opt_in.xml',
        'views/thankyou_template.xml',
        'views/mass_mailing_view.xml',
        'security/ir.model.access.csv',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': True,
    'price': 30,
    'license': 'OPL-1',
    'currency': 'EUR',
}
