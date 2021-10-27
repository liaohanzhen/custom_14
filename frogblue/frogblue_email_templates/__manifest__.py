# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Frogblue Email Templates",
    "version": "14.0",
    "depends": ['sale_management', 'account', 'delivery', 'purchase'],
    "author": "Openfellas",
    "website": "http://www.openfellas.com",
    "category": "Extensions",
    "description": """This module provides email templates for Frogblue project""",
    "data": [
        "translations.sql",
        "email_templates/template_edi_sale.xml",
        "email_templates/template_edi_invoice.xml",
        # "email_templates/template_delivery_confirmation.xml", # Deprecated in V14
        "email_templates/template_edi_purchase.xml",
        "email_templates/template_order_proforma.xml",
        "base/views/res_company_view.xml"
    ],
    "qweb": [
    ]
}
