# -*- coding: utf-8 -*-

from odoo import fields, models

class ProductAttachment(models.Model):
    _inherit = 'product.attachment'
    
    product_id = fields.Many2one('product.product', help="Product")
    