odoo.define('syscoon_website_sale_pricelist_selection.signup', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var utils = require('web.utils');

publicWidget.registry.SignUpForm.include({
	_onSubmit: function () {
		var cookie = utils.get_cookie('selected_pricelist');
		if (cookie){
			utils.set_cookie('selected_pricelist', "", -1); // remove cookie
		}
		this._super.apply(this, arguments);
	}
})
});