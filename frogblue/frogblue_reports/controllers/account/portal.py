# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.addons.account.controllers.portal import PortalAccount
from odoo.exceptions import AccessError
from odoo.http import request


class PortalAccountFrogblue(PortalAccount):

    @http.route(['/my/invoices/<int:invoice_id>'], type='http', auth="public", website=True)
    def portal_my_invoice_detail(self, invoice_id, access_token=None, report_type=None, download=False, **kw):
        res = super(PortalAccountFrogblue, self).portal_my_invoice_detail(
            invoice_id, access_token=access_token, **kw
        )
        try:
            invoice_sudo = self._document_check_access('account.move' ,invoice_id, access_token)
        except AccessError:
            return res

        if report_type in ('html', 'pdf', 'text'):
            return self._show_report(model=invoice_sudo, report_type=report_type, report_ref='frogblue_reports.report_frogblue_account_invoice', download=download)

        values = self._invoice_get_page_view_values(invoice_sudo, access_token, **kw)
        acquirers = values.get('acquirers')
        if acquirers:
            country_id = values.get('partner_id') and values.get('partner_id')[0].country_id.id
            values['acq_extra_fees'] = acquirers.get_acquirer_extra_fees(invoice_sudo.amount_residual, invoice_sudo.currency_id, country_id)

        return request.render("account.portal_invoice_page", values)
