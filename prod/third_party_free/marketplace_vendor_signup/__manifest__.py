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
    "name"          :   "Marketplace Multi Step Vendor Signup",
    "summary"       :   """Allow Marketplace vendors to fill signup form in multiple steps""",
    "category"      :   "website",
    "version"       :   "1.0.0",
    "sequence"      :   "1",
    "author"        :   "Webkul Software Pvt. Ltd.",
    "licence"       :   "Other proprietary",
    "website"       :   "https://store.webkul.com/Odoo-Marketplace-Multi-Step-Vendor-Signup.html",
    "description"   :   """Multi Step Vendor Signup
    Marketplace Signup""",
    "live_test_url" :   "http://odoodemo.webkul.com/?module=marketplace_vendor_signup&lifetime=60&lout=1&custom_url=/seller/signup",
    "images"        :   ['static/description/Banner.png'],
    "depends"       :   ['odoo_marketplace'],
    "data"          :   [
                            "security/ir.model.access.csv",
                            "wizards/field_add_domain.xml",
                            "views/marketplace_config.xml",
                            "views/seller_registration.xml",
                            "views/seller_signup_template.xml",
                            "views/template.xml",
                        ],
    "demo"          :   [],
    "application"   :   True,
    "installable"   :   True,
    "auto_installed":   False,
    "price"         :   99,
    "currency"      :   "USD",
    "pre_init_hook" :   "pre_init_check",
}
