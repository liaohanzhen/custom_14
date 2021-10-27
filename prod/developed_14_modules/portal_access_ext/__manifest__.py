# -*- encoding: utf-8 -*-
{
    'name': 'Project Access Group selection',
    'version': '14.0',
    'author': 'Nikunj Antala',
    'support': 'sheliyanilesh@gmail.com',
    'category': 'Hidden',
    'summary': 'User have access to select portal group in Portal access management popup.',
    'description': """
        User can select specific Portal group to assign to customer in Portal access popup.
    """,
    'depends': ['portal','sale_purchase'],
    'website': '',
    'data': [
        "views/res_partner_view.xml",
        "wizard/portal_wizard_views.xml",
    ],
    'application': False,
}
