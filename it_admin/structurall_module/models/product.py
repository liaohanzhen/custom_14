# -*- coding: utf-8 -*-
from odoo import fields, models, api,_

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    costo_km = fields.Float(string="Costo por Km")
    precio_renta = fields.Float(string="Precio de renta")
    costo_instalacion = fields.Float(string="Costo de instalación")
