odoo.define('portal_documents.portal_user_documents', function (require) {
    "use strict";
    require('web.dom_ready');
    
    var ajax = require('web.ajax');
    $(document).ready(function() {
        /*$('#sheliya_all').find('.sheliya_panel').show();
        $('#sheliya_all').find('.btn_accordion').css({"color":"#2275df"});
        $('.sheliya_btn_accordion').click(function() {
            $(this).find('.btn_accordion').css({"color":"#2275df"});
            $(this).siblings().find('.btn_accordion').css({"color":"inherit"});
            $(this).find('.sheliya_panel').show();
            $(this).siblings().find('.sheliya_panel').hide();
        });
        $('.sheliya_btn_accordion').on('click', function(e) {
            var idx = $(this).attr('id');
            $(".sheliya_panel li").each(function(e){
                var id = this.id;
                if (id != idx) {
                    $(this).css('display', 'none');
                } else {
                    $(this).css('display', 'block');
                }
                if (idx == 'sheliya_all') {
                    $(this).css('display', 'block');
                }
            });
        });*/
        $('.portal_attachment_id').on('click', function(e) {
            var attachment_id = $(this).parent().find('.portal_attachment_id_hidden').val();
            ajax.jsonRpc("/download/portal/attachment", 'call', {'attachment_id':attachment_id})
                .then(function (data) {
                    setTimeout('location.reload()', 200);
                }).fail(function (error){
                });
        });
    });
})