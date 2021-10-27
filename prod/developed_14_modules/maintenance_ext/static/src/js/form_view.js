odoo.define('maintenance_ext.FormView', function (require) {
    var FormView = require('web.FormView');
    
    FormView.include({
    	load_record: function(record) {
    		if (record && (this.model=='maintenance.equipment') && this.$el.find("iframe").length>0){
            	if (record.iframe_url != undefined && record.iframe_url != false ){
            		this.$el.find("iframe")[0].src = record.iframe_url;
            	}
            	else{
            		this.$el.find("iframe")[0].src = '';
            	}
            }
    		return this._super(record);
    	},
    });
});