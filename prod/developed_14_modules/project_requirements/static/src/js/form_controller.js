odoo.define('project_requirements.FormController', function (require) {
"use strict";

var FormController = require('web.FormController');
var relational_fields = require('web.relational_fields');
var rpc = require('web.rpc');
var web_client = require('web.web_client');
relational_fields.FieldStatus.include({
	
	_setValue: function (value, options) {
		var self = this;
		return this._super.apply(this, arguments).then(function () {
        /*this.alive(r).then(function () {*/
        	if (self.model=='crm.lead' && self.name=='stage_id'){
	        	var lead_id = self.record.data.id;
	        	rpc.query({
	                model: 'crm.stage',
	                method: 'get_create_project',
	                args: [value],
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
	                        context: {'lead_id':lead_id},
	                    });
	            	}
	            })
	        }
        });
	},
	/*_onClickStage: function (e) {
		var self = this;
		var r= this._super(e)
        
        this.alive(r).then(function (column_db_ids) {
	    	if (self.model=='crm.lead' && self.name=='stage_id'){
	        	var value = $(e.currentTarget).data("value")
	        	var lead_id = self.record.data.id;
	        	rpc.query({
	                model: 'crm.stage',
	                method: 'get_create_project',
	                args: [value],
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
	                        context: {'lead_id':lead_id},
	                    });
	            	}
	            })
	        }
        });
    },*/
});


FormController.include({
	saveRecord: function () {
		var self = this;
		var data = self.renderer.state.data;
		return this._super.apply(this, arguments).then(function (changedFields) {
			if (changedFields.length && self.renderer.state.model==='crm.lead' && changedFields.indexOf('stage_id')> -1){
				rpc.query({
	                model: 'crm.stage',
	                method: 'get_create_project',
	                args: [data.stage_id.res_id],
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
	                        context: {'lead_id':self.renderer.state.data.id},
	                    });
	            	}
	            })
	            
				/*return this.do_action({
	                name: "Select Project Template",
	                type: 'ir.actions.act_window',
	                view_mode: 'form',
	                views: [[false, 'form']],
	                target: 'new',
	                res_model: 'crm.project.wizard',
	                context: {'lead_id':self.renderer.state.data.id},
	                	
	            });*/
	        }
			return changedFields;
		});
	}
})
});