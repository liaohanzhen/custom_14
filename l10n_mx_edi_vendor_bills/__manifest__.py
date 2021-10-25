# Copyright 2017, Jarsa Sistemas, S.A. de C.V.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Import Supplier Invoice from CFDI',
    'summary': 'Create multiple Invoices from CFDI',
    'version': '14.0.1.0.0',
    'category': 'Accounting/Localizations/EDI',
    'author': 'Vauxoo,Jarsa',
    'website': 'https://www.vauxoo.com',
    'depends': [
        'l10n_mx_edi',
    ],
    'license': 'LGPL-3',
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'views/assets.xml',
        'views/account_move_views.xml',
        'views/product_view.xml',
        'wizards/attach_xmls_wizard_view.xml',
    ],
    'demo': [
        'demo/ir_attachment.xml',
    ],
    'qweb': [
        'static/src/xml/*.xml',
    ],
    'installable': True,
}
