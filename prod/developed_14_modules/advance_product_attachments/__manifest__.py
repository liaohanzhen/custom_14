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
    'name'          : "Advance Website Product Attachments",
    'version'       : '14.0',
    'summary'       : """Advance Website Product Attachments""",
    'author'        : 'Webkul Software Pvt. Ltd.',
    'website'       : 'https://store.webkul.com/Odoo-Advance-Website-Product-Attachments.html',
    "license"       :  "Other proprietary",
    'category'      : 'website',
    "live_test_url" : "http://odoodemo.webkul.com/?module=advance_product_attachments&custom_url=/shop/product/e-com10-apple-wireless-keyboard-18",
    'description'   : "https://webkul.com/blog/odoo-advance-website-product-attachments",
    'depends'       : [
        'website_sale',
    ],

    'data'          : [
                        'security/ir.model.access.csv',
                        'views/res_config_view.xml',
                        'wizard/attachment_wizard_view.xml',
                        'views/product_template_views.xml',
                        'views/templates.xml',
    ],
    'demo': [
        'data/data_attachment.xml',
    ],
    "images"        :  ['static/description/Banner.png'],
    "application"   :  True,
    "installable"   :  True,
    "auto_install"  :  False,
    "price"         :  49,
    "currency"      :  "EUR",
    'sequence'      :   1,
#     'pre_init_hook' :   'pre_init_check',
}