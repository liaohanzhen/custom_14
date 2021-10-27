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
  "name"                 :  "Odoo Marketplace Quote System",
  "summary"              :  """With the module you can accept price quotations of products from customers who wish to buy products in bulk. The customer can send their purchase quote to the seller/admin and buy the products when approved.""",
  "category"             :  "Website",
  "version"              :  "1.0.0",
  "sequence"             :  20,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Marketplace-Quote-System.html",
  "description"          :  """Purchase quotations
Sell in bulk
Bulk sell
Product bulk
Bulk sale products
Bulk sale clothes
Customer quote system
Product in bulk
Sell Product in Wholesale
Invite RFQs from customers
Customer purchase quote
Purchase quote
Odoo Marketplace
Odoo multi vendor Marketplace
Multi seller marketplace
Multi-seller marketplace
multi-vendor Marketplace""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=marketplace_quote_system&lifetime=120&lout=1&custom_url=/",
  "depends"              :  [
                             'odoo_marketplace',
                             'website_quote_system',
                            ],
  "data"                 :  [
                             'security/access_control_security.xml',
                             'security/ir.model.access.csv',
                             'edi/mail_to_seller_on_new_quote.xml',
                             'data/mp_dashboard_data.xml',
                             'views/mp_customer_quote_views.xml',
                             'views/inherit_mp_dashboard.xml',
                             'views/mp_product_views.xml',
                             'views/mp_res_config_view.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  35,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}