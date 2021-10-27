# -*- coding: utf-8 -*-
#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
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

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
from odoo.exceptions import AccessError
from odoo.http import request
from odoo.tools import consteq

class PortalAccount(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(PortalAccount, self)._prepare_portal_layout_values()
        partner = request.env.user.partner_id

        customer_quote_count = request.env['quote.quote'].search_count([
            ('customer_id', '=', partner.id),
        ])
        values['customer_quote_count'] = customer_quote_count
        return values

    # ------------------------------------------------------------
    # My Quote Requests
    # ------------------------------------------------------------

    def _customer_quote_check_access(self, quote_id, access_token=None):
        customer_quote = request.env['quote.quote'].browse([quote_id])
        customer_quote_sudo = customer_quote.sudo()
        try:
            customer_quote.check_access_rights('read')
            customer_quote.check_access_rule('read')
        except AccessError:
            if not access_token or not consteq(customer_quote_sudo.access_token, access_token):
                raise
        return customer_quote_sudo

    def _customer_quote_get_page_view_values(self, customer_quote, access_token, **kwargs):

        # CHECK IF PRODUCT WITHOUT QUOTE ALREADY EXIST IN CART
        values = {
            'page_name': 'customer_quote',
            'customer_quote': customer_quote,
            # 'product_line_found': False,
        }
        if access_token:
            values['no_breadcrumbs'] = True
        if kwargs.get('error'):
            values['error'] = kwargs['error']
        if kwargs.get('warning'):
            values['warning'] = kwargs['warning']
        if kwargs.get('success'):
            values['success'] = kwargs['success']
        return values

    @http.route(['/my/quote', '/my/quote/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_quote_request(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        CustomerQuote = request.env['quote.quote']

        domain = [
            ('customer_id', '=', partner.id),
        ]

        searchbar_sortings = {
            'create_date': {'label': _('Create Date'), 'order': 'create_date desc'},
            'status': {'label': _('Status'), 'order': 'status'},
        }
        # default sort by order
        if not sortby:
            sortby = 'create_date'
        order = searchbar_sortings[sortby]['order']

        # archive_groups = self._get_archive_groups('quote.quote', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # count for pager
        quotation_count = CustomerQuote.search_count(domain)

        # make pager
        pager = request.website.pager(
            url="/my/quote",
            url_args={'date_begin': date_begin, 'date_end': date_end},
            total=quotation_count,
            page=page,
            step=self._items_per_page
        )
        # search the count to display, according to the pager data
        quotations = CustomerQuote.search(domain, limit=self._items_per_page, offset=pager['offset'], order=order)
        request.session['my_quote_requests_history'] = quotations.ids[:100]
        values.update({
            'date': date_begin,
            'quotations': quotations,
            'pager': pager,
            # 'archive_groups': archive_groups,
            'default_url': '/my/quote',
            'page_name': 'customer_quote',
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })
        return request.render("website_quote_system.portal_my_customer_quotes", values)

    @http.route(['/my/quote/<int:quote_id>'], type='http', auth="user", website=True)
    def portal_my_quote_requests_detail(self, quote_id=None, access_token=None, **kw):
        quote = request.env['quote.quote'].browse([quote_id])
        if not quote.exists():
            return request.render('website_quote_system.404')
        try:
            customer_quote_sudo = self._customer_quote_check_access(quote_id, access_token)
        except AccessError:
            return request.redirect('/my')

        values = self._customer_quote_get_page_view_values(customer_quote_sudo, access_token, **kw)
        history = request.session.get('my_quote_requests_history', [])
        values.update(get_records_pager(history, customer_quote_sudo))
        return request.render("website_quote_system.portal_quote_requests_page", values)
