odoo.define('web.ListRendererAureliehocquelCRM', function (require) {
'use strict';

var session = require('web.session');
var rpc = require('web.rpc');
var ListRenderer = require('web.ListRenderer');
var utils = require('web.utils');
var translation = require('web.translation');
var _t = translation._t;

ListRenderer.include({
	human_number_custom: function (number, decimals, minDigits, formatterCallback) {
		number = Math.round(number);
		decimals = decimals | 0;
        minDigits = minDigits || 1;
        formatterCallback = formatterCallback || utils.insert_thousand_seps;
        var symbol = '';
		var d2 = Math.pow(10, decimals);
        var val = _t('kMGTPE');
        var symbol = '';
        for (var i = val.length - 1 ; i > 0 ; i--) {
            var s = Math.pow(10, i * 3);
            if (s <= number / Math.pow(10, minDigits - 1)) {
                number = Math.round(number * d2 / s) / d2;
                symbol = val[i - 1];
                break;
            }
        }
        return formatterCallback('' + number) +' '+ symbol;
    },
	_renderView: function () {
		var res = this._super.apply(this, arguments);
		var self = this;
		if (this.state.model=='crm.lead'){
			rpc.query({
                model: 'crm.lead',
                method: 'get_js_data_for_total_count',
                args: [],
            })
            .then(function (data) {
            	var total_planned_revenue = '$ '+self.human_number_custom(data['total_planned_revenue'],0,1); 
            	var total_project_power = self.human_number_custom(data['total_project_power'],0,1) +'W';
            	var total_deals = data['total_leads'];
    	        
    	        $('#crm_pipeline_total').remove()
    	        $('div.o_cp_buttons').after("<div id='crm_pipeline_total' style='padding-left: 20%;font-size: 16px;font-weight: 500;'>Revenue : "+total_planned_revenue+" - Project Power : "+total_project_power+" - "+total_deals+" Deals</div>")
    	        
            }).guardedCatch(function (type, error){
            	console.log(error);
            });
		}
		else{
			$('#crm_pipeline_total').remove()
		}
		return res;
	}
	
})

});