# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
{
    "name" : "Paypal Express Direct Pay",
    "summary" : "Integrate paypal express checkout payment gateway with ODOO for accepting payments from customers.",
    "category" : "Website",
    "version" : "1.0.0",
    "author" : "Webkul Software Pvt. Ltd.",
    "license" : "Other proprietary",
    "website" : "https://store.webkul.com/Odoo.html",
    "description" : """Integrate paypal express checkout payment gateway with ODOO for accepting payments from customers.""",
    "live_test_url" : "http://odoodemo.webkul.com/?module=paypal_express_directpay",
    "depends" : [
        'payment_paypal_express',
        'website_sale',
    ],
    "data" : [
        'views/template.xml',
        'views/paypal_acquirer.xml',
        'data/paypal_config.xml',
    ],
    "images" : ['static/description/Banner.png'],
    "application" : True,
    "installable" : True,
    "price" : 46,
    "currency" : "USD",
    "pre_init_hook" : "pre_init_check",
}
