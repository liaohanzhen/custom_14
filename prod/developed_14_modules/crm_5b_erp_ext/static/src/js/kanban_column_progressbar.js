odoo.define('web.KanbanColumnProgressBarAureliehocquel', function (require) {
'use strict';

var session = require('web.session');

var KanbanColumnProgressBar = require('web.KanbanColumnProgressBar');
var utils = require('web.utils');

KanbanColumnProgressBar.include({
	
    init: function (parent, options, columnState) {
        this._super.apply(this, arguments);
        // <progressbar/> attributes
        this.sumFieldMW = columnState.progressBarValues.sum_field_mw;
        //KanbanColumnProgressBar.prototype._super.apply(this, arguments);
        // Previous progressBar state
        var state = options.progressBarStates[this.columnID];
        if (state) {
            this.totalCounterValueMW = state.totalCounterValueMW;
        }
        // Prepare currency (TODO this should be automatic... use a field ?)
        //var sumFieldMWInfo = this.sumFieldMW && columnState.fieldsInfo.kanban[this.sumFieldMW];
        
    },
    /**
     * @override
     */
    start: function () {
        var self = this;

        this.$bars = {};
        _.each(this.colors, function (val, key) {
            self.$bars[val] = self.$('.bg-' + val + '-full');
        });
        this.$counter = this.$('.o_kanban_counter_side');
        this.$number = this.$counter.find('b');
        this.$counterMW = this.$('.o_kanban_counter_side');
        this.$numberMW = this.$counterMW.find('#counter_mw');
        
        if (this.sumFieldMW) {
            var $mw = $('<span/>', {
                text: 'W',
            });
            $mw.appendTo(this.$counterMW);
            
        }

        return this._super.apply(this, arguments).then(function () {
            // This should be executed when the progressbar is fully rendered
            // and is in the DOM, this happens to be always the case with
            // current use of progressbars

            var subgroupCounts = {};
            _.each(self.colors, function (val, key) {
                var subgroupCount = self.columnState.progressBarValues.counts[key] || 0;
                if (self.activeFilter === key && subgroupCount === 0) {
                    self.activeFilter = false;
                }
                subgroupCounts[key] = subgroupCount;
            });
            self.groupCount = self.columnState.count;
            self.subgroupCounts = subgroupCounts;
            self.prevTotalCounterValue = self.totalCounterValue;
            self.totalCounterValue = self.sumField ? (self.columnState.aggregateValues[self.sumField] || 0) : self.columnState.count;
            //Added
            self.prevTotalCounterValueMW = self.totalCounterValueMW;
            self.totalCounterValueMW = self.sumFieldMW ? (self.columnState.aggregateValues[self.sumFieldMW] || 0) : self.columnState.count;
            
            self._notifyState();
            self._render();
        });
    },
    /*start: function () {
    	var self = this;
    	
    	this.$counterMW = this.$('.o_kanban_counter_side');
        this.$numberMW = this.$counterMW.find('#counter_mw');
        return this._super.apply(this, arguments).then(function () {
            debugger;
        	self.prevTotalCounterValueMW = self.totalCounterValueMW;
            self.totalCounterValueMW = self.sumFieldMW ? (self.columnState.aggregateValues[self.sumFieldMW] || 0) : self.columnState.count;
            
        });
    },*/

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Updates the rendering according to internal data. This is done without
     * qweb rendering because there are animations.
     *
     * @private
     */
    _render: function () {
    	//this._super.apply(this, arguments);
    	this._super()
    	var self = this;
        // Display and animate the counter number
        var startMW = this.prevTotalCounterValueMW;
        var endMW = this.totalCounterValueMW;
        var animationClassMW = startMW > 999 ? 'o_kanban_grow' : 'o_kanban_grow_huge';
        if (startMW !== undefined && endMW > startMW && this.ANIMATE) {
            $({currentValueMW: startMW}).animate({currentValueMW: endMW}, {
                duration: 1000,
                start: function () {
                    self.$counterMW.addClass(animationClassMW);
                },
                step: function () {
                    self.$numberMW.html(_getCounterHTML(this.currentValueMW));
                },
                complete: function () {
                    self.$numberMW.html(_getCounterHTML(this.currentValueMW));
                    self.$counterMW.removeClass(animationClassMW);
                },
            });
        } else {
            this.$numberMW.html(_getCounterHTML(endMW));
        }
        function _getCounterHTML(value) {
            return utils.human_number(value, 0, 3);
        }

    },
    /**
     * Notifies the new progressBar state so that if a full rerender occurs, the
     * new progressBar that would replace this one will be initialized with
     * current state, so that animations are correct.
     *
     * @private
     */
    _notifyState: function () {
        this.trigger_up('set_progress_bar_state', {
            columnID: this.columnID,
            values: {
                groupCount: this.groupCount,
                subgroupCounts: this.subgroupCounts,
                totalCounterValue: this.totalCounterValue,
                totalCounterValueMW: this.totalCounterValueMW,
                activeFilter: this.activeFilter,
            },
        });
    },


	});

});
