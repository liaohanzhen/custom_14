# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, _
from odoo.addons.website_sale.controllers.variant import WebsiteSaleVariantController
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request

class WebsiteSaleStockVariantController(WebsiteSaleVariantController):
    
    
    @http.route()
    def get_combination_info_website(self, product_template_id, product_id, combination, add_qty, **kw):
        
        res = super(WebsiteSaleStockVariantController, self).get_combination_info_website(product_template_id, product_id, combination, add_qty, **kw)
        product = request.env['product.product'].sudo().browse(res['product_id'])
        if product and product.packaging_ids:
            package_obj = request.env['product.packaging'].sudo()
            if hasattr(package_obj, 'is_sale_qty'):
                packages = product.packaging_ids.filtered(lambda x: x.is_sale_qty).sorted(lambda x:x.qty)
            else:
                packages = product.packaging_ids.sorted(lambda x:x.qty)
            if packages:
                res['variant_package_qty'] = packages[0].qty
            package_data = []
            for package in product.packaging_ids:
                if package.qty > 0:
                    package_data.append(str(int((add_qty or 1)/package.qty))+' '+package.name)
            res['package_data'] = package_data
        return res

    @http.route('/change/currency-format', type='json', auth="user", website=True)
    def chnage_currency(self, price, digits=None, dp=False, *args, **kwargs):
        currency_obj = request.env.user.currency_id or None
        if digits is None:
            digits = DEFAULT_DIGITS = 2
            if dp:
                decimal_precision_obj = request.env['decimal.precision']
                digits = decimal_precision_obj.precision_get(dp)
            elif currency_obj:
                digits = currency_obj.decimal_places
        new_price = request.lang.format(f'%.{digits}f', float(price), True, True)
        return new_price