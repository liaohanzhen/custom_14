odoo.define('slack_odoo_connector.DocumentThread', function (require) {
"use strict";


var DocumentThread = require('mail.model.DocumentThread');

DocumentThread.include({
	_postMessage: function (data) {
		data.context.is_message_from_js = true;
		return this._super(data);
	},
});



});