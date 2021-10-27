from odoo import fields, models, api, _


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'


    estados = fields.Many2many('res.country.state', string="Estados")
    
class PricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    rental_price = fields.Float(string="Precio de renta")