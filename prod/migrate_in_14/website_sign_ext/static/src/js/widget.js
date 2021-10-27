odoo.define('website_sign_ext.widget', function (require) {
"use strict";

var relational_fields = require('web.relational_fields');
var AbstractField = require('web.AbstractField');
var registry = require('web.field_registry');

var FieldSelectionDynamic = relational_fields.FieldSelection.extend({
	template: 'FieldSelection',
    specialData: "_fetchSpecialRelation",
    supportedFieldTypes: ['selection', 'many2one'],
    events: _.extend({}, AbstractField.prototype.events, {
        'change': '_onChange',
    }),
	
    _setValues: function () {
        debugger;
        if (!this.attrs.sequence_number){
        	var count = this.getParent().state.count;
        	if (this.getParent().state.count){
        		this.attrs.sequence_number = count;
        	}
        	else{
        		this.attrs.sequence_number = 10;
        	}
        	
        }
        var seq = [];
        for(var i = 1 ; i <= this.attrs.sequence_number ; i++) {
        	seq.push([i.toString(),i.toString()])
        }
        this.values = [[false, this.attrs.placeholder || '']].concat(seq);
         
    },
});

registry.add('selection_dynamic', FieldSelectionDynamic)

});