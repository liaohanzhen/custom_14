# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.http import request, route
from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.web.controllers.main import ensure_db, Home

from odoo.addons.auth_signup.controllers.main import AuthSignupHome


class SyscoonAuthSignupHome(AuthSignupHome):
    @http.route()
    def web_auth_signup(self, *args, **kw):
        response = super(SyscoonAuthSignupHome, self).web_auth_signup(*args, **kw)
        if not response.qcontext.get('error', False):
            request.session.is_user_signup=True
            if not response.qcontext.get('token') and response.qcontext.get('signup_enabled'):
                User = request.env['res.users']
                user_sudo = User.sudo().search(
                    User._get_login_domain(kw.get('login')), order=User._get_login_order(), limit=1
                )
                template = request.env.ref('auth_signup.mail_template_user_signup_account_created', raise_if_not_found=False)
                if user_sudo and template:
                    template.sudo().send_mail(user_sudo.id, force_send=True)
        return response
    
    
    
class SyscoonHome(Home):

    @route()
    def web_login(self, *args, **kw):
        ensure_db()
        response = super(SyscoonHome, self).web_login(*args, **kw)
        if request.session.uid and not request.env.user._is_public():
            if request.session.get('website_sale_current_pl'):
                request.session.pop('website_sale_current_pl')
            pricelist = request.env.user.property_product_pricelist
            if pricelist:
                request.session['website_sale_current_pl'] = pricelist.id
        return response
    
    
        
class WebsiteSale(WebsiteSale):

    @route(['/shop/get/pricelist'], type='json', auth="public",
           website=True, csrf=False)
    def get_pricelist(self):
        pricelists = request.website.get_pricelist_available()
        if not request.env.user._is_public():
            return pricelists.filtered(lambda p: p.selectable or p.id==request.env.user.partner_id.property_product_pricelist.id).read(['name'])
            
        return pricelists.filtered(lambda p: p.selectable).read(['name'])

    @route(['/shop/change_pricelist/<model("product.pricelist"):pl_id>'], type='http', auth="public", website=True, sitemap=False)
    def pricelist_change(self, pl_id, **post):
        if (pl_id.selectable or pl_id == request.env.user.partner_id.property_product_pricelist) \
                and request.website.is_pricelist_available(pl_id.id):
            request.session['website_sale_current_pl'] = pl_id.id
            request.session['hide_pricelist_dropdown'] = post.get('hide_pricelist_dropdown',False)
            sale_order = request.website.sale_get_order(force_pricelist=pl_id.id)
            if pl_id.fiscal_position_id:
                sale_order.sudo().write({'fiscal_position_id': pl_id.fiscal_position_id.id,})
                sale_order._compute_tax_id()
            else:
                sale_order.sudo().write({'fiscal_position_id': sale_order.partner_id.property_account_position_id.id,})
                sale_order._compute_tax_id()
        return request.redirect(request.httprequest.referrer or '/')
