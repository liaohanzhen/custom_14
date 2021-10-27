odoo.define('website_sale_portal.ProductConfiguratorMixin5B', function (require) {
'use strict';

var ProductConfiguratorMixin = require('sale.ProductConfiguratorMixin');
var sAnimations = require('website.content.snippets.animation');

sAnimations.registry.WebsiteSale.include({
    /**
     * Adds the stock checking to the regular _onChangeCombination method
     * @override
     */
    _onChangeCombination: function (ev, $parent, combination){
        this._super.apply(this, arguments);
        var $default_code = $parent.parent().parent().find('#product_default_code')
        $default_code.html(combination.default_code);
    }
});

/*ProductConfiguratorMixin.include({
	_onChangeCombination: function (ev, $parent, combination){
		debugger;
		this._super.apply(this, arguments);
		var $default_code = $parent.parent().parent().find('#product_default_code')
		$default_code.html(combination.default_code);
	}
})*/

});
