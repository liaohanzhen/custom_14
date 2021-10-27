odoo.define('employee_checklists.kanbanrecordcolor', function(require) {
"use strict";
	
	var KanbanRecord = require('web.KanbanRecord');
	KanbanRecord.include({
		_getColorID: function(variable) {
			if (typeof(variable) === 'number' && (variable===11 || variable===12 || variable===13)) {
	            return variable;
	        }
			return this._super(variable);
		},
		
	});
});