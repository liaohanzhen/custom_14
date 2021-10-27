# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Frogblue base extensions",
    "version": "14.0.0.0.13",
    "depends": [
        'account_accountant',
        'helpdesk',
        'calendar',
        'crm',
        'delivery',
        'mail',
        'account_inter_company_rules',
        'sale_purchase_inter_company_rules',
        'product',
        'stock_account',
        'account_bank_statement_import_camt',
        'purchase_requisition',
        'account_asset',
        'purchase',
        'stock_barcode',
        'rma_ept',
        'syscoon_partner_accounts',
        'website_crm_partner_assign',
    ],
    "author": "Openfellas",
    "website": "http://www.openfellas.com",
    "category": "Extensions",
    "description": """
        This module provides base extensions for Frogblue project
    """,
    "data": [
        'security/ir.model.access.csv',
        'security/security.xml',
        'attachment/views/ir_attachment.xml',
        'base/views/res_partner_view.xml',
        'base/views/res_company_views.xml',
        'calendar/views/calendar.xml',
        'crm/views/crm_lead_view.xml',
        'delivery/views/product_template_view.xml',
        'helpdesk/views/helpdesk_ticket.xml',
        'product/views/product_views.xml',
        'sale/views/sale_order.xml',
        'stock/views/stock.xml',
        'stock/wizard/ic_scheduled_date.xml',
        'stock/wizard/fb_inventory_report.xml',
        "account/views/account_invoice_view.xml",
        "account/views/account_asset_views.xml",
        "purchase/views/purchase_views.xml",
        "account/views/account_asset_views.xml",
        "account/views/account_invoice_view.xml",
        'data/data.xml',
        'mail/data/mail_data.xml',
        'portal/views/sale_portal_template.xml',
    ],
    "qweb": [
    ]
}
