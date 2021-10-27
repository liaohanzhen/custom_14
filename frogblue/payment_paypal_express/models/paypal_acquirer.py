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
import pprint
import logging
_logger = logging.getLogger(__name__)

from odoo import models, fields, api, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.tools.float_utils import float_compare

class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('paypal_express', 'Paypal Checkout')],ondelete={'paypal_express': 'cascade'})
    paypal_client_id = fields.Char("Paypal Client ID", required_if_provider='paypal_express', help="Enter paypal client ID.")

    def paypal_express_form_generate_values(self, values):
        self.ensure_one()
        paypal_tx_values = dict(values)
        amount = values.get('amount')
        phone_no = values.get('billing_partner_phone') or values.get('partner_phone')
        phone_no = ''.join(e for e in str(phone_no) if e.isalnum())
        paypal_values = {
            'company': self.company_id.name,
            'amount': format(amount, '.2f'),
            'currency': values.get('currency') and values.get('currency').name or '',
            'currency_id': values.get('currency') and values.get('currency').id or '',

            'billing_first_name' : values.get('billing_partner_first_name') if values.get('billing_partner_first_name') else values.get('billing_partner_last_name'),
            'billing_last_name' : values.get('billing_partner_last_name') if values.get('billing_partner_first_name') else '',
            'billing_phone' : phone_no,
            'billing_email' : values.get('billing_partner_email') or values.get('partner_email'),

            'billing_address_l1' : values.get('billing_partner_address'),
            'billing_area1' : values.get('billing_partner_state') and values.get('billing_partner_state').code or '',
            'billing_area2' : values.get('billing_partner_city'),
            'billing_zip_code' : values.get('billing_partner_zip'),
            'billing_country_code' : values.get('billing_partner_country') and values.get('billing_partner_country').code or '',

            'shipping_partner_name' : values.get('partner_name'),
            'shipping_address_l1' : values.get('partner_address'),
            'shipping_area1' : values.get('partner_state') and values.get('partner_state').code or '',
            'shipping_area2' : values.get('partner_city'),
            'shipping_zip_code' : values.get('partner_zip'),
            'shipping_country_code' : values.get('partner_country') and values.get('partner_country').code or '',
        }
        paypal_values['returndata'] = paypal_tx_values.pop('return_url', '')
        paypal_tx_values.update(paypal_values)
        return paypal_tx_values

class TransactionPaypalExpress(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _paypal_express_form_get_tx_from_data(self, data):
        """ Given a data dict coming from paypal, verify it and find the related
        transaction record. Create a payment method if an alias is returned."""
        reference, amount, currency_name = data.get('invoice_num'), data.get('amount'), data.get('currency')
        tx_ids = self.env['payment.transaction'].search([('reference', '=', reference)])
        if not tx_ids or len(tx_ids) > 1:
            error_msg = 'received data for reference %s' % (pprint.pformat(reference))
            if not tx_ids:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        return tx_ids[0]

    def _paypal_express_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        if self.acquirer_reference and data.get('invoice_num') != self.acquirer_reference:
            invalid_parameters.append(('Transaction Invoice Id', data.get('invoice_num'), self.acquirer_reference))
        # check what is buyed
        if float_compare(float(data.get('amount', '0.0')), self.amount, 2) != 0:
            invalid_parameters.append(('Amount', data.get('amount'), '%.2f' % self.amount))
        if data.get('currency') != self.currency_id.name:
            invalid_parameters.append(('Currency', data.get('currency'), self.currency_id.name))
        return invalid_parameters

    def _paypal_express_form_validate(self, data):
        trans_state = data.get("state", False)
        if trans_state:
            self.write({
                'acquirer_reference':data.get('acquirer_reference'),
                'state_message': _("Paypal Payment Gateway Response :-") + data["state"]
            })
            if trans_state == 'COMPLETED':
                self._set_transaction_done()
            elif trans_state == "PENDING":
                self._set_transaction_pending()
            elif trans_state == "DECLINED":
                self._set_transaction_cancel()
            # elif trans_state == "PARTIALLY_REFUNDED":
            # elif trans_state == "REFUNDED":
