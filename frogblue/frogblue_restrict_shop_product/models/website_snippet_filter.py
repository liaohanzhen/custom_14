# -*- coding: utf-8 -*-

from odoo import models

class WebsiteSnippetFilter(models.Model):
    _inherit = 'website.snippet.filter'
    
    def _prepare_values(self, limit=None, search_domain=None):
        if self.env.user.shop_preview_user:
            if search_domain == None:
                search_domain = []
            search_domain.append(('preview_product', '=', True))
        return super(WebsiteSnippetFilter, self)._prepare_values(limit=limit, search_domain=search_domain)