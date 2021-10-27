# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import OrderedDict
from operator import itemgetter

from odoo import http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem
import base64
from odoo.osv.expression import OR
import binascii


class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values['documents_count'] = request.env['documents.document'].search_count([('partner_id','=',partner.id)])
        return values
    
    @http.route(['/my/my_documents', '/my/my_documents/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_documents(self, page=1,**kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        ir_attachment = request.env['documents.document']
        domain = [('partner_id','=',partner.id)]
        ir_attachments_count = ir_attachment.search_count(domain)
        pager = portal_pager(
            url="/my/my_documents",
            
            total=ir_attachments_count,
            page=page,
            step=self._items_per_page
        )
        ir_attachments = ir_attachment.search(domain,limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'ir_attachments': ir_attachments,
            'page_name': 'my_documents',
            'pager': pager,
            'default_url': '/my/my_documents',
        })
        return request.render("5b_portal_documents.portal_my_documents", values)
