/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : https://store.webkul.com/license.html/ */

odoo.define('marketplace_vendor_signup.multi_vendor_signup', function (require) {
    "use strict";
    
    var core = require('web.core');
    var _t = core._t;
    var ajax = require('web.ajax');

    $(document).ready(function(){

        var current_group, next_group, previous_group; //groups
        var opacity;

        function getState(){
            var selectStates = $("select[name='state_id']");
            if ($("select[name='country_id']").length){
                selectStates.find("option:gt(0)").remove();
            }
            if ($("select[name='country_id']").val()) {
                ajax.jsonRpc("/marketplace_vendor_signup/country_info/" + $("select[name='country_id']").val(), 'call', {}).then(
                function(data) {
                    if (data.states.length) {
                        selectStates.html('');
                        _.each(data.states, function(x) {
                            var opt = $('<option>').text(x[1])
                                .attr('value', x[0]);
                            selectStates.append(opt);
                        });
                        selectStates.parent('div').show();
                    }
                    else {
                        selectStates.val('').parent('div').hide();
                        selectStates.removeAttr("required");
                    }
                }
                );
            }
        }

        function validateForm(current_fieldset) {
            var field_obj, valid = true;
            if ($("#password_match_error")){
            $("#password_match_error").remove()
            }

            field_obj = $(current_fieldset).find(".wk_attr_input")
            field_obj.each(function() {
                
                if ($(this).attr("required") && $(this).val()){
                    $(this).removeClass("wk_warning");
                }
                if ($(this).attr("required") && !$(this).val()){
                    $(this).addClass("wk_warning");
                    valid = false;
                }
                if($(this).attr("id") == "login" && $("#seller_email_error").is(":visible")){
                    valid = false;
                }
                if($(this).attr("required") && $(this).attr("type") == 'checkbox' && !$(this).is( ":checked" )){
                    $(this).parent().addClass("wk_boolean_warning");
                    valid = false;
                }
                if($(this).attr("id")=="profile_url" && $("#profile_url_error").is(":visible")){
                    valid = false;
                }
                if($(this).attr("id")=="confirm_password"){
                    var password = $("#wk_mp").find("#password").val()
                    var confirm_password = $("#wk_mp").find("#confirm_password").val()
                    if (password != confirm_password){
                        $(this).closest('.field-confirm_password').append('</span><div class="text-danger" id="password_match_error" style="display:none;"></div>')
                        $("#password_match_error").html("Passwords do not match.").show()
                        valid = false;
                    }
                }
                if($(this).attr("id")=="country_id"){
                    getState()
                }
            });
            return valid; // return the valid status
          }

        $(".mp_next").click(function(){
            var current_fieldset = $(this).parent()
            current_group = $(this).parent();
            next_group = $(this).parent().next();
            if (!validateForm(current_fieldset)) return false;

            //Add Class Active
            $("#group_progress li").eq($("fieldset").index(next_group)).addClass("active");
            next_group.show();
            current_group.animate({opacity: 0}, {
            step: function(now) {
            opacity = 1 - now;
            
            current_group.css({
            'display': 'none',
            'position': 'relative'
            });
            next_group.css({'opacity': opacity});
            },
            });
            });

        $(".mp_previous").click(function(){
            current_group = $(this).parent();
            previous_group = $(this).parent().prev();
            $("#group_progress li").eq($("fieldset").index(current_group)).removeClass("active");
            
            previous_group.show();
            
            current_group.animate({opacity: 0}, {
            step: function(now) {
            opacity = 1 - now;
            
            current_group.css({
            'display': 'none',
            'position': 'relative'
            });
            previous_group.css({'opacity': opacity});
            },
            });
            });

        $(".submit").click(function(){
            return false;
            })

        $(".wk_attr_input").keypress(function(){
            $(this).removeClass("wk_warning");
        });
        $(".wk_attr_input").change(function(){
            if($(this).prop('tagName') == 'SELECT' && $(".wk_attr_input option:selected").val() != "" ){
                $(this).removeClass("wk_warning");
            }
            else if($(this).attr("type") == 'checkbox' && $(this).is( ":checked" )){
                $(this).parent().removeClass("wk_boolean_warning");
            }
            else if($(this).attr("id")=="confirm_password"){
                var password = $("#wk_mp").find("#password").val()
                var confirm_password = $("#wk_mp").find("#confirm_password").val()
                if (password == confirm_password){
                    $("#password_match_error").remove()
                }
            }
        });

        if($(".wk_attr_input").attr("id") == 'login'){
            $("#login").closest('.field-login').append('<span class="fa form-control-feedback pull-right" style="margin-top:-24px;margin-right: 10px;"></span><div class="text-danger" id="seller_email_error" style="display:none;"></div>')
        }

        function validate_seller_email($email){

            var seller_email = String($email.val());
            var $form = $email.closest('.oe_signup_form');
            var $email_div = $email.closest('.field-login');
            var $email_span = $email_div.find('.form-control-feedback');
            var $button = $form.find(".mp_next");
            
            if($('#login').hasClass('invalide_url')){
                $('#login').removeClass('invalide_url');
            }
            if($email_span.hasClass('fa-pencil')){
                $email_span.removeClass('fa-pencil');
            }
            if($email_span.hasClass('fa-times')){
                $email_span.removeClass('fa-times');
            }
            if($email_span.hasClass('fa-check')){
                $email_span.removeClass('fa-check');
            }

            $email_span.addClass('fa-spinner fa-pulse');
            ajax.jsonRpc("/profile/seller/email/vaidation", 'call', {'email': seller_email})
            .then(function (vals)
            {   
                $button.removeClass("disabled");
                if(vals && seller_email != ''){
                    if($email_div.hasClass('has-error')){
                        $email_div.removeClass('has-error');
                    }
                    if($email_span.hasClass('fa-pencil')){
                        $email_span.removeClass('fa-pencil');
                    }
                    if($email_span.hasClass('fa-times')){
                        $email_span.removeClass('fa-times');
                    }
                    if($email_span.hasClass('fa-spinner fa-pulse')){
                        $email_span.removeClass('fa-spinner fa-pulse');
                    }
                    if($('#login').hasClass('invalide_url')){
                        $('#login').removeClass('invalide_url');
                    }
                    $email_div.addClass('has-success');
                    $email_span.addClass('fa-check');
                    $('#seller_email_error').hide();
                }
                else{
                    if($email_div.hasClass('has-success')){
                        $email_div.removeClass('has-success');
                    }
                    if($email_span.hasClass('fa-pencil')){
                        $email_span.removeClass('fa-pencil');
                    }
                    if($email_span.hasClass('fa-check')){
                        $email_span.removeClass('fa-check');
                    }
                    if($email_span.hasClass('fa-spinner fa-pulse')){
                        $email_span.removeClass('fa-spinner fa-pulse');
                    }
                    $email_div.addClass('has-error');
                    $email_span.addClass('fa-times');
                    if(seller_email != ''){
                        $('#seller_email_error').html('Another user is already registered using this email address.');
                        $button.addClass("disabled")
                    }
                    else{
                        $('#seller_email_error').html('Please Enter Your Email.');
                    }
                    $('#login').addClass('invalide_url');
                    $('#seller_email_error').show();
                }
            });
        }
        $(document).on("change",".mp_form #mp_terms_conditions", function()
		{
            validate_seller_email($('#login'));
        });
        $(document).on("input",".mp_form #login", function()
		{
            validate_seller_email($(this));
        });

    });
});  