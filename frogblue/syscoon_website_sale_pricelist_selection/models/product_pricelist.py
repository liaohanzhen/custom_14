from odoo import models, fields

class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'
    
    fiscal_position_id = fields.Many2one('account.fiscal.position','Fiscal Position')