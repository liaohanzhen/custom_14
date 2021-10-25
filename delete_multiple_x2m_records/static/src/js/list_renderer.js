odoo.define('delete_multiple_x2m_records.list_view_x2m_delete', function (require) {
"use strict";

require('web.EditableListRenderer');
var core = require('web.core');
var ListRenderer = require('web.ListRenderer');
var _t = core._t;

ListRenderer.include({
	events: _.extend({}, ListRenderer.prototype.events, {
        'click thead th.o_list_record_delete_header': '_onTrashIconClickHeader',
    }),
    _onTrashIconClickHeader: function (event) {
        event.stopPropagation();
        var self = this;
        var $selectedRows = this.$('tbody .o_list_record_selector input:checked').closest('tr');
        if ($selectedRows.length<=0){
        	alert("Please select atleast one record.");
        }
        else{
        	if (confirm(_t("Do you really want to remove these records?"))){
        		var ids = _.map($selectedRows, function (row) {
                    return $(row).data('id');
                });
        		_.each(ids, function (id) {
        			self.trigger_up('list_record_remove', {id: id});
        			});
        	}
        }
		
    },
	_getNumberOfCols: function () {
		var n = this._super();
        if (this.addTrashIcon && !this.hasSelectors) {
            n+=2; //Increment by two, because we are adding selector and trash icon in the header.
        }
        return n;
    },
    _renderRow: function (record, index) {
        var $row = this._super.apply(this, arguments);
        if (this.addTrashIcon && !this.hasSelectors) {
        	$row.prepend(this._renderSelector('td'));
        }
        return $row;
    },
    _renderFooter: function (isGrouped) {
    	var $footer = this._super(isGrouped);
    	if (this.addTrashIcon && !this.hasSelectors) {
    		$footer.find("tr").prepend($('<td>'));
    		$footer.find("tr").append($('<td>'));
    	}
    	return $footer;
    },
    _renderHeader: function (isGrouped) {
    	var $header = this._super(isGrouped);
    	if (this.addTrashIcon && !this.hasSelectors) {
    		$header.find("tr").prepend(this._renderSelector('th'));
    		
    		var $icon = $('<span>', {class: 'fa fa-trash-o', name: 'delete'});
            var $td = $('<th>', {class: 'o_list_record_delete_header'}).append($icon);
            $header.find("tr").append($td);
    	}
    	return $header;
    },
    
}); 

});
