/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

odoo.define('website_quote_system.customer_quote', function(require) {
"use strict";
var ajax = require('web.ajax');

$(document).ready(function() {
    $(".oe_website_sale a[href='/shop/checkout']").on('click', function(ev) {
        // validating cart for quote orders...
        ev.preventDefault();
        ajax.jsonRpc("/quote/order/validate", "call", {}).then(function(data) {
            if (data == false) {
                alert("Warning!!! Seems some quote items are not approved, Please remove it and try adding again...");
                ev.preventDefault();
            } else {
                window.location = "/shop/checkout";
            }
        })
    });

    $('tr.quote_req_row').click(function() {
        var href = $(this).find("a").attr("href");
        if (href) {
            window.location = href;
      }
    });

     $('#quote_request_button').on('click',function (event) {
         console.log("hello ")
        var $form = $(this).closest('form');
        var product_id = parseInt($form.find('input[type="hidden"][name="product_id"]').first().val());
        var def_qty = parseFloat($form.find('input[type="hidden"][name="def_qty"]').first().val());
        var def_price = parseFloat($form.find('input[type="hidden"][name="def_price"]').first().val());
        event.preventDefault();
        $('.quote_loader').show();
        ajax.jsonRpc("/shop/customer_quote", 'call', {
            'product_id': product_id,
        }
        ).then(function (customer_quote_template) {
            var $modal = $(customer_quote_template);
            $('.quote_loader').hide();
            $modal.appendTo('#wrap')
            .modal('show')
            .on('hidden.bs.modal', function () {
                $(this).remove();
            });

            $('#new_quantity').addClass("valid");
            $('#new_price').addClass("valid");

            $('#new_quantity').on('input', function() {
                var input=$(this);
                var new_qty=input.val();
                if(!new_qty){
                    input.removeClass("valid").addClass("invalid");
                    document.getElementById("qty_error").textContent="*This field is required.";
                    $('.invalid').css('border','2px solid #ad4442');
                }
                else if(!$.isNumeric(new_qty)){
                    input.removeClass("valid").addClass("invalid");
                    document.getElementById("qty_error").textContent="*Quantity must be in numbers.";
                    $('.invalid').css('border','2px solid #ad4442');
                }
                else if(new_qty < def_qty){
                    input.removeClass("valid").addClass("invalid");
                    document.getElementById("qty_error").textContent="*Quantity must be more than minimum quantity.";
                    $('.invalid').css('border','2px solid #ad4442');
                }
                else if(new_qty < 1){
                    input.removeClass("valid").addClass("invalid");
                    document.getElementById("qty_error").textContent="*Quantity must be more than minimum quantity.";
                    $('.invalid').css('border','2px solid #ad4442');
                }
                else{
                    input.removeClass("invalid").addClass("valid");
                    document.getElementById("qty_error").textContent="";
                    $('.valid').css('border','2px solid #3c753d');

                }
            });
            $('#new_price').on('input', function() {
                var input=$(this);
                var new_price=input.val();
                if(!new_price){
                    input.removeClass("valid").addClass("invalid");
                    document.getElementById("price_error").textContent="*This field is required.";
                    $('.invalid').css('border','2px solid #ad4442');
                }
                else if(!$.isNumeric(new_price)){
                    input.removeClass("valid").addClass("invalid");
                    document.getElementById("price_error").textContent="*Price must be in numbers.";
                    $('.invalid').css('border','2px solid #ad4442');
                }
                else if(new_price < 0){
                    input.removeClass("valid").addClass("invalid");
                    document.getElementById("price_error").textContent="*Price cannot be in negative.";
                    $('.invalid').css('border','2px solid #ad4442');
                }
                else if(new_price == 0){
                    input.removeClass("valid").addClass("invalid");
                    document.getElementById("price_error").textContent="*Price cannot be in zero.";
                    $('.invalid').css('border','2px solid #ad4442');
                }
                else{
                    input.removeClass("invalid").addClass("valid");
                    document.getElementById("price_error").textContent="";
                    $('.valid').css('border','2px solid #3c753d');
                }
            });
            // SUBMIT QUOTE BUTTON
            $('#quote_submit_button').on('click', function(event) {
                var $form = $(this).closest('form')
                var product_id = parseInt($form.find('input[type="hidden"][name="product_id"]').first().val());
                var new_quantity = parseFloat($form.find('input[name="new_quantity"]').val());
                var new_price = parseFloat($form.find('input[name="new_price"]').val())
                // or parseFloat($form.find('input[type="hidden"][name="def_price"]').first().val());
                var new_desc = document.getElementById("new_desc").value

                var form_data=$("#create_customer_quote").serializeArray();
                var error_free_qty=true;
                var error_free_price=true;
                for (var input in form_data) {
                    // var element=$("#"+form_data[input]['name']);
                    // CHECK QUANTITY
                    var qty_element=$("#new_quantity");
                    var qty_valid=qty_element.hasClass("valid");

                    var error_qty_element=$("#qty_error");
                    if (!qty_valid){
                        error_qty_element.removeClass("qty_error").addClass("qty_error_show"); error_free_qty=false;
                    }
                    else{
                        error_qty_element.removeClass("qty_error_show").addClass("qty_error");
                    }
                    // CHECK PRICE
                    var price_element = $("#new_price");
                    var price_valid = price_element.hasClass("valid");
                    var error_price_element = $("#price_error");
                    if (!price_valid){
                        error_price_element.removeClass("price_error").addClass("price_error_show"); error_free_price=false;
                    }
                    else{
                        error_price_element.removeClass("price_error_show").addClass("price_error");
                    }
                }
                if (!error_free_qty || !error_free_price) {
                    event.preventDefault();
                } else {
                    event.preventDefault();
                    $modal.modal('toggle');
                    $('#new_quantity').addClass("invalid");
                    $('#new_price').addClass("invalid");
                    $('.quote_loader').show();
                    ajax.jsonRpc("/shop/customer_quote_submit", 'call',{
                        'product_id' :   product_id,
                        'qty'        :   new_quantity,
                        'price'      :   new_price,
                        'description':   new_desc,
                    })
                    .then(function (customer_quote_template_submit) {
                        $('.quote_loader').hide();
                            var $modal1 = $(customer_quote_template_submit);
                            $modal1.appendTo('#wrap')
                            $modal1.modal('show')
                            .on('hidden.bs.modal', function () {
                                $(this).remove();
                            });
                        });
                    }
                });
            });
        });
    });
});
