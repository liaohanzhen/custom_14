odoo.define('employee_training.FormView', function (require) {
    var FormView = require('web.FormView');
    
    FormView.include({
    	load_record: function(record) {
    		if (record && (this.model=='training.template' || this.model=='wiki.web.page.wizard') && this.$el.find("iframe").length>0){
            	if (record.iframe_url != undefined && record.iframe_url != false ){
            		this.$el.find("iframe")[0].src = record.iframe_url;
            	}
            	else if(this.dataset != undefined && this.dataset.context!= undefined && this.dataset.context.default_iframe_url){
            		this.$el.find("iframe")[0].src = this.dataset.context.default_iframe_url
            	}
            	else{
            		//this.$el.find("iframe[src='src_iframe_custom']")[0].src = '';
            		this.$el.find("iframe")[0].src = '';
            	}
            }
    		return this._super(record);
    	},
    });
});