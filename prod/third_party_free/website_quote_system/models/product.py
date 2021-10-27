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

from odoo import models,fields,api,_
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    quotation = fields.Boolean(string ='Allow for quote', copy=False)
    min_qty = fields.Float(string ='Minimum Quantity', default =1.0, copy=False)
    valid_days = fields.Integer(string="Valid Upto", default =1, copy=False)

    def _check_quote_qty_date(self, vals):
        quotation = vals.get('quotation') if vals.get('quotation') else self.quotation
        if quotation:
            qty = vals.get('min_qty') if vals.get('min_qty') else self.min_qty
            valid_days = vals.get('valid_days') if vals.get('valid_days') else self.valid_days
            if qty <= 0.0:
                raise UserError(_("Minimum quantity for Customer Quote must be greater than 0."))
            if valid_days <= 0:
                raise UserError(_("Valid Days for Customer Quote must be greater than 0."))

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        res._check_quote_qty_date(vals)
        return res

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        for rec in self:
            rec._check_quote_qty_date(vals)
        return res
