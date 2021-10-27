odoo.define('employee.training.session', function (require) {
    var ListView = require('web.ListView');
        
    ListView.include({
    	load_list: function() {
    		//Show/Hide Signature button in Trainees list view based on Training Session states 
    		//debugger;
    		if (this.dataset.x2m !== undefined && this.dataset.x2m.name === 'trainee_ids' && this.dataset.x2m.field.relation==='hr.employee.trainee'){
            	var state = this.dataset.x2m.dataset.parent_view.datarecord.state;
            	if (state!=='SIGNATURE REQUIRED'){
            		_.each(this.columns, function(column) {if (column.id === "action_do_signature"){column.invisible="1";}});
            	}
            }
    		return this._super();
    	},
    	setup_columns: function (fields, grouped) {
    		//Show/Hide Signature button in Trainees list view based on Training Session states
    		var res = this._super(fields, grouped);
    		if (this.dataset.x2m !== undefined && this.dataset.x2m.name === 'trainee_ids' && this.dataset.x2m.field.relation==='hr.employee.trainee'){
    			var state = this.dataset.x2m.dataset.parent_view.datarecord.state;
    			var index = this.visible_columns.indexOf(_.filter(this.visible_columns, function (column) {return column.name === 'action_do_signature'})[0]);
    			if (index > -1 && state!=='SIGNATURE REQUIRED') {
    				this.visible_columns.splice(index, 1);
    				this.aggregate_columns = _(this.visible_columns).invoke('to_aggregate');
    			}
    		}
    		return res;
    	},
    });
    ListView.List.include({
    	render: function () {
    		if (this.dataset.x2m !== undefined && this.dataset.x2m.name === 'trainee_ids' && this.dataset.x2m.field.relation==='hr.employee.trainee'){
    			var state = this.dataset.x2m.dataset.parent_view.datarecord.state;
            	if (state!=='SIGNATURE REQUIRED'){
            		_.each(this.columns, function(column) {if (column.name === 'action_do_signature'){column.invisible="1"}});
            	}
            }
    		return this._super();
    	},
    	pad_table_to: function (count) {
    		if (this.dataset.x2m !== undefined && this.dataset.x2m.name === 'trainee_ids' && this.dataset.x2m.field.relation==='hr.employee.trainee'){
    			var state = this.dataset.x2m.dataset.parent_view.datarecord.state;
            	if (state!=='SIGNATURE REQUIRED'){
            		_.each(this.columns, function(column) {if (column.name === 'action_do_signature'){column.invisible="1"}});
            	}
            }
    		return this._super(count);
    	}
    });
});