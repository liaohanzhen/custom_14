odoo.define('delete_multiple_x2m_records.list_view_x2m_delete', function (require) {
	"use strict";
	
	var ListView        = require('web.ListView');
	var core = require('web.core');
	var _t = core._t;
	core.form_widget_registry.get('one2many').include({
		multi_selection: true
	});
	core.form_widget_registry.get('one2many_list').include({
		multi_selection: true
	});
	core.form_widget_registry.get('many2many').include({
		multi_selection: true
	});
	ListView.include({
		load_list: function() {
			var res = this._super();
			if (this.$('thead .o_list_record_delete span').length>0){
				var self = this;
				this.$('thead .o_list_record_delete span').click(function() {
					var selection = self.groups.get_selection();
		            var row_ids = selection.ids;
		            if (row_ids.length===0){
		            	alert("Please select atleast one record.");
		            }
		            else{
		            	if (self.x2m!==undefined && self.x2m.field!==undefined && self.x2m.field.type==='one2many'){
		            		if (confirm(_t("Do you really want to remove these records?"))){
		            			self.do_delete(row_ids);
		            		}
		            	}
		            	else{
		            		self.do_delete(row_ids);
		            	}
		            }
		        });
			}
			return res;
		}
		
	});
});
