/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

odoo.define('payment_paypal_express.express_checkout', function (require) {
    "use strict";

    var publicWidget = require('web.public.widget');
    var PaymentForm = require('payment.payment_form');
    var ajax = require('web.ajax');

    var core = require('web.core');
    var _t = core._t;

    function get_payer_data(data_values){
        var payer = {}
        if(!data_values){
            return payer
        }
        if(data_values.billing_first_name || data_values.billing_last_name){
            var name = {}
            if(data_values.billing_first_name){
                name['given_name'] = data_values.billing_first_name
            }
            if(data_values.billing_last_name){
                name['surname'] = data_values.billing_last_name
            }
            payer['name'] = name
        }
        var address = {}
        if(data_values.billing_address_l1){
            address['address_line_1'] = data_values.billing_address_l1
        }
        if(data_values.billing_area2){
            address['admin_area_2'] = data_values.billing_area2
        }
        if(data_values.billing_area1){
            address['admin_area_1'] = data_values.billing_area1
        }
        if(data_values.billing_zip_code){
            address['postal_code'] = data_values.billing_zip_code
        }
        if(data_values.billing_country_code){
            address['country_code'] = data_values.billing_country_code
        }
        payer['address'] = address
        if(data_values.billing_email){
            payer['email_address'] = data_values.billing_email
        }
        if(data_values.billing_phone.match('^[0-9]{1,14}?$')){
            payer['phone'] = {
                phone_type: "MOBILE",
                phone_number: {
                    national_number: data_values.billing_phone,
                }
            }
        }
        return payer
    }
    function get_shipping_data(data_values){
        var shipping = {}
        if(!data_values){
            return shipping
        }
        if(data_values.shipping_partner_name){
            shipping['name'] = {
                full_name: data_values.shipping_partner_name,
            }
        }
        var shipping_address = {}
        if(data_values.shipping_address_l1){
            shipping_address['address_line_1'] = data_values.shipping_address_l1
        }
        if(data_values.shipping_area2){
            shipping_address['admin_area_2'] = data_values.shipping_area2
        }
        if(data_values.shipping_area1){
            shipping_address['admin_area_1'] = data_values.shipping_area1
        }
        if(data_values.shipping_zip_code){
            shipping_address['postal_code'] = data_values.shipping_zip_code
        }
        if(data_values.shipping_country_code){
            shipping_address['country_code'] = data_values.shipping_country_code
        }
        shipping['address'] = shipping_address
        return shipping
    }

    publicWidget.registry.PaypalCheckoutButton = publicWidget.Widget.extend({
        selector: '#paypal-button',
        willStart: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                return self._rpc({
                    route: '/paypal/express/checkout/url',
                    params: {}
                }).then(function(url){
                    if(url){
                        return ajax.loadJS(url).then(function(){
                            self.checkout_override();
                        });
                    }
                });
            });
        },
        get_btn_style: function(){
            return {
                size: 'small',
                color: 'blue',
                shape: 'pill',
                label:  'pay',
                }
        },
        order_values: function () {
            var self = this;
            var form = $('#payment_method').find('form');
            var checked_radio = form.find('input[type="radio"]:checked');
            if (checked_radio.length !== 1) {
                return;
            }
            checked_radio = checked_radio[0];
            var provider = checked_radio.dataset.provider
            if(provider === 'paypal_express'){
                var $tx_url = form.find('input[name="prepare_tx_url"]');
                if ($tx_url.length === 1) {
                    var values = {
                        acquirer_id: parseInt($(checked_radio).data('acquirer-id')),
                        save_token: $('input[name="o_payment_form_save_token"]').checked === true,
                        access_token: form.data('access-token'),
                        success_url: form.data('success-url'),
                        error_url: form.data('error-url'),
                        callback_method: form.data('callback-method'),
                        order_id: form.data('order-id'),
                    }
                    return self._rpc({
                        route: $tx_url[0].value,
                        params: values,
                    }).then(function (result) {
                        var newForm = document.createElement('div');
                        newForm.innerHTML = result;

                        return {
                                amount : $(newForm).find('input[name="amount"]').val(),
                                reference : $(newForm).find('input[name="invoice_num"]').val(),
                                currency_code : $(newForm).find('input[name="currency"]').val(),
                                billing_first_name: $(newForm).find('input[name="billing_first_name"]').val(),
                                billing_last_name: $(newForm).find('input[name="billing_last_name"]').val(),
                                billing_phone: $(newForm).find('input[name="billing_phone"]').val(),
                                billing_email: $(newForm).find('input[name="billing_email"]').val(),
                                billing_address_l1: $(newForm).find('input[name="billing_address_l1"]').val(),
                                billing_area1: $(newForm).find('input[name="billing_area1"]').val(),
                                billing_area2: $(newForm).find('input[name="billing_area2"]').val(),
                                billing_zip_code: $(newForm).find('input[name="billing_zip_code"]').val(),
                                billing_country_code: $(newForm).find('input[name="billing_country_code"]').val(),
                                shipping_partner_name: $(newForm).find('input[name="shipping_partner_name"]').val(),
                                shipping_address_l1: $(newForm).find('input[name="shipping_address_l1"]').val(),
                                shipping_area1: $(newForm).find('input[name="shipping_area1"]').val(),
                                shipping_area2: $(newForm).find('input[name="shipping_area2"]').val(),
                                shipping_zip_code: $(newForm).find('input[name="shipping_zip_code"]').val(),
                                shipping_country_code: $(newForm).find('input[name="shipping_country_code"]').val(),
                        }
                    });
                }
            }
            return {}
        },
        checkout_override: function () {
            var self = this;
            var loader = $('#paypal_express_loader');
            paypal.Buttons({
                style: self.get_btn_style(),
                createOrder: function(data, actions) {
                    loader.show();
                    return self.order_values().then(function (values){
                        loader.hide();
                        return actions.order.create({
                            payer: get_payer_data(values),
                            purchase_units: [{
                                amount: {
                                    value: values.amount,
                                    currency_code: values.currency_code
                                },
                                reference_id: values.reference,
                                shipping: get_shipping_data(values),
                            }],
                        });
                    });
                },
                onApprove: function(data, actions) {
                    loader.show();
                    return actions.order.capture()
                    .then(function (details) {
                        self._rpc({
                            route: '/paypal/express/checkout/state',
                            params: details
                        }).then(function(result){
                            window.location.href = window.location.origin + result
                            loader.hide();
                        });
                    });
                },
                onCancel: function (data, actions) {
                    loader.show();
                    self._rpc({
                        route: '/paypal/express/checkout/cancel',
                        params: data
                    }).then(function(result){
                        window.location.href = window.location.origin + result
                        loader.hide();
                    });
                },
                onError: function (error) {
                    // This is not handle in this module because of two reasons:
                    // 1. error object details is not mention in paypal doc.
                    // 2. Page close and page unload trigger onError function of Smart Payment Button.
                    loader.hide();
                    return alert(error);
                }
            }).render('#paypal-button');
        },
    });

    PaymentForm.include({
        updateNewPaymentDisplayStatus: function () {
            this._super.apply(this, arguments);
            var checked_radio = this.$('input[type="radio"]:checked');
            if (checked_radio.length !== 1) {
                return;
            }
            checked_radio = checked_radio[0];
            var provider = checked_radio.dataset.provider
            if(provider == 'paypal_express'){
                $('#o_payment_form_pay').hide();
                $('#paypal-button').show();
            }
            else{
                $('#paypal-button').hide();
                $('#o_payment_form_pay').show();
            }
        },
    });

    return publicWidget.registry.PaypalCheckoutButton;
});
