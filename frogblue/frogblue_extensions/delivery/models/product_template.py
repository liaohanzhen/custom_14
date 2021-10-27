# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class CustomerProductCode(models.Model):
    _name = 'customer.product.code'
    _description = 'Customer Products Code'

    customer_id = fields.Many2one('res.partner', string='Customer')
    product_code = fields.Char('Product code')
    product_id = fields.Many2one('product.template', string='Product')

    _sql_constraints = [
        (
            'customer_id_uniq',
            'unique (product_id,customer_id)',
            'Products can have only one product code per customer!'
        )
    ]


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_version = fields.Char(
        string="Version Number",
        help="Version Number"
    )
    external_reference = fields.Char('Construction No.', index=True)

    customer_product_code_ids = fields.One2many('customer.product.code', 'product_id')

    net_weight = fields.Float(
        'Net Weight',
        digits='Stock Weight',
        help="The Net weight of the product in Kg."
    )


class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    @api.depends('quant_ids')
    def _compute_net_weight(self):
        net_weight = 0.0
        for quant in self.quant_ids:
            net_weight += quant.quantity * quant.product_id.net_weight
        self.net_weight = net_weight

    net_weight = fields.Float(compute='_compute_net_weight')
