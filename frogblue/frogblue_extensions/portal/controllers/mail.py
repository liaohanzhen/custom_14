from odoo import http, _
from odoo.http import request
from odoo.osv import expression
from odoo.tools import consteq, plaintext2html
from odoo.addons.portal.controllers.mail import PortalChatter


class PortalChatterFrogblue(PortalChatter):
    
    @http.route()
    def portal_chatter_post(self, res_model, res_id, message, redirect=None, attachment_ids='', attachment_tokens='', **kw):
        res = super(PortalChatterFrogblue, self).portal_chatter_post(res_model, res_id, message, redirect=redirect, attachment_ids=attachment_ids, attachment_tokens=attachment_tokens, **kw)
        return res