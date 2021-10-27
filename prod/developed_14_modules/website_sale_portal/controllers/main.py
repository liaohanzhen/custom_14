# -*- coding: utf-8 -*-

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import http
from odoo.http import request
from odoo.osv import expression

class WebsiteSalePortal(WebsiteSale):
      #in 14 not partner.public_categ_ids in code here
#     def _get_search_domain(self, search, category, attrib_values,search_in_description=True):
#         domain = super(WebsiteSalePortal, self)._get_search_domain(search, category, attrib_values,search_in_description=True)
#         partner = request.env.user.partner_id
#         #domain.append(('public_categ_ids','in',partner.public_categ_ids.ids))
#         if not category:
#             if partner.public_categ_ids.ids:
#                 domain.append(('public_categ_ids','child_of',partner.public_categ_ids.ids))
#             else:
#                 domain.append(('public_categ_ids','in',partner.public_categ_ids.ids))
#         return domain
    
    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>''',
        '''/shop/category/<model("product.public.category", "[('website_id', 'in', (False, current_website_id))]"):category>/page/<int:page>'''
    ], type='http', auth="user", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        result = super(WebsiteSalePortal, self).shop(page=page, category=category, search=search, ppg=ppg, **post)
        partner = request.env.user.partner_id
        categories = partner.public_categ_ids
        if categories:
            allowed_categories = request.env['product.public.category'].search([('id', 'child_of', categories.ids)])
            user_categories = request.env['product.public.category'].search([('id', 'parent_of', categories.ids)] + request.website.website_domain())
            allowed_categories += user_categories 
            categs = user_categories.filtered(lambda c: not c.parent_id)
            categ_ids = categs.ids
            result.qcontext.update({'categories': result.qcontext.get('categories').filtered(lambda x:x.id in categ_ids),'allowed_categories_ids': allowed_categories.ids})
        else:
            result.qcontext.update({'categories': categories,'allowed_categories_ids':[]})
        #result.qcontext.update({'categories': partner.public_categ_ids,})
         
        return result
    
    @http.route(['/shop/<model("product.template"):product>'], type='http', auth="public", website=True, sitemap=True)
    def product(self, product, category='', search='', **kwargs):
        return super(WebsiteSalePortal, self).product(product, category=category, search=search, **kwargs)
    @http.route(['/shop/change_pricelist/<model("product.pricelist"):pl_id>'], type='http', auth="user", website=True, sitemap=False)
    def pricelist_change(self, pl_id, **post):
        return super(WebsiteSalePortal, self).pricelist_change(pl_id, **post)
    
    @http.route(['/shop/pricelist'], type='http', auth="user", website=True, sitemap=False)
    def pricelist(self, promo, **post):
        return super(WebsiteSalePortal, self).pricelist( promo, **post)
    
    @http.route(['/shop/cart'], type='http', auth="user", website=True)
    def cart(self, access_token=None, revive='', **post):
        return super(WebsiteSalePortal, self).cart(access_token=access_token, revive=revive, **post)
    
    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        return super(WebsiteSalePortal, self).cart_update(product_id, add_qty=add_qty, set_qty=set_qty, **kw)
    
    @http.route(['/shop/cart/update_json'], type='json', auth="user", methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True):
        return super(WebsiteSalePortal, self).cart_update_json(product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty, display=display)
    
    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="user", website=True)
    def address(self, **kw):
        return super(WebsiteSalePortal, self).address(**kw)
    
    @http.route(['/shop/checkout'], type='http', auth="user", website=True)
    def checkout(self, **post):
        return super(WebsiteSalePortal, self).checkout(**post)
    
    @http.route(['/shop/confirm_order'], type='http', auth="user", website=True)
    def confirm_order(self, **post):
        return super(WebsiteSalePortal, self).confirm_order(**post)
    
    