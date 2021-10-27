from odoo import fields,models


class ProductTemplate(models.Model):
    _inherit='product.template'
    
    
    preview_product=fields.Boolean("Preview Product")