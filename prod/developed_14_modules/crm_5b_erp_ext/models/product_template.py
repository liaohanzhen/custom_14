# -*- coding: utf-8 -*-

from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    is_mav = fields.Boolean('Is MAV', default=False,)