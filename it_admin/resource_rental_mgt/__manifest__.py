# -*- coding: utf-8 -*-
{
    'name': "Resource Rental Management",
    'version': '1.0',
    'summary': "This module allows you to manage the rental of your products for your customers",
    'author': 'ErpMstar Solutions',
    'category': 'Management System',
    'sequence': 2,

    'website': '',

    'depends': ['product', 'mail','sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/resource_rental.xml',
        'views/rental_product_view.xml',
        'wizards/wizard_view.xml',
        'wizards/rental_order_wizard.xml',
        'views/settings.xml',
        'data/popup_mail_template.xml',
        'data/mail_template_next.xml',
    ],
    'qweb': [
    ],
    'images': [
        'static/description/rent.jpg',
    ],
    'installable': True,
    'application': True,
    'price': 59,
    'currency': 'EUR',
    'live_test_url': "https://www.youtube.com/watch?v=DcTokYviQqA",
}
