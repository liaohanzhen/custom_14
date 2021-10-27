# -*- coding: utf-8 -*-
{
    'name': "Amazon Pay Payment Acquirer",
    'version': '14.0.1.2.0',
    'category': 'Accounting/Payment',
    'author': "Maksym Nastenko",
    'support': "maximnastenko@gmail.com",
    'license': 'OPL-1',
    'price': 75,
    'currency': 'EUR',
    'installable': True,
    'auto_install': False,


    'depends': [
        'payment',
    ],
    'external_dependencies': {
        'python': [
            'amazon_pay',
        ],
    },


    'summary': "Handling one-time payments with Amazon Pay",
    'images': [
        'static/description/AmazonPay_cover_gray.png',
    ],
    'description': """
Amazon Pay payment acquirer module.

https://pay.amazon.eu/

""",


    'data': [
        'security/ir.model.access.csv',


        'views/payment_amazonpay_templates.xml',      # it should be before data file because of reference on a view


        'data/payment_acquirer_data.xml',


        'views/payment_views.xml',
    ],


    'post_init_hook': 'create_missing_journal_for_acquirers',
    'uninstall_hook': 'uninstall_hook',

}

