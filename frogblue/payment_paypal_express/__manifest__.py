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
  "name"                 :  "Website Paypal Express Checkout Payment Acquirer",
  "summary"              :  """Odoo Paypal Express Checkout Payment Acquirer integrates Paypal with your Odoo for accepting quick payments from customers.""",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/odoo-website-paypal-express-checkout-payment-acquirer.html",
  "description"          :  """Paypal Express Checkout Payment Acquirer
Odoo Paypal Express Checkout Payment Acquirer
Paypal Express Checkout Payment Acquirer in Odoo
Paypal Integration
Odoo Paypal Express
Paypal Express
Paypal Express Checkout
Paypal Express Checkout Integration
Configure Paypal
PayPal integration with Odoo
Paypal Express Checkout Payment integration with Odoo""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=payment_paypal_express&custom_url=/shop",
  "depends"              :  ['payment'],
  "data"                 :  [
                             'views/assests.xml',
                             'views/template.xml',
                             'views/paypal_checkout_template.xml',
                             'views/paypal_acquirer_view.xml',
                             'data/paypal_demo_data.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "price"                :  69,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}