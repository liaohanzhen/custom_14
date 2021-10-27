odoo.define('frogblue_webshop.package_qty', function (require) {
"use strict";

var publicWidget = require('web.public.widget');
var session = require('web.session');
var rpc = require('web.rpc');


publicWidget.registry.WebsiteSale.include({
    change_total_price: function(price){
	    var qty = parseInt($("input[name=add_qty]").val());
	    price = (price * qty).toFixed(2)
	    rpc.query({
            route: '/change/currency-format',
            params: {
                price: price,
            },
        }).then(function (res) {
            $("b#total_cost span.oe_currency_value").eq(1).text(res)
        })
	},
    _onClickAddCartJSON: function (ev){
		ev.preventDefault();
		var $link = $(ev.currentTarget);
	    var $input = $link.closest('.input-group').find("input");
	    var increment_qty = parseFloat($input.data('packageQty'))
	    var min = parseFloat($input.data("min") || 0);
	    var max = parseFloat($input.data("max") || Infinity);
	    var previousQty = parseFloat($input.val() || 0, 10);
	    var quantity = ($link.has(".fa-minus").length ? - increment_qty : increment_qty) + previousQty;
	    var newQty = quantity > min ? (quantity < max ? quantity : max) : min;
	    if (newQty !== previousQty) {
	        $input.data("onclickaddcart",true);
			$input.val(newQty).trigger('change');
	    }
	    return false;
	},
	_onChangeCombination: function (ev, $parent, combination){
        //	/sale/get_combination_info
		this._super(ev, $parent, combination);
        var self = this;
        self.change_total_price(combination.price)
		if (combination.variant_package_qty !== undefined){
			var $add_qty = $parent.find('input[name="add_qty"]');
			if ($add_qty.data("onclickaddcart")){
				$add_qty.data("onclickaddcart",false);
			}
			else {
				$add_qty.data("package-qty",combination.variant_package_qty);
				$add_qty.data("min",combination.variant_package_qty);
				$add_qty.val(combination.variant_package_qty);
			}
		}
	},
});

});
