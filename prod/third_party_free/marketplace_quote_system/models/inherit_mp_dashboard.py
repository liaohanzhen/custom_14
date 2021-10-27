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

from odoo import models, fields, api

class marketplace_dashboard(models.Model):
    _inherit = "marketplace.dashboard"

    def _get_approved_count(self):
        super(marketplace_dashboard, self)._get_approved_count()
        for rec in self:
            if rec.state == 'quotes':
                if rec.is_user_seller():
                    user_id = self.env['res.users'].search([('id', '=', rec._uid)])
                    seller_id = user_id.partner_id.id
                    obj = self.env['quote.quote'].search([('marketplace_seller_id', '=', seller_id), ('status', '=', 'approved')])
                else:
                    obj = self.env['quote.quote'].search([('marketplace_seller_id', '!=', False), ('status', '=', 'approved')])
                rec.count_product_approved = len(obj)

    def _get_pending_count(self):
        super(marketplace_dashboard, self)._get_pending_count()
        for rec in self:
            if rec.state == 'quotes':
                if rec.is_user_seller():
                    user_id = self.env['res.users'].search([('id', '=', rec._uid)])
                    seller_id = user_id.partner_id.id
                    obj = self.env['quote.quote'].search([('marketplace_seller_id', '=', seller_id), ('status', '=', 'pending')])
                else:
                    obj = self.env['quote.quote'].search([('marketplace_seller_id', '!=', False), ('status', '=', 'pending')])
                rec.count_product_pending = len(obj)

    def _get_incart_count(self):
        for rec in self:
            if rec.state == 'quotes':
                if rec.is_user_seller():
                    user_id = self.env['res.users'].search([('id', '=', rec._uid)])
                    seller_id = user_id.partner_id.id
                    obj = self.env['quote.quote'].search([('marketplace_seller_id', '=', seller_id), ('status', '=', 'incart')])
                else:
                    obj = self.env['quote.quote'].search([('marketplace_seller_id', '!=', False), ('status', '=', 'incart')])
                rec.count_product_incart = len(obj)
            else:
                rec.count_product_incart = 0

    def _get_rejected_count(self):
        for rec in self:
            if rec.state == 'quotes':
                rec.count_product_rejected = 0
            else:
                return super(marketplace_dashboard, self)._get_rejected_count()

    state = fields.Selection(selection_add=[('quotes', 'Quotes')])
    count_product_incart = fields.Integer(compute='_get_incart_count')
