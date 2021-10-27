
from odoo import models, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
        combination_info = super(ProductTemplate, self)._get_combination_info(
            combination=combination, product_id=product_id, add_qty=add_qty, pricelist=pricelist,
            parent_combination=parent_combination, only_template=only_template)
        if self.env.context.get('website_id'):
            product = self.env['product.product'].browse(combination_info['product_id']) or self
            combination_info.update(
                default_code = product.default_code,
            )
        else:
            combination_info.update(default_code = False,)
        return combination_info