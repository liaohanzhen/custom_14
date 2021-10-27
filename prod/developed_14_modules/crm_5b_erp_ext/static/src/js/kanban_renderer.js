odoo.define('web.KanbanRendererAureliehocquel', function (require) {
'use strict';

var session = require('web.session');

var KanbanRenderer = require('web.KanbanRenderer');
var utils = require('web.utils');
var translation = require('web.translation');
var _t = translation._t;

KanbanRenderer.include({
	
	human_number_custom: function (number, decimals, minDigits, formatterCallback) {
		number = Math.round(number);
		decimals = decimals | 0;
        minDigits = minDigits || 1;
        formatterCallback = formatterCallback || utils.insert_thousand_seps;
        var symbol = '';
		/*var ranges = [
			  { divider: 1e18 , suffix: 'E' },
			  { divider: 1e15 , suffix: 'P' },
			  { divider: 1e12 , suffix: 'T' },
			  { divider: 1e9 , suffix: 'G' },
			  { divider: 1e6 , suffix: 'M' },
			  { divider: 1e3 , suffix: 'k' }
			];
		debugger;
		for (var i = 0; i < ranges.length; i++) {
		    if (number >= ranges[i].divider) {
		    	number = number / ranges[i].divider;
		        symbol = ranges[i].suffix;
		        break;
		    }
		  }
		return formatterCallback('' + number) +' '+ symbol;  */
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
		
		if (this.state.model=='crm.lead'){
			var total_planned_revenue=0;
	        var total_project_power=0;
	        var total_deals = 0;
	        _.each(this.state.data, function (d) {
	        	
	        	if (d.aggregateValues.expected_revenue!=undefined){
	        		total_planned_revenue = total_planned_revenue + d.aggregateValues.expected_revenue; 
	        	}
	        	if (d.aggregateValues.project_power!=undefined){
	        		total_project_power = total_project_power + d.aggregateValues.project_power; 
	        	}
	        	total_deals = total_deals +d.count;
	        })
	        total_planned_revenue = '$ '+this.human_number_custom(total_planned_revenue,0,1); //'$ '+total_planned_revenue+'M'
	        total_project_power = this.human_number_custom(total_project_power,0,1) +'W';
	        /*try {
	        	var currency = session.currencies[this.state.data[0].data[0].data.company_currency.res_id] 
	        }
	        catch(err) {
	        	var currency =false;
	        }*/
	        /*if (currency) {
	            if (currency.position === 'before') {
	            	total_planned_revenue = currency.symbol +total_planned_revenue
	            	
	            } else {
	            	total_planned_revenue = total_planned_revenue + currency.symbol 
	            }
	        }
	        //this.getParent().getParent().getParent().getParent().$el.find('.o_cp_sidebar').prepend("<div id='crm_pipeline_total' style='padding-left: 20%;font-size: 16px;font-weight: 500;'>Revenue : "+total_planned_revenue+" * Project Power : "+total_project_power+"W * "+total_deals+" Deals</div>")
	        */
	       
	        //this.getParent().$el.find('#crm_pipeline_total').remove()
	        //this.$el.before("<div id='crm_pipeline_total' style='padding-left: 20%;font-size: 16px;font-weight: 500;'>Revenue : "+total_planned_revenue+" - Project Power : "+total_project_power+" - "+total_deals+" Deals</div>")
	        
	        $('#crm_pipeline_total').remove()
	        $('div.o_cp_buttons').after("<div id='crm_pipeline_total' style='padding-left: 20%;font-size: 16px;font-weight: 500;'>Revenue : "+total_planned_revenue+" - Project Power : "+total_project_power+" - "+total_deals+" Deals</div>")
		}
		else{
			$('#crm_pipeline_total').remove()
		}

        return res;
	}
})

});