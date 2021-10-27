# -*- coding: utf-8 -*-


import logging
import pprint

from odoo import SUPERUSER_ID, _
from odoo.http import Controller, route, request
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)


class AmazonPayController(Controller):

    _request_url = '/payment/amazonpay/request'
    _ipn_url = '/payment/amazonpay/ipn'

    _validate_url = '/payment/process'
    _payment_url = '/shop/payment'

    #
    #
    #
    @route(_request_url, type='json', auth='none', methods=['POST'], csrf=False)
    def payment_amazonpay_request(self, **kwargs):
        # get request params
        reference = kwargs.get('reference')
        tx_id = kwargs.get('tx_id')
        amazonpay_order_reference_id = kwargs.get('amazonpay_order_reference_id')

        # check params
        if not reference or not tx_id:
            raise ValidationError(_("Transaction not found"))
        if not amazonpay_order_reference_id:
            raise ValidationError(_("Amazon payment method not selected"))

        # try to find transaction
        tx = request.env['payment.transaction'].sudo().search([
            ('id', '=', tx_id),
            ('reference', '=', reference),
            # ('acquirer_reference', '=', False),   # @TODO: may be check this ?
            ('state', '=', 'draft'),
        ])
        if not tx:
            raise ValidationError(_("Transaction not found"))

        #
        # Here is workaround for combination of sale + stock + mailing +
        # multi-company + multi-website.
        #
        # For some reason, in this combination we have not uid and company
        # in environment after sudo() call, but it strongly need for
        # next steps of payment postprocessing (stock: requires company;
        # mailing: requires user) and so it cause crush on payment apply.
        #
        # So we had to setup superuser and company directly here.
        #
        tx = tx.with_user(SUPERUSER_ID).with_company(tx.acquirer_id.company_id.id)

        #
        # save Amazon Order Reference ID and process transaction
        #
        tx.acquirer_reference = amazonpay_order_reference_id
        result = tx.s2s_do_transaction()

        # return redirect URL if success
        if result and isinstance(result, bool):
            result = {
                'redirect': self._validate_url,
            }

        # return result
        return result

    #
    #
    #
    @route(_ipn_url, type='http', auth='none', methods=['POST', 'GET'], csrf=False)
    def payment_amazonpay_ipn(self, **kwargs):
        #
        # @TODO
        #
        _logger.info("Amazon Pay IPN: %s", pprint.pformat(kwargs))

