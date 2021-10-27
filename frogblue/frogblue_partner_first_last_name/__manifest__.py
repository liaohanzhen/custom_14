# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Frogblue Partner First Last Name",
    "version": "14.0",
    "depends": ['base', 'crm','auth_signup'],
    "author": "Openfellas",
    "website": "http://www.openfellas.com",
    "category": "Contacts",
    "description": """
        This module splits the name for non company partners from first and last name
    """,
    "data": [
        'views/res_partner_views.xml',
        'views/res_users_views.xml',
        'views/crm_views.xml',
    ],
    "qweb": [
    ]
}
