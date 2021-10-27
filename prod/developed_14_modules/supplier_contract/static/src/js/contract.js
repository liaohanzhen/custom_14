odoo.define('marketplaces.custom.view', function (require) {
    "use strict";
    var FormView = require('web.FormView');
    FormView.include({
    	on_processed_onchange: function(result) {
    		try {
    			if (this.dataset.model==='res.partner.contract' && result.value!==undefined && result.value.payment_term_id_tmp!==undefined){
    	    		var parent_field = this.dataset.parent_view.fields.property_supplier_payment_term_id;
    	    		parent_field._inhibit_on_change_flag = true;
    	    		parent_field.set_value(result.value.payment_term_id_tmp);
    	    		parent_field._inhibit_on_change_flag = false;
    	    		parent_field._dirty_flag = true;
    	    	}
    		}
    		catch(e) {
    			return this._super(result);
    		}
    		return this._super(result);
    	},
    	
    });
});