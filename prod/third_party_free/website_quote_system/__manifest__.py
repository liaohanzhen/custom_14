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
  "name"                 :  "Website Quote System",
  "summary"              :  """The module allows you to accept price quotations of products from customers who wish to buy products in bulk. The customer can send their purchase quote to the Odoo user and buy the products when approved.""",
  "category"             :  "Sales",
  "version"              :  "1.0.0",
  "sequence"             :  1,
  "author"               :  "Webkul Software Pvt. Ltd.",
  "license"              :  "Other proprietary",
  "website"              :  "https://store.webkul.com/Odoo-Website-Quote-System.html",
  "description"          :  """Website Quote System
bulk quotations in odoo
Purchase quotations
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
Purchase quote""",
  "live_test_url"        :  "http://odoodemo.webkul.com/?module=website_quote_system",
  "depends"              :  [
                             'sale_management',
                             'delivery',
                             'website_webkul_addons',
                             'website_sale_stock',
                            ],
  "data"                 :  [
                             'security/ir.model.access.csv',
                             'security/access_control_security.xml',
                             'edi/mail_to_salesman_on_new_quote.xml',
                             'edi/mail_to_admin_on_new_quote.xml',
                             'edi/mail_to_customer_on_quote_state_change.xml',
                             'edi/mail_to_customer_on_new_quote.xml',
                             'data/quotation_seq.xml',
                             'data/customer_quote_config_data.xml',
                             'views/quote_request_menu_template.xml',
                             'views/customer_quote_template.xml',
                             'views/customer_quote_product_view.xml',
                             'views/templates.xml',
                             'views/customer_quote_config_settings_views.xml',
                             'views/quote_views.xml',
                             'views/quote_dashboard_view.xml',
                             'views/webkul_addons_config_views.xml',
                             'data/wk_quote_dashboard_data.xml',
                            ],
  "demo"                 :  [
                             'demo/product_demo_data.xml',
                             'demo/customer_quote_demo_data.xml',
                             'demo/sale_order_demo_data.xml',
                            ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  99,
  "currency"             :  "USD",
  "pre_init_hook"        :  "pre_init_check",
}