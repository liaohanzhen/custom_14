$(document).ready(function(){
    var shop_index = window.location.href.indexOf("/shop");
    var is_deutsch_lan = false;
    
//    if($('.js_language_selector > button > span').length > 0 && $('.js_change_lang').length > 0){
//    	var current_lang = $('.js_language_selector > button > span').text();
//    	_.each($('.js_change_lang'),function(e){
//    		var js_change = $(e).find('span').text();
//    		if(js_change == current_lang){
//    			if($(e).data('url_code') == 'de'){
//    				is_deutsch_lan = true;
//    			}
//    		}
//    	});
//    }
    
    if($('html').length > 0){
    	var CurrLanguage = $($('html')[0]).attr('lang');
    	if(CurrLanguage == 'de-DE'){
    		is_deutsch_lan = true;
    	}
    }
    
    if (is_deutsch_lan) {
    	if($('main').length > 0){
    		var oe_website_sale = $('main')[0];
    		if(oe_website_sale && oe_website_sale.firstElementChild){
            	var frogblue_de_snippet = '<div class="website_frogblue_de_snippet banner-wrap"><div class="banner-wrap-inner"><header class="banner-header"><h1 class="logo-text"><b>frog</b>Versand</h1></header><section class="banner-content"><div class="banner-logo"><img src="/website_frogblue_de_snippet/static/src/images/logo.png" alt="logo" width="310"/></div><h2 class="banner-title">HEUTE BESTELLT MORGEN GELIEFERT</h2><div class="fron-blue"><img src="/website_frogblue_de_snippet/static/src/images/frog-blue.png" alt="frogblue"width="290"></div><p> Bestellen Sie bis 14.00 Uhr und Sie erhalten die Ware bereits am nächsten Tag</p></section></div></div>';    
            	$('main #wrap').addClass("hasAdBanner");
            	$(oe_website_sale.firstElementChild).before(frogblue_de_snippet);
    		}
    	}
    }
});