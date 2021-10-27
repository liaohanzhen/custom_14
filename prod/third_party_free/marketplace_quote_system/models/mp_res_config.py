# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
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

from odoo import models, fields, api, _
from odoo.tools.translate import _

class MarketplaceConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enable_notify_seller_on_new_quote = fields.Boolean(string="Enable")
    notify_seller_on_new_quote = fields.Many2one(
        "mail.template", string="Notification for Seller", domain="[('model_id.model','=','quote.quote')]")

    def set_values(self):
        res = super(MarketplaceConfigSettings, self).set_values()
        self.env['ir.default'].sudo().set(
            'res.config.settings', 'enable_notify_seller_on_new_quote', self.enable_notify_seller_on_new_quote)
        self.env['ir.default'].sudo().set(
                    'res.config.settings', 'notify_seller_on_new_quote', self.notify_seller_on_new_quote.id)
        return True

    @api.model
    def get_values(self, fields=None):
        res = super(MarketplaceConfigSettings, self).get_values()
        seller_quote_temp = self.env['ir.model.data'].get_object_reference(
            'marketplace_quote_system', 'quote_create_email_template_to_seller')[1]
        enable_notify_seller_on_new_quote = self.env['ir.default'].get(
            'res.config.settings', 'enable_notify_seller_on_new_quote')
        notify_seller_on_new_quote = self.env['ir.default'].get(
                    'res.config.settings', 'notify_seller_on_new_quote') or seller_quote_temp
        res.update({
                'enable_notify_seller_on_new_quote': enable_notify_seller_on_new_quote,
                'notify_seller_on_new_quote': notify_seller_on_new_quote,
        })
        return res
