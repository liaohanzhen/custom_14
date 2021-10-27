# -*- coding: utf-8 -*-


import logging
import uuid
import werkzeug
import json

from amazon_pay.client import AmazonPayClient

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

from ..controllers.main import AmazonPayController


_logger = logging.getLogger(__name__)


#
#
#
class AmazonPayPaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('amazonpay', "Amazon Pay")],
                                ondelete={'amazonpay': 'set default'})

    amazonpay_merchant_id = fields.Char(string="Merchant ID", groups='base.group_user')
    amazonpay_mws_access_key = fields.Char(string="MWS Access Key", groups='base.group_user')
    amazonpay_mws_secret_key = fields.Char(string="MWS Secret Key", groups='base.group_user')
    amazonpay_client_id = fields.Char(string="Client ID", groups='base.group_user')

    amazonpay_region = fields.Selection(selection=[
        ('us', "US"),
        ('eu', "EU"),
        ('uk', "UK"),
        ('de', "DE"),
        ('jp', "JP"),
        ('na', "NA"),
    ], string="Region", default='na')

    amazonpay_sandbox = fields.Boolean(compute='_compute_amazonpay_urls')
    amazonpay_widgets_url = fields.Char(string="Widgets URL", compute='_compute_amazonpay_urls')
    amazonpay_ipn_url = fields.Char(string="IPN URL", compute='_compute_amazonpay_urls')

    amazonpay_close_order_reference_after_capture = fields.Boolean(string="Close order reference after capture", default=True)

    #
    #
    #
    @api.constrains('provider', 'state')
    def _amazonpay_check_state(self):
        """ This version of module supports only one active configuration
            of Amazon Pay payment acquirer.
        """
        if self.sudo().search_count([
            ('provider', '=', 'amazonpay'),
            ('state', '!=', 'disabled'),
        ]) > 1:
            # raise exception for rollback transaction
            raise ValidationError(_("Only one active Amazon Pay payment acquirer configuration supported now!"))

    #
    #
    #
    @api.onchange('amazonpay_region')
    @api.depends('amazonpay_region')
    def _compute_amazonpay_urls(self):
        for record in self:
            if record.provider == 'amazonpay':
                record.amazonpay_sandbox = (record.state == 'test')

                #
                # calculate Widgets.js URL
                #
                if record.amazonpay_region in ('eu', 'de'):
                    widgets_url = 'https://static-eu.payments-amazon.com/OffAmazonPayments/eur%s/lpa/js/Widgets.js'
                elif record.amazonpay_region == 'uk':
                    widgets_url = 'https://static-eu.payments-amazon.com/OffAmazonPayments/gbp%s/lpa/js/Widgets.js'
                elif record.amazonpay_region == 'jp':
                    widgets_url = 'https://static-fe.payments-amazon.com/OffAmazonPayments/jp%s/lpa/js/Widgets.js'
                else:
                    widgets_url = 'https://static-na.payments-amazon.com/OffAmazonPayments/us%s/js/Widgets.js'

                record.amazonpay_widgets_url = widgets_url % (record.amazonpay_sandbox and '/sandbox' or '')

                # get base URL
                base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                record.amazonpay_ipn_url = werkzeug.urls.url_join(base_url, AmazonPayController._ipn_url)

            else:
                record.amazonpay_sandbox = False
                record.amazonpay_widgets_url = None
                record.amazonpay_ipn_url = None

    #
    #
    #
    def _get_feature_support(self):
        """ Get advanced feature support by provider.

        Each provider should add its technical in the corresponding
        key for the following features:
            * fees: support payment fees computations
            * authorize: support authorizing payment (separates
                         authorization and capture)
            * tokenize: support saving payment data in a payment.tokenize
                        object
        """
        res = super()._get_feature_support()

        res['authorize'].append('amazonpay')    # https://developer.amazon.com/docs/amazon-pay-onetime/request-an-authorization.html
        # res['fees'].append('amazonpay')       # @NOTE: precalc fees not supported
        # res['tokenize'].append('amazonpay')   # @TODO: https://developer.amazon.com/docs/amazon-pay-automatic/intro.html

        return res

    #
    #
    #
    def amazonpay_get_form_action_url(self):
        # return own url for request acquirer on server side
        return AmazonPayController._request_url

    def amazonpay_form_generate_values(self, values):
        """ Prepare params for render form

        :param values:
        :return:
        """
        amazonpay_values = dict(values)

        #
        # add a special params for use on request acquirer
        #
        reference = str(values.get('reference'))
        if reference and reference != '/':
            tx = self.env['payment.transaction'].sudo().search([('reference', '=', reference)], limit=1)
            if tx:
                amazonpay_values['tx_id'] = tx.id

        # return params
        return amazonpay_values


#
#
#
class AmazonPayPaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    capture_manually = fields.Boolean(related='acquirer_id.capture_manually')
    amount_str = fields.Char(compute='_compute_amount_str')

    amazonpay_seller_authorize_reference_id = fields.Char(string="Seller Auth ID", readonly=True, index=True,
                                                          help="Merchant (seller) side operation ID. This identifier must be unique for all your transactions (authorization, capture, refund, etc.).")
    amazonpay_amazon_authorize_reference_id = fields.Char(string="Amazon Auth ID", readonly=True)

    amazonpay_seller_capture_id = fields.Char(string="Seller Capture ID", readonly=True, index=True,
                                              help="Merchant (seller) side operation ID. This identifier must be unique for all your transactions (authorization, capture, refund, etc.).")
    amazonpay_amazon_capture_id = fields.Char(string="Amazon Capture ID", readonly=True)

    amazonpay_seller_refund_id = fields.Char(string="Seller Refund ID", readonly=True, index=True,
                                              help="Merchant (seller) side operation ID. This identifier must be unique for all your transactions (authorization, capture, refund, etc.).")
    amazonpay_amazon_refund_id = fields.Char(string="Amazon Refund ID", readonly=True)

    amazonpay_log_ids = fields.One2many(comodel_name='payment.transaction.amazonpay.log',
                                        inverse_name='transaction_id',
                                        groups='base.group_system',
                                        string="Amazon Pay Log")

    #
    #
    #
    @api.onchange('amount')
    @api.depends('amount')
    def _compute_amount_str(self):
        for record in self:
            record.amount_str = '%0.2f' % self.amount

    #
    #
    #
    # --------------------------------------------------
    # SERVER2SERVER RELATED METHODS
    # --------------------------------------------------

    def amazonpay_s2s_do_transaction(self, **kwargs):
        self.ensure_one()

        # check current state
        if self.state not in ('draft', 'error'):
            raise ValidationError(_("Not allowed transaction state"))
        if not self.acquirer_reference:
            raise ValidationError(_("Amazon order reference ID not specified"))

        # get client instance
        client = self._amazonpay_create_client()

        #
        # 1. Send order info
        #
        res = self._amazonpay_call_api(
            'set_order_reference_details',
            dict(
                amazon_order_reference_id=self.acquirer_reference,
                order_total=self.amount_str,
                seller_order_id=self.reference,
                # @TODO: set additional params (store_name, seller_note, custom_information)
            ),
            client=client
        )
        # there is not expected any specific result accept basic errors handling,
        # so just go on to the next step

        #
        # 2. Confirm order
        #
        res = self._amazonpay_call_api(
            'confirm_order_reference',
            dict(
                amazon_order_reference_id=self.acquirer_reference
            ),
            client=client
        )
        # there is not expected any specific result accept basic errors handling,
        # so just go on to the next step

        #
        # 3. @TODO: Make a call to the GetOrderReferenceDetails.
        # After you successfully confirm the order reference, you should call
        # the GetOrderReferenceDetails API to get the remaining buyer information,
        # like name and shipping address, to ensure that you retrieved the latest address.
        #

        #
        # We no need to switch transaction to pending here, because pending
        # may switch order state to 'sent' and remove them from cart, but
        # same action will be done by switching to 'authorized' state above.
        #
        # self._set_transaction_pending()

        #
        # 4. Authorize payment (with capture capture if need)
        #
        # @NOTE: only synchronous mode supported now!
        #
        amazonpay_seller_authorize_reference_id = self._amazonpay_get_seller_id()
        res = self._amazonpay_call_api(
            'authorize',
            dict(
                amazon_order_reference_id=self.acquirer_reference,
                authorization_reference_id=amazonpay_seller_authorize_reference_id,
                authorization_amount=self.amount_str,
                transaction_timeout=0,      # @TODO: implement Asynchronous Authorization as option (https://developer.amazon.com/docs/amazon-pay-onetime/request-an-authorization.html)
                capture_now=not self.capture_manually
                # @TODO: set additional params (seller_authorization_note, soft_descriptor)
            ),
            client=client
        )

        #
        # 5. Analyze result for check authorization state
        # (@see https://developer.amazon.com/docs/amazon-pay-onetime/handle-decline.html)
        # (@see https://developer.amazon.com/docs/amazon-pay-api/authorization-states-and-reason-codes.html)
        #
        auth_status = self._amazonpay_get_result(res, 'AuthorizeResponse.AuthorizeResult.AuthorizationDetails.AuthorizationStatus')
        auth_state = auth_status.get('State')
        auth_reason_code = auth_status.get('ReasonCode')
        action = 'reloadWallet'
        error_message = None
        if auth_state == 'Declined':
            error_message = _("The authorization has been declined by Amazon.")

            if auth_reason_code == 'InvalidPaymentMethod':
                error_message += ' %s: %s' % (auth_reason_code, _("That payment method was not accepted for this transaction. Please choose another."))

            elif auth_reason_code == 'TransactionTimedOut':
                # this message is specific for synchronous mode
                error_message += ' %s: %s' % (auth_reason_code, _("Amazon could not process your within the default timeout; try to repeat please."))

            elif auth_reason_code == 'AmazonRejected':
                action = 'logout'
                error_message += ' %s: %s' % (auth_reason_code, _("Your payment was not successful. Please try another payment method."))

            elif auth_reason_code == 'ProcessingFailure':
                error_message += ' %s: %s' % (auth_reason_code, _("Your payment was not successful. Please try another payment method."))

        #
        # Skip checking 'Closed' state value here, because it's may be normal.
        #
        # For example, if we use CaptureNow option, then will be returned
        # state = 'Closed' with reason 'MaxCapturesProcessed' and it is not
        # error and transaction should be DONE.
        #
        # Otherwise, we can get some cases when it is error, so
        # @TODO: check this carefully
        #
        # elif auth_state == 'Closed':
        #     error_message = _("The authorization has been closed.")
        #
        #     if auth_reason_code == 'ExpiredUnused':
        #         error_message += ' %s: %s' % (auth_reason_code, _("The authorization has been in the Open state for 30 days (two days for Sandbox), and you did not submit any captures against it."))
        #
        #     elif auth_reason_code == 'MaxCapturesProcessed':
        #         error_message += ' %s: %s' % (auth_reason_code, _("You have already captured the full amount of the authorization. Amazon allows only one capture per authorization."))
        #
        #     elif auth_reason_code == 'AmazonClosed':
        #         error_message += ' %s: %s' % (auth_reason_code, _("Amazon has closed the authorization object because of problems with your account."))
        #
        #     elif auth_reason_code == 'OrderReferenceCanceled':
        #         error_message += ' %s: %s' % (auth_reason_code, _("The order reference was canceled causing all open authorizations to be canceled."))
        #
        #     elif auth_reason_code == 'SellerClosed':
        #         error_message += ' %s: %s' % (auth_reason_code, _("You have explicitly closed the authorization using the CloseAuthorization operation."))

        if error_message:
            # try to close order
            self._amazonpay_do_close_order_reference(client)

            # and switch to error state
            self._set_transaction_error(error_message)

            # and return result to client
            return {
                'action': action,
                'error': {
                    'message': error_message
                }
            }

        #
        # 6. Switch state to 'authorized'.
        #
        # This action may switch order state to 'sent' and remove them from
        # cart, same as switching ot pending state, so switching to pending
        # no need at all.
        #
        self._set_transaction_authorized()

        #
        # 7. Post-authorize
        #
        self.amazonpay_seller_authorize_reference_id = amazonpay_seller_authorize_reference_id
        self.amazonpay_amazon_authorize_reference_id = self._amazonpay_get_result(res, 'AuthorizeResponse.AuthorizeResult.AuthorizationDetails.AmazonAuthorizationId')
        if self.capture_manually:
            # Save authorization ID for use in capture (if need)
            self._amazonpay_log("Save authorize reference ID for capture manually [%s]", (
                self.amazonpay_amazon_authorize_reference_id,
            ))

            # return action result
            return True
        else:
            # seller capture ID same as authorize ID in this case
            self.amazonpay_seller_capture_id = amazonpay_seller_authorize_reference_id

            # Or do postprocess and return result (close order reference, if need)
            return self._amazonpay_do_capture_postprocess(client)

    def amazonpay_s2s_capture_transaction(self, **kwargs):
        self.ensure_one()

        # check current state
        if self.state != 'authorized':
            raise ValidationError(_("Capture allowed in 'Authorized' state only"))
        if not self.amazonpay_amazon_authorize_reference_id:
            raise ValidationError(_("Amazon authorize reference ID not specified."))

        # get client instance
        client = self._amazonpay_create_client()

        # do capture
        amazonpay_seller_capture_id = self._amazonpay_get_seller_id()
        res = self._amazonpay_call_api(
            'capture',
            dict(
                amazon_authorization_id=self.amazonpay_amazon_authorize_reference_id,
                capture_reference_id=amazonpay_seller_capture_id,
                capture_amount=self.amount_str,
                # @TODO: set additional params (seller_capture_note, soft_descriptor)
            ),
            client=client
        )

        #
        # Analyze result for check capture state
        # (@see https://developer.amazon.com/docs/amazon-pay-api/capture-states-and-reason-codes.html)
        #
        capture_status = self._amazonpay_get_result(res, 'CaptureResponse.CaptureResult.CaptureDetails.CaptureStatus')
        capture_state = capture_status.get('State')
        capture_reason_code = capture_status.get('ReasonCode')
        error_message = None
        if capture_state == 'Declined':
            error_message = _("The capture has been declined by Amazon.")

            if capture_reason_code == 'AmazonRejected':
                error_message += ' %s: %s' % (capture_reason_code, _("Amazon has rejected the capture. You should only retry the capture if the authorization is in the Open state."))

            elif capture_reason_code == 'ProcessingFailure':
                error_message += ' %s: %s' % (capture_reason_code, _("Amazon could not process the transaction because of an internal processing error. You should only retry the capture if the authorization is in the Open state. Otherwise, you should request a new authorization and then call Capture on it."))

        elif capture_state == 'Closed':
            error_message = _("The capture has been closed.")

            if capture_reason_code == 'MaxAmountRefunded':
                error_message += ' %s: %s' % (capture_reason_code, _("You have already refunded the following amounts, including any A-to-z claims and chargebacks."))

            elif capture_reason_code == 'MaxRefundsProcessed':
                error_message += ' %s: %s' % (capture_reason_code, _("You have already submitted 10 refunds for this Capture object."))

            elif capture_reason_code == 'AmazonClosed':
                error_message += ' %s: %s' % (capture_reason_code, _("Amazon has closed the capture because of a problem with your account or with the buyer's account."))

        if error_message:
            # and switch to error state
            self._set_transaction_error(error_message)

            # raise error
            raise UserError(error_message)

        #
        # save capture ID
        #
        self.amazonpay_seller_capture_id = amazonpay_seller_capture_id
        self.amazonpay_amazon_capture_id = self._amazonpay_get_result(res, 'CaptureResponse.CaptureResult.CaptureDetails.AmazonCaptureId')

        # do postprocess and return result
        return self._amazonpay_do_capture_postprocess(client)

    def amazonpay_s2s_void_transaction(self, **kwargs):
        self.ensure_one()

        # just close order reference
        if not self._amazonpay_do_close_order_reference():
            return False

        # switch transaction state
        self._set_transaction_cancel()

        # return action result
        return True

    def amazonpay_s2s_do_refund(self, **kwargs):
        self.ensure_one()

        # check current state
        if self.state in ('authorized', 'done', 'error'):   # @TODO: check this
            raise ValidationError(_("Not allowed transaction state '%s' for refund") % self.state)
        if not self.amazonpay_amazon_capture_id:
            raise ValidationError(_("Amazon capture reference ID not specified."))

        # do refund
        amazonpay_seller_refund_id = self._amazonpay_get_seller_id()
        res = self._amazonpay_call_api(
            'refund',
            dict(
                amazon_capture_id=self.amazonpay_amazon_capture_id,
                refund_reference_id=self.amazonpay_seller_reference_id,
                refund_amount=self.amount_str
                # @TODO: set additional params (seller_refund_note, soft_descriptor)
            )
        )

        #
        # Analyze result for check capture state
        # (@see https://developer.amazon.com/docs/amazon-pay-api/capture-states-and-reason-codes.html)
        #
        refund_status = self._amazonpay_get_result(res, 'RefundResponse.RefundResult.RefundDetails.RefundStatus')
        refund_state = refund_status.get('State')
        refund_reason_code = refund_status.get('ReasonCode')
        error_message = None
        if refund_state == 'Declined':
            error_message = _("The refund has been declined by Amazon.")

            if refund_reason_code == 'AmazonRejected':
                error_message += ' %s: %s' % (refund_reason_code, _("Amazon has rejected the refund. You should issue a refund to the buyer in an alternate manner (for example, a gift card or store credit)."))

            elif refund_reason_code == 'ProcessingFailure':
                error_message += ' %s: %s' % (refund_reason_code, _("Amazon could not process the transaction because of an internal processing error or because the buyer has already received a refund from an A-to-z claim or a chargeback. You should only retry the refund if the Capture object is in the Completed state. Otherwise, you should refund the buyer in an alternative way (for example, a store credit or a check)."))

        if error_message:
            # and switch to error state
            self._set_transaction_error(error_message)

            # raise error
            raise UserError(error_message)

        #
        # save refund ID
        #
        self.amazonpay_seller_refund_id = amazonpay_seller_refund_id
        self.amazonpay_amazon_refund_id = self._amazonpay_get_result(res, 'RefundResponse.RefundResult.RefundDetails.AmazonRefundId')

        # @TODO: may be need to change transaction state here ?

        # return action result
        return True

    #
    #
    #
    def _amazonpay_do_capture_postprocess(self, client=None):
        self.ensure_one()

        #
        # Mark the order reference as closed on capture if specified.
        # @see https://developer.amazon.com/docs/amazon-pay-onetime/mark-order-as-closed.html
        #
        if self.acquirer_id.amazonpay_close_order_reference_after_capture:
            self._amazonpay_log("Close order (auto) after capture")
            if not self._amazonpay_do_close_order_reference(client):
                return False

        # switch transaction state here
        self._set_transaction_done()

        # return result
        return True

    def _amazonpay_do_close_order_reference(self, client=None):
        self.ensure_one()

        #
        # Check current transaction state
        # (do not check transaction state value and do not switch
        # to 'error' state here, just leave order reference)
        #
        if not self.acquirer_reference:
            raise ValidationError(_("Amazon order reference ID not specified"))
        if self.state in ('done', 'cancel'):
            _logger.warning("Amazon Pay: trying to void an already performed tx (ref %s)" % self.reference)

        # get client instance
        if not client:
            client = self._amazonpay_create_client()

        #
        # Firstly, try to close authorization.
        #
        # @TODO: check this, may be not need at all, and close_order_reference is enough.
        #
        if self.state == 'authorized' and self.amazonpay_amazon_authorize_reference_id:
            res = self._amazonpay_call_api(
                'close_authorization',
                dict(
                    amazon_authorization_id=self.amazonpay_amazon_authorize_reference_id,
                    # @TODO: set additional params (closure_reason)
                ),
                client=client,
                switch_state=False,     # do not switch to 'error' state
                raise_error=False,      # and do not raise any errors, just log
            )
            # there is not expected any specific result accept basic errors handling,
            # so just go on to the next step

        #
        # Mark the order reference as closed on capture if specified.
        # @see https://developer.amazon.com/docs/amazon-pay-onetime/mark-order-as-closed.html
        #
        res = self._amazonpay_call_api(
            'close_order_reference',
            dict(
                amazon_order_reference_id=self.acquirer_reference
                # @TODO: set additional params (closure_reason)
            ),
            client=client,
            switch_state=False,     # do not switch to 'error' state
            raise_error=False,      # and do not raise any errors, just log
        )
        # there is not expected any specific result accept basic errors handling,
        # so just go on to the next step

        # return True always (no matter close operation result)
        return True

    #
    #
    #
    def _amazonpay_create_client(self):
        self.ensure_one()
        self._amazonpay_log("Create client [%s, %s]", (
            self.acquirer_id.amazonpay_merchant_id,
            self.acquirer_id.amazonpay_region
        ))
        return AmazonPayClient(
            mws_access_key=self.acquirer_id.amazonpay_mws_access_key,
            mws_secret_key=self.acquirer_id.amazonpay_mws_secret_key,
            merchant_id=self.acquirer_id.amazonpay_merchant_id,
            region=self.acquirer_id.amazonpay_region,
            currency_code=self.currency_id.name,
            sandbox=self.acquirer_id.amazonpay_sandbox,
            log_enabled=self.acquirer_id.amazonpay_sandbox,
            log_level='INFO',
        )

    def _amazonpay_call_api(self, method, params, client=None, switch_state=True, raise_error=True):
        self.ensure_one()

        # get client instance
        if not client:
            client = self._amazonpay_create_client()

        # log request params
        self._amazonpay_log('%s(%s)' % (method, params))

        # call API
        res_dict = {}
        res_json = '{}'
        try:
            res = getattr(client, method)(**params)
            res_dict = res.to_dict()
            res_json = res.to_json()
        except Exception as ex:
            _logger.error("Amazon Pay API call error", exc_info=ex)
            # @TODO: Handle errors from Amazon Pay API calls (@see https://developer.amazon.com/docs/amazon-pay-onetime/handling-api-errors.html)
            if raise_error:
                raise

        # log result
        self._amazonpay_log("%s RESULT: %s", (method, res_json))

        # write into journal log
        self.env['payment.transaction.amazonpay.log'].sudo().create({
            'transaction_id': self.id,
            'operation': method,
            'sent': json.dumps(params or {}),
            'received': res_json,
        })

        # analyze on errors and return result
        if switch_state or raise_error:
            # check error in response
            error = self._amazonpay_get_result(res_dict, 'ErrorResponse.Error')
            if error:
                # get error message
                error_message = '%s: %s' % (error.get('Code', ''), error.get('Message', ''))

                # switch transaction to error state
                if switch_state:
                    self._set_transaction_error(error_message)

                # raise error
                if raise_error:
                    raise UserError(error_message)

        # return response dict
        return res_dict

    def _amazonpay_log(self, message, params=None):
        self.ensure_one()
        if self.acquirer_id.amazonpay_sandbox:
            msg = 'AMAZON PAY [%s/%s]. ' % (self.reference, self.acquirer_reference) + message
            if params:
                msg = msg % params
            _logger.info(msg)

    @staticmethod
    def _amazonpay_get_result(res_dict, path):
        value = None

        if res_dict and path:
            path_elements = path.split('.')
            value = res_dict
            for el in path_elements:
                value = value.get(el)
                if not value:
                    return value

        return value

    @staticmethod
    def _amazonpay_get_seller_id():
        # @NOTE: this value length limited to 32 symbols by Amazon Pay
        return str(uuid.uuid4()).replace('-', '')


#
#
#
class AmazonPayPaymentTransactionLog(models.Model):
    _name = 'payment.transaction.amazonpay.log'
    _description = "Amazon Pay payment transaction log"
    _order = 'id'

    transaction_id = fields.Many2one(comodel_name='payment.transaction', ondelete='cascade', required=True)

    operation = fields.Char(string="Operation", required=True, readonly=True)
    sent = fields.Text(string="Sent", readonly=True)
    received = fields.Text(string="Received", required=True, readonly=True)

