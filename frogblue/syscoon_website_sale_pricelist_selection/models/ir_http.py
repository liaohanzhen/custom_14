# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models,api
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _get_translation_frontend_modules_name(cls):
        mods = super(IrHttp, cls)._get_translation_frontend_modules_name()
        return mods + ['syscoon_website_sale_pricelist_selection']
    
    
    @api.model
    def get_frontend_session_info(self):
        session_info = super(IrHttp, self).get_frontend_session_info()
        session_info.update({
            'is_public_user': request.env.user._is_public(),
            'is_user_pricelist_set': True if not request.session.is_user_signup and request.env.user.property_product_pricelist else False,
        })
        return session_info
    
        