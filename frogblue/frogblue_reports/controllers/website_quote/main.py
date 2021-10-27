# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, fields, _
# from odoo.addons.website_quote.controllers.main import sale_quote
from odoo.http import request


# class WebsiteSaleQuoteFrogblue(sale_quote):
class WebsiteSaleQuoteFrogblue():

    @http.route("/quote/<int:order_id>/<token>", type='http', auth="public",
        website=True)
    def view(self, order_id, pdf=None, token=None, message=False, **post):
        res = super(WebsiteSaleQuoteFrogblue, self).view(
            order_id, pdf=pdf, token=token, message=message, **post
        )
        if token:
            order = request.env['sale.order'].sudo().search(
                [('id', '=', order_id), ('access_token', '=', token)]
            )
        else:
            order = request.env['sale.order'].search(
                [('id', '=', order_id)]
            )
        if not order:
            return res
        order_sudo = order.sudo()

        if pdf:
            pdf = request.env.ref(
                'frogblue_reports.report_frogblue_sale_order'
            ).sudo().with_context(
                set_viewport_size=True
            ).render_qweb_pdf([order_sudo.id])[0]
            pdfhttpheaders = [
                ('Content-Type', 'application/pdf'),
                ('Content-Length', len(pdf))
            ]
            return request.make_response(pdf, headers=pdfhttpheaders)
        return res
