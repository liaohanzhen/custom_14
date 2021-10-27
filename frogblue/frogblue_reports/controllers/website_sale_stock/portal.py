# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.website_sale_stock.controllers.portal import SaleStockPortal
from odoo.http import request, route
from odoo import exceptions


class SaleStockPortalFrogblue(SaleStockPortal):

    @route(['/my/picking/pdf/<int:picking_id>'], type='http', auth="public",
        website=True)
    def portal_my_picking_report(self, picking_id, access_token=None, **kw):
        res = super(SaleStockPortalFrogblue, self).portal_my_picking_report(picking_id, access_token=access_token, **kw)
        try:
            picking_sudo = self._stock_picking_check_access(picking_id,access_token=access_token)
        except exceptions.AccessError:
            return res

        pdf = request.env.ref('frogblue_reports.report_frogblue_delivery_note').sudo().render_qweb_pdf([picking_sudo.id])[0]
        pdfhttpheaders = [('Content-Type', 'application/pdf'),('Content-Length', len(pdf)),]
        return request.make_response(pdf, headers=pdfhttpheaders)
