/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

odoo.define('wk_paypal_express_custom.express_checkout_custom', function (require) {
    "use strict";
    var ajax = require('web.ajax');
    var page_url = window.location.href

    var PaymentPaypalExpress = require('payment_paypal_express.express_checkout');
    var type;
    if (page_url.indexOf("/shop/cart") > -1){
        type = "cart"
    }
    else if (page_url.indexOf("/shop/") > -1){
        type = "product"
    }

    PaymentPaypalExpress.include({
        get_btn_style: function(){
            if (type=="cart" || type=="product"){
                var b_style = {
                    color:   'gold',
                    shape:   'rect',
                    label:   'checkout',
                    size: 'small',
                    height: 34,
                    tagline: false,
                }
                if (type=="cart"){
                    $("#paypal-button").addClass("cart_paypal_button")
                }
                else if (type == "product"){
                        b_style["height"] = 40;
                        b_style["size"] = 'small';
                        $("#paypal-button").addClass("pro_paypal_button")
                }
                console.log("b_style"+JSON.stringify(b_style))
                return b_style

            }else{
                return this._super.apply(this, arguments);
            }
        },
        get_transaction: function(){
          var self = this;
          return self._rpc({
                  route: '/get/paypal/acquirer/details',
                  }).then(function (result) {
                      var acquirer_id = result.acquirer_id
                      var values = {
                                  'acquirer_id': parseInt(acquirer_id),
                                  'public_paypal_checkout':true,
                                }
                      return self._rpc({
                              route: '/shop/payment/transaction/',
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
                                  })
                      })
        },
        create_order: function(){
            var self = this;
            var product_id = parseInt($('#paypal-button').closest('.js_product').find('input[name="product_id"]').val());
            var add_qty = parseInt($('#paypal-button').closest('.js_product').find('input[name="add_qty"]').val());
            var csrf_token = parseInt($('#paypal-button').closest('.js_product').find('input[name="csrf_token"]').val());
            var values = {
                'product_id': product_id,
                'add_qty':  add_qty,
                'csrf_token':csrf_token,
                        }
            return self._rpc({
                    route: '/get/product/order/details',
                    params: values,
                    }).then(function (result) {
                        return result
                        })
        },

        order_values: function () {
            var self = this;
            var page_url = window.location.href
            if (page_url.indexOf("/shop/payment") > -1){
                return this._super.apply(this, arguments);
            }
            if(type=="product"){

                return self.create_order().then(function(result){
                  return self.get_transaction()
                })
            }else{
              return self.get_transaction()
            }
        },
    });

});
