/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
odoo.define('advance_product_attachments.wk_attachment', function (require) {
    "use strict";
    var ajax = require('web.ajax');
    $(document).ready(function() {
        $('#wk_all').find('.wk_panel').show();
        $('#wk_all').find('.btn_accordion').css({"color":"#2275df"});
        $('.wk_btn_accordion').click(function() {
            $(this).find('.btn_accordion').css({"color":"#2275df"});
            $(this).siblings().find('.btn_accordion').css({"color":"inherit"});
            $(this).find('.wk_panel').show();
            $(this).siblings().find('.wk_panel').hide();
        });
        $('.wk_btn_accordion').on('click', function(e) {
            var idx = $(this).attr('id');
            
            var $ul = $('ul.js_add_cart_variants') ;$(event.target).closest('ul.js_add_cart_variants');
            var $parent = $ul.closest('.js_product');
            var variant_ids = $ul.data("attribute_value_ids");
            if(_.isString(variant_ids)) {
                variant_ids = JSON.parse(variant_ids.replace(/'/g, '"'));
            }
            
            var values = [];
            $parent.find('input.js_variant_change:checked, select.js_variant_change').each(function() {
                values.push(+$(this).val());
            });
            var product_id = false;
            for (var k in variant_ids) {
                if (_.isEmpty(_.difference(variant_ids[k][1], values))) {
                	product_id = variant_ids[k][0];
                	break;
                }
            }
            
            $(".wk_panel li").each(function(e){
                var id = this.id;
                var variant_id = this.getAttribute('variant_id')
                if (!variant_id || variant_id == product_id){
                	if (id == idx || idx == 'wk_all') {
                		$(this).css('display', 'block');
                    } else {
                    	$(this).css('display', 'none');
                    }
                }
                else {
                	$(this).css('display', 'none');
                }
                /*if (id != idx) {
                    $(this).css('display', 'none');
                } else {
                    $(this).css('display', 'block');
                }
                if (idx == 'wk_all') {
                    $(this).css('display', 'block');
                }*/
            });
            
        });
        $('.attachment_id').on('click', function(e) {
            var pro_attachment_id = $(this).parent().find('.pro_attachment_id').val();
            ajax.jsonRpc("/download/attachment", 'call', {'pro_attachment_id':pro_attachment_id})
                .then(function (data) {
                    setTimeout('location.reload()', 200);
                }).fail(function (error){
                });
        });
    });
})