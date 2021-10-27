odoo.define('supplier_approval.widget', function (require) {
    "use strict";
    
    var core = require('web.core');
    var field_registry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var _t = core._t;
    var QWeb = core.qweb;
    
	var FieldApprovalButton = AbstractField.extend({
	    className: 'o_stat_info',
	    supportedFieldTypes: ['boolean'],

	    //--------------------------------------------------------------------------
	    // Public
	    //--------------------------------------------------------------------------

	    /**
	     * A boolean field is always set since false is a valid value.
	     *
	     * @override
	     */
	    isSet: function () {
	        return true;
	    },

		_render: function() {
	        this._super.apply(this, arguments);
	        this.$el.empty();
	        var text, hover;
	        
	        switch (this.nodeOptions.terminology) {
	            case "approved":
	            	text = this.value ? _t("Approved") : _t("Inactive");
	                hover = this.value ? _t("Deactivate") : _t("Activate");
	                break;
	            case "not approved":
	            	text = this.value ? _t("Approved") : _t("Not Approved");
	                hover = this.value ? _t("Not Approve") : _t("Approve");
	                break;
	            default:
	            	var opt_terms = this.nodeOptions.terminology || {};
	                if (typeof opt_terms === 'string') {
	                    opt_terms = {}; //unsupported terminology
	                }
	                text = this.value ? _t(opt_terms.string_true) || _t("On")
	                                  : _t(opt_terms.string_false) || _t("Off");
	                hover = this.value ? _t(opt_terms.hover_true) || _t("Switch Off")
	                                   : _t(opt_terms.hover_false) || _t("Switch On");
	        }
	        var val_color = this.value ? 'text-success' : 'text-danger';
	        var hover_color = this.value ? 'text-danger' : 'text-success';
	        var $val = $('<span>').addClass('o_stat_text o_not_hover ' + val_color).text(text);
	        var $hover = $('<span>').addClass('o_stat_text o_hover ' + hover_color).text(hover);
	        this.$el.append($val).append($hover);
	        
	    },
	});
	//core.form_widget_registry.add("toggle_approval", FieldApprovalButton);

field_registry.add('toggle_approval', FieldApprovalButton);
});