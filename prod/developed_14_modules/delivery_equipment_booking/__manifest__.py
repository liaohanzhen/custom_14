# -*- coding: utf-8 -*-
{
    'name': "Delivery Equipment Booking",

    'summary': """
        """,

    'description': """

Portal Delivery Equipment Booking
================================
    """,
    'version': '12.3',
    'depends': [
        'website_sale','calendar','portal'
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/calender_view_equipment_booking.xml'
    ],
    'demo': [
        'data/demo_data.xml',
        'data/mail_to_customer_on_equipment_booking.xml',
    ],


}
