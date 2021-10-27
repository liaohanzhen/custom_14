odoo.define('maintenance_ext.FormRenderer', function (require) {
'use strict';

var FormRenderer = require('web.FormRenderer');
var rpc = require('web.rpc');

FormRenderer.include({
	_renderView: function () {
		var res = this._super.apply(this, arguments);
		var self = this;
		if (self.state.model=='maintenance.equipment' && this.$el.find("iframe").length>0){
        	if (self.state.data.iframe_url != undefined && self.state.data.iframe_url != false ){
        		this.$el.find("iframe")[0].src = self.state.data.iframe_url;
        	}
        	/*else if(self.state.getContext() != undefined && self.state.getContext().default_iframe_url){
        		this.$el.find("iframe")[0].src = self.state.getContext().default_iframe_url
        	}*/
        	else{
        		//this.$el.find("iframe[src='src_iframe_custom']")[0].src = '';
        		this.$el.find("iframe")[0].src = '';
        	}
        }
		return res;
	},
})

});