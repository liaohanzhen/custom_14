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
            $(".wk_panel li").each(function(e){
                var id = this.id;
                if (id != idx) {
                    $(this).css('display', 'none');
                } else {
                    $(this).css('display', 'block');
                }
                if (idx == 'wk_all') {
                    $(this).css('display', 'block');
                }
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