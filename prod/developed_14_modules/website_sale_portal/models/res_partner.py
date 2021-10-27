
from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    public_categ_ids = fields.Many2many('product.public.category', string='Allowed eCommerce Categories', help="Customer can see products only for those categories, those are selected here.")
    
    