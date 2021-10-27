odoo.define('web_gantt_ext.GanttModelEXT', function (require) {
"use strict";

var GanttModel = require('web_gantt.GanttModel');

GanttModel.include({
	
	_setRange: function (focusDate, scale) {
		debugger;
		    this.ganttData.scale = scale;
		    this.ganttData.focusDate = focusDate;
		    if (this.ganttData.dynamicRange) {
		        this.ganttData.startDate = focusDate.clone().startOf(this.SCALES[scale].interval);
		        this.ganttData.stopDate = this.ganttData.startDate.clone().add(1, scale);
		    } else {
		        this.ganttData.startDate = focusDate.clone().startOf(scale);
		        this.ganttData.stopDate = focusDate.clone().endOf(scale);
		        debugger;
		this.ganttData.startDate._d.setHours(7)
		this.ganttData.stopDate._d.setHours(18)    
		    }
		},
	});



});