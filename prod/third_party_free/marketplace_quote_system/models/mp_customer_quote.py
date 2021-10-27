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

from odoo import models,fields, api, _

class CustomerQuote(models.Model):
    _inherit = "quote.quote"

    marketplace_seller_id = fields.Many2one("res.partner", string="Seller", related = 'product_id.marketplace_seller_id', store=True)
    activity_date_deadline = fields.Date(
        'Next Activity Deadline', related='activity_ids.date_deadline',
        readonly=True, store=True,  # store to enable ordering + search
        groups="odoo_marketplace.marketplace_seller_group")

    def send_quote_creation_mail(self):
        res = super(CustomerQuote, self).send_quote_creation_mail()
        template = self.env['mail.template']
        config_setting_obj = self.env['res.config.settings'].get_values()
        if config_setting_obj["enable_notify_seller_on_new_quote"] and config_setting_obj.get("notify_seller_on_new_quote") and config_setting_obj["notify_seller_on_new_quote"]:
            temp_id = config_setting_obj[
                "notify_seller_on_new_quote"]
            if temp_id:
                template.browse(temp_id).sudo().send_mail(self.id, force_send=True)
        return res

    @api.model
    def create(self, vals):
        res= super(CustomerQuote, self).create(vals)
        if vals.get("product_id"):
            product = self.env['product.product'].browse(vals.get("product_id"))
            if product and product.marketplace_seller_id:
                res.message_subscribe([product.marketplace_seller_id.id])
        return res

class ProductTemplate(models.Model):
    _inherit = "product.template"
