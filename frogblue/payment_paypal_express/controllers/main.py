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

import logging
_logger = logging.getLogger(__name__)

import odoo
from odoo import http, _
from odoo.http import request

class PaypalExpressRedirect(http.Controller):

    @http.route(['/paypal/express/checkout/url',], type='json', auth="public", methods=['POST'], website=True)
    def paypal_checkout_checkout_url(self, **post):
        pricelist = request.session.get('website_sale_current_pl')
        acquirer_obj = request.env['payment.acquirer'].search([('provider','=','paypal_express')], limit=1)
        if acquirer_obj:
            url = "https://www.paypal.com/sdk/js?client-id=" + str(acquirer_obj.paypal_client_id)
            lang = request.lang
            if pricelist:
                pricelist = request.env['product.pricelist'].browse(pricelist)
                if pricelist and pricelist.currency_id:
                    url += '&currency=' + str(pricelist.currency_id.name)
            if lang:
                url += '&locale=' + str(lang.code)
            return url
        return False

    @http.route(['/paypal/express/checkout/state',], type='json', auth="public", methods=['POST'], website=True)
    def paypal_checkout_checkout_state(self, **post):
        purchase_units = post.get('purchase_units')
        data = {}
        try:
            if purchase_units:
                purchase_units = purchase_units[0]
                data['invoice_num'] = purchase_units['reference_id']
                captures = purchase_units['payments']['captures']
                if captures:
                    captures = captures[0]
                    data['acquirer_reference'] = captures['id']
                    data['state'] = captures['status']
                    data['amount'] = captures['amount']['value']
                    data['currency'] = captures['amount']['currency_code']
        except Exception as e:
            _logger.info("~~~~~~~~~~~~~~EXCEPTION~~~~~~~~~~~%r~~~~~~~~~~~~~~~",e)
        res = request.env['payment.transaction'].sudo().form_feedback(data, 'paypal_express')
        return '/payment/process'

    @http.route(['/paypal/express/checkout/cancel'], type='json', auth="public", methods=['POST'], website=True)
    def paypal_checkout_checkout_cancel(self, **post):
        trans_id = request.session.get('__website_sale_last_tx_id',False)
        if trans_id:
            trans_obj = request.env['payment.transaction'].sudo().browse(int(trans_id)) if trans_id else None
            try:
                trans_obj._set_transaction_cancel()
            except Exception as e:
                _logger.info("~~~~~~~~Transaction already in process~~~~~~~~~")
        return '/payment/process'

    @http.route(['/paypal/express/checkout/error'], type='json', auth="public", methods=['POST'], website=True)
    def paypal_checkout_checkout_error(self, **post):
        error_msg = post.get('error',None)
        trans_id = request.session.get('__website_sale_last_tx_id',False)
        if trans_id and error_msg:
            trans_obj = request.env['payment.transaction'].sudo().browse(int(trans_id)) if trans_id else None
            try:
                trans_obj._set_transaction_error(msg)
            except Exception as e:
                _logger.info("~~~~~~~~Transaction already in process~~~~~~~~~")
        return '/payment/process'
