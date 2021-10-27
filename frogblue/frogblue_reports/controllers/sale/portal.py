# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, http, _
from odoo.addons.sale.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError
from odoo.http import request


class CustomerPortalFrogblue(CustomerPortal):

    @http.route(['/my/orders/<int:order_id>'], type='http', auth="public", website=True)
    def portal_order_page(self, order_id, report_type=None, access_token=None, message=False, download=False, **kw):
        res = super(CustomerPortalFrogblue, self).portal_order_page(order_id, access_token=access_token, **kw)
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token=access_token)
        except AccessError:
            return res

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=order_sudo, report_type=report_type, report_ref='frogblue_reports.report_frogblue_sale_order', download=download)

        if order_sudo:
            # store the date as a string in the session to allow serialization
            now = fields.Date.today().isoformat()
            session_obj_date = request.session.get('view_quote_%s' % order_sudo.id)
            if session_obj_date != now and request.env.user.share and access_token:
                request.session['view_quote_%s' % order_sudo.id] = now
                body = _('Quotation viewed by customer %s', order_sudo.partner_id.name)
                _message_post_helper(
                    "sale.order",
                    order_sudo.id,
                    body,
                    token=order_sudo.access_token,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                    partner_ids=order_sudo.user_id.sudo().partner_id.ids,
                )

        values = self._order_get_page_view_values(order_sudo, access_token, **kw)
        values['message'] = message

        return request.render('sale.sale_order_portal_template', values)
