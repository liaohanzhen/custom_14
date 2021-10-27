from odoo import models, fields

class ProductCategory(models.Model):
    _inherit = 'product.category'
    
    syscom_categ_id = fields.Integer('Syscom Category ID')