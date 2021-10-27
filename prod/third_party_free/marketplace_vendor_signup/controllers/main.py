# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################

import werkzeug
import odoo
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.exceptions import UserError
from odoo import _
from odoo import http
from odoo.http import request
from odoo.addons.odoo_marketplace.controllers.main import AuthSignupHome
from odoo.addons.odoo_marketplace.controllers.main import MarketplaceSellerProfile

import logging
_logger = logging.getLogger(__name__)

class MarketplaceSellerProfile(MarketplaceSellerProfile):
    @http.route(['/profile/seller/email/vaidation'], type='json', auth="public", methods=['POST'], website=True)
    def seller_email_validation(self, email, **post):
        check_email = request.env["res.users"].sudo().search([('login', '=', email)])
        if len(check_email) == 0:
            return True
        else:
            return False

class AuthSignupHome(AuthSignupHome):
    def _signup_with_values(self, token, values):
        signup_obj = request.website.get_active_register_groups()
        params = dict(request.params)
        attribute_list = signup_obj.attribute_ids.mapped(lambda self: self.attribute.name)
        if params:
            if params.get('wk_website') :
                params.update({
                    'website' : params.get('wk_website'),
                })
                del params['wk_website']
            values.update(dict((k, params[k]) for k in attribute_list if k in params))
        return super(AuthSignupHome, self)._signup_with_values(token, values)

    @http.route(['/marketplace_vendor_signup/country_info/<model("res.country"):country>'], type='json', auth="public", methods=['POST'], website=True)
    def marketplace_vendor_signup_country_infos(self, country, **kw):
        states = country.sudo().state_ids

        return dict(
            states=[(st.id, st.name) for st in states],
        )

    @http.route('/seller/signup', type='http', auth="public", website=True)
    def seller_signup_form(self, *args, **kw):
        signup_setting = request.website.mp_multi_step_signup
        qcontext = self.get_auth_signup_qcontext()
            
        if signup_setting:
            if not qcontext.get('token') and not qcontext.get('signup_enabled'):
                raise werkzeug.exceptions.NotFound()
            
            if kw.get("name", False) and 'error' not in qcontext and request.httprequest.method == 'POST':
                try:
                    self.do_signup(qcontext)
                    self.web_login(*args, **kw)
                    return AuthSignupHome().signup_form_successful()
                except UserError as e:
                    qcontext['error'] = e.name or e.value
                except (SignupError, AssertionError) as e:
                    _logger.error("%s", e)
                    qcontext['error'] = _("Could not create a new account.")
            if kw.get("signup_from_seller_page", False) == "true":
                qcontext.pop("error")
                qcontext.update({"set_seller": True, 'hide_top_menu': True})
            return request.render('odoo_marketplace.mp_seller_signup', qcontext)
        return super(AuthSignupHome,self).seller_signup_form(*args, **kw)

    @http.route('/signup/successful', type="http", website=True, auth="public")
    def signup_form_successful(self, **kwargs):
            return request.render('marketplace_vendor_signup.mp_signup_successful')