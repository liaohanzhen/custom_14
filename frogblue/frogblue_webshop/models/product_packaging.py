# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    is_sale_qty = fields.Boolean('Is Standard Sale Quantity')

    _sql_constraints = [
        (
            'check_uniqe_is_sale_qty_per_product',
            'Check(1=1)',
            'A product can only have one standard sale quantity!'
        ),
    ]
