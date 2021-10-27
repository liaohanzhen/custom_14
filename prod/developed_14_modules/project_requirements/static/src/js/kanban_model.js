odoo.define('project_requirements.KanbanModel', function (require) {
"use strict";

var KanbanModel = require('web.KanbanModel');
var rpc = require('web.rpc');
var web_client = require('web.web_client');

KanbanModel.include({
	moveRecord: function (recordID, groupID, parentID) {
		var res = this._super(recordID, groupID, parentID)
		var parent = this.localData[parentID];
		var groupedFieldName = parent.groupedBy[0];
		var new_group = this.localData[groupID];
		var record = this.localData[recordID];
		this.alive(res).then(function (column_db_ids) {
			if (parent.model=='crm.lead' && groupedFieldName=='stage_id'){
				rpc.query({
	                model: 'crm.stage',
	                method: 'get_create_project',
	                args: [new_group.res_id],
	            })
	            .then(function (res) {
	            	if (res){
	            		return web_client.do_action({
	                        name: "Select Project Template",
	                        type: 'ir.actions.act_window',
	                        view_mode: 'form',
	                        views: [[false, 'form']],
	                        target: 'new',
	                        res_model: 'crm.project.wizard',
	                        context: {'lead_id':record.data.id},
	                    });
	            	}
	            })
			}
		})
		
		return res;
	}
	})

});