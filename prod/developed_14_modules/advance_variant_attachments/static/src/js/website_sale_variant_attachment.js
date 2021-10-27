odoo.define('advance_variant_attachments.website_sale', function(require) {
'use strict';

require('web.dom_ready');


if(!$('.oe_website_sale').length) {
    return $.Deferred().reject("DOM doesn't contain '.oe_website_sale'");
}

$('.oe_website_sale').each(function() {
    var oe_website_sale = this;
    
    $(oe_website_sale).on('change', 'ul[data-attribute_value_ids]', function(event) {
    	var $ul = $(event.target).closest('.js_add_cart_variants');
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
        
        if (product_id) {
        	$(".wk_panel li").each(function(e){
                var id = this.id;
                
                /*if ($(this).parent().attr('style').includes("display: none;")){
                	continue
                }*/
                
                var variant_id = this.getAttribute('variant_id')
                if (!variant_id || variant_id == product_id){
                	$(this).css('display', 'block');
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
        	
        }
    });
});

});