from odoo import fields, http 
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale

class frogblus(WebsiteSale):
    
    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        values= super(frogblus,self)._get_search_domain(search, category, attrib_values, search_in_description=True) 
        if request.env.user.shop_preview_user:
            values.append(('preview_product', '=', True))
        return values   