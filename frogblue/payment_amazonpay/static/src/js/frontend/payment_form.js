odoo.define('payment_amazonpay.payment_form', function (require) {
"use strict";


const ajax = require('web.ajax');
const core = require('web.core');
const utils = require('web.utils');
const PaymentForm = require('payment.payment_form');

const amzp_common = require('payment_amazonpay.common');


const _t = core._t;


PaymentForm.include({


    init: function ()
    {
        const result = this._super.apply(this, arguments);

        // determine interface language for use in Amazon widgets
        this._language = (utils.get_cookie('frontend_lang') || 'en_GB').replace('_', '-');

        return result;
    },


    willStart: function ()
    {
        const self = this;

        return this._super.apply(this, arguments).then(function ()
        {
            //
            // @TODO: implement more that one active Amazon Pay payment acquirer configuration
            //

            const $checkedRadio = self.$('input[data-provider="amazonpay"]');
            if ($checkedRadio.length)
            {
                // get container
                const $card = $checkedRadio.closest('.card-body');

                // add button element
                $('<div/>', {
                    id: 'AmazonPay_AmazonPayButton',
                    style: 'display: none !important;',
                }).appendTo($card);

                // add handlers
                window.onAmazonLoginReady = function() {
                    amazon.Login.setSandboxMode($checkedRadio.data('amazonpaySandbox') === 'true');
                    amazon.Login.setClientId($checkedRadio.data('amazonpayClientId'));
                    amazon.Login.setUseCookie(true);

                    //
                    // @TODO: may be region should be selected here also
                    //
                    //      AsiaPacific: "APAC"
                    //      Europe: "EU"
                    //      France: "FR"
                    //      Germany: "DE"
                    //      Italy: "IT"
                    //      Japan: "JP"
                    //      NorthAmerica: "NA"
                    //      Spain: "ES"
                    //      UnitedKindom: "UK"
                    //      UnitedStates: "US"
                    //
                    // const region = $input.data('amazonpayRegion');
                    // if (region == 'eu')
                    // {
                    //     amazon.Login.setRegion(amazon.Login.Region.Europe);
                    // }
                    // else if (region == 'uk')
                    // {
                    //     amazon.Login.setRegion(amazon.Login.Region.UnitedKindom);
                    // }
                    // else if (region == 'de')
                    // {
                    //     amazon.Login.setRegion(amazon.Login.Region.Germany);
                    // }
                    // else if (region == 'fr')
                    // {
                    //     amazon.Login.setRegion(amazon.Login.Region.France);
                    // }
                    // else if (region == 'it')
                    // {
                    //     amazon.Login.setRegion(amazon.Login.Region.Italy);
                    // }
                    // else if (region == 'es')
                    // {
                    //     amazon.Login.setRegion(amazon.Login.Region.Spain);
                    // }
                    // else if (region == 'us')
                    // {
                    //     amazon.Login.setRegion(amazon.Login.Region.UnitedStates);
                    // }
                    // else if (region == 'jp')
                    // {
                    //     amazon.Login.setRegion(amazon.Login.Region.Japan);
                    // }
                    // else if (region == 'apac')
                    // {
                    //     amazon.Login.setRegion(amazon.Login.Region.AsiaPacific);
                    // }
                    // else
                    // {
                    //     amazon.Login.setRegion(amazon.Login.Region.NorthAmerica);
                    // }
                };
                window.onAmazonPaymentsReady = function() {
                    self._amazonpay_initButton($checkedRadio.data('amazonpayMerchantId'));
                };

                // add wallet element
                self.$amazonpayWallet = $('<div/>', {
                    id: 'AmazonPay_WalletWidget',
                    style: 'display: none;',
                }).appendTo($card);

                // load Widgets.js
                return ajax.loadJS($checkedRadio.data('amazonpayWidgetsUrl'));
            }

            return $.when();
        });
    },


    updateNewPaymentDisplayStatus: function ()
    {
        const result = this._super.apply(this, arguments);

        const $checkedRadio = this.$('input[type="radio"]:checked');
        if ($checkedRadio.length !== 1) {
            return;
        }

        if ($checkedRadio.data('provider') === 'amazonpay')
        {
            this.$amazonpayWallet.show();
        }
        else
        {
            this.$amazonpayWallet.hide();
        }

        // @NOTE: do not hide error here, because on click to Amazon button
        // (to re-render widget) update selected payment will be called and
        // and error message will be cleared.
        // this.hideError();

        return result;
    },


    payEvent: function (event)
    {
        event.preventDefault();

        const self = this;

        // if this is Amazon Pay
        const $selectedAmazonPayment = self.getSelectedAmazonPayment();
        if ($selectedAmazonPayment)
        {
            if (!$selectedAmazonPayment.data('amazonpayOrderReferenceId'))
            {
                // emulate payment button click
                self._amazonpay_callButton($selectedAmazonPayment);
            }
            else
            {
                const orderReferenceId = $selectedAmazonPayment.data('amazonpayOrderReferenceId');
                if (!orderReferenceId)
                {
                    self.displayError(
                        _t("Cannot set-up the payment"),
                        _t("Amazon payment method not selected")
                    );
                }
                else
                {
                    //
                    // Copy part of process from base payment_form.js
                    //
                    const button = event.target;
                    self.disableButton(button);

                    // if there's a prepare tx url set
                    const $tx_url = self.$('input[name="prepare_tx_url"]');
                    if ($tx_url.length === 1 && $tx_url[0].value)
                    {
                        return ajax.jsonRpc($tx_url[0].value, 'call', {
                            'acquirer_id': parseInt(self.getAcquirerIdFromRadio($selectedAmazonPayment)),
                            'save_token': undefined,
                            'access_token': self.options.accessToken,
                            'success_url': self.options.successUrl,
                            'error_url': self.options.errorUrl,
                            'callback_method': self.options.callbackMethod,
                            'order_id': self.options.orderId,
                        })
                            .then(function (data)
                            {
                                if (data)
                                {
                                    // get result form
                                    const $data = $(data);

                                    return ajax.jsonRpc($data.find('input[name="data_set"]').data('actionUrl'), 'call', {
                                        'reference': $data.find('input[name="reference"]').val(),
                                        'tx_id': parseInt($data.find('input[name="tx_id"]').val(), 10),
                                        'amazonpay_order_reference_id': orderReferenceId,
                                    })
                                        .then(function (result)
                                        {
                                            if (result)
                                            {
                                                if (result.error)
                                                {
                                                    self.displayError(
                                                        result.error.title || _t("Amazon Pay transaction processing error"),
                                                        result.error.message
                                                    );

                                                    $selectedAmazonPayment.removeAttr('data-amazonpay-order-reference-id');
                                                    $selectedAmazonPayment.removeData('amazonpayOrderReferenceId');
                                                    self.$amazonpayWallet.empty();
                                                    OffAmazonPayments.Widgets.mediator.widgetCount -= OffAmazonPayments.Widgets.mediator.getWalletWidgets().length;
                                                    _.each(OffAmazonPayments.Widgets.mediator.getWalletWidgets(), function (wallet)
                                                    {
                                                        delete OffAmazonPayments.Widgets.mediator.registry[wallet.eventValue]
                                                    });

                                                    if (result.action === 'logout')
                                                    {
                                                        amzp_common.onLogout.call(self);
                                                    }
                                                    else if (result.action === 'reloadWallet')
                                                    {
                                                        self._amazonpay_callButton($selectedAmazonPayment);
                                                    }

                                                    self.enableButton(button);
                                                }
                                                else if (result.redirect)
                                                {
                                                    window.location = result.redirect;
                                                }
                                                else
                                                {
                                                    window.location.reload();
                                                }
                                            }
                                            else
                                            {
                                                window.location.reload();
                                            }
                                        });
                                }
                                else
                                {
                                    self.displayError(
                                        _t("Server Error"),
                                        _t("We are not able to redirect you to the payment form.")
                                    );
                                    self.enableButton(button);
                                }
                            })
                            .guardedCatch(function (error)
                            {
                                error.event.preventDefault();
                                self.displayError(
                                    _t("Amazon Pay transaction processing error"),
                                    self._parseError(error) || ''
                                );
                                self.enableButton(button);
                            });
                    }
                    else
                    {
                        self.displayError(
                            _t("Cannot set-up the payment"),
                            _t("We're unable to process your payment.")
                        );
                    }
                }
            }
        }
        else
        {
            // else - do super
            this._super.apply(this, arguments);
        }
    },


    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    getSelectedAmazonPayment: function ()
    {
        const $selectedPayment = this.$('input[type="radio"]:checked');
        if ($selectedPayment.length === 1 && $selectedPayment.data('provider') === 'amazonpay')
        {
            return $selectedPayment;
        }
        return undefined;
    },


    _amazonpay_initButton: function (merchantId)
    {
        const self = this;

        let authRequest;
        OffAmazonPayments.Button('AmazonPay_AmazonPayButton', merchantId, {
            type:  'PwA',
            color: 'Gold',
            size:  'medium',
            language: self._language,

            authorization: function()
            {
                authRequest = amazon.Login.authorize({
                    scope: 'payments:widget',
                    popup: true,                // @TODO: implement non-popup mode
                }, function (response) {
                    //
                    // Authorization response is object:
                    //      status
                    //      scope
                    //      token_type
                    //      access_token
                    //      expires_in
                    //
                    if (response.error)
                    {
                        let message = response.error_description || response.error;
                        if (response.error_uri)
                        {
                            message += ' (' + response.error_uri + ')';
                        }
                        self.displayError(response.error, message)
                    }
                    else
                    {
                        self._amazonpay_showWalletWidget(merchantId);
                    }
                });
            }
        });
    },


    _amazonpay_callButton: function ($checkedRadio)
    {
        $checkedRadio = $checkedRadio || this.getSelectedAmazonPayment();
        if ($checkedRadio)
        {
            $checkedRadio
                .closest('.card-body')
                .find('#AmazonPay_AmazonPayButton > img.amazonpay-button-inner-image')
                .click();
        }
    },


    _amazonpay_showWalletWidget: function (merchantId)
    {
        const self = this;

        this.$amazonpayWallet.show();
        new OffAmazonPayments.Widgets.Wallet({
            sellerId: merchantId,
            design: {
                designMode: 'smartphoneCollapsible'
            },

            // Add the onOrderReferenceCreate function to generate an Order Reference ID.
            // @see https://developer.amazon.com/docs/amazon-pay-onetime/no-address-widget.html
            onOrderReferenceCreate: function (orderReference)
            {
                const $selectedAmazonPayment = self.getSelectedAmazonPayment();
                if ($selectedAmazonPayment)
                {
                    // remember order reference ID
                    const orderReferenceId = orderReference.getAmazonOrderReferenceId();
                    $selectedAmazonPayment.attr('data-amazonpay-order-reference-id', orderReferenceId);
                }
            },
            // onReady: function (orderReference)
            // {
            //     console.log(orderReference.getAmazonOrderReferenceId());
            // },
            onPaymentSelect: function ()
            {
                //
                // Replace this code with the action that you want to perform
                // after the payment method is chosen.
                // Ideally this would enable the next action for the buyer
                // including either a "Continue" or "Place Order" button.
                //
                // @TODO: check that payment method really selected
                // When Wallet widget loaded no any payment selected and a special
                // button "Use this payment method" shown (AmazonOrderReferenceId
                // not created yet).
                // But when we press this button 'onPaymentSelect' handler not
                // called but AmazonOrderReferenceId created and 'onOrderReferenceCreate'
                // handler called.
                // So, for check that payment method selected we can check that
                // AmazonOrderReferenceId exists but this is not explicit.
                //
            },
            onError: function (error)
            {
                // Error handling code
                // @see https://payments.amazon.com/documentation/lpwa/201954960
                self.displayError(error.getErrorCode(), error.getErrorMessage());
            }
        }).bind('AmazonPay_WalletWidget');
    },


});


//
// try to bind to frontend menu item
//
require('web.dom_ready');
const $logoutMenuItem = $('#o_logout');
if ($logoutMenuItem.length)
{
    $logoutMenuItem.click(function ()
    {
        amzp_common.onLogout.call(this);
    });
}


});
