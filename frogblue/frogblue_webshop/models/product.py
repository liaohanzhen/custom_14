# -*- coding: utf-8 -*-
from odoo import models, api


class ProductProduct(models.Model):
    _inherit = "product.product"

    def package_product(self):
        package_obj = self.env['product.packaging'].sudo()
        if hasattr(package_obj, 'is_sale_qty'):
            packages = self.sudo().packaging_ids.filtered(lambda x: x.is_sale_qty).sorted(lambda x: x.qty)
        else:
            packages = self.sudo().packaging_ids.sorted(lambda x: x.qty)
        return packages and packages[0].qty or 0

    @api.model
    def change_currency(self, *args, **kwargs):

        return '15'
