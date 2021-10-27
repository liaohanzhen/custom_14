odoo.define('avietfils_calendar.CalendarRendererTwo', function (require) {
    "use strict";
    var calendar = require('web.CalendarRenderer')
    var core = require('web.core');
    var session = require('web.session');
    var calendarModel = require('web.CalendarModel');
    var _t = core._t;
    const { createYearCalendarView } = require('/web/static/src/js/libs/fullcalendar.js');

//    console.log(calendarModel)
    calendarModel.include({
        _loadColors: function (element, events) {
            if (this.fieldColor) {
                var fieldName = this.fieldColor;
                _.each(events, function (event) {
                    var value = event.record[fieldName];
                    if (typeof value === "string"){
                        event.color_index = _.isArray(value) ? value[0] : value;
                    }
                    else{
                        event.color_index = _.isArray(value) ? value[0] % 30 : value % 30;
                    }
                });
                this.model_color = this.fields[fieldName].relation || element.model;
            }
            return Promise.resolve();
        },
    });

    return calendar.include({
        getColor: function (key) {
            if (!key) {
                return;
            }
            if (this.color_map[key]) {
                return this.color_map[key];
            }
            // check if the key is a css color
            if (typeof key === 'string' && key.match(/^((#[A-F0-9]{3})|(#[A-F0-9]{6})|((hsl|rgb)a?\(\s*(?:(\s*\d{1,3}%?\s*),?){3}(\s*,[0-9.]{1,4})?\))|)$/i)) {
                return this.color_map[key] = key;
            }
            if (typeof key === 'number' && !(key in this.color_map)) {
                return this.color_map[key] = key;
            }
//            var index = (((_.keys(this.color_map).length + 1) * 5) % 24) + 1;
            var index = key.replace(' ','_').toLowerCase()
            this.color_map[key] = index;
            return index;
        },
        _getFullCalendarOptions: function (fcOptions) {
            var self = this;
            const options = Object.assign({}, this.state.fc_options, {
                plugins: [
                    'moment',
                    'interaction',
                    'dayGrid',
                    'timeGrid'
                ],
                eventDrop: function (eventDropInfo) {
                    var event = self._convertEventToFC3Event(eventDropInfo.event);
                    self.trigger_up('dropRecord', event);
                },
                eventResize: function (eventResizeInfo) {
                    self._unselectEvent();
                    var event = self._convertEventToFC3Event(eventResizeInfo.event);
                    self.trigger_up('updateRecord', event);
                },
                eventClick: function (eventClickInfo) {
                    eventClickInfo.jsEvent.preventDefault();
                    eventClickInfo.jsEvent.stopPropagation();
                    var eventData = eventClickInfo.event;
                    self._unselectEvent();
                    $(self.calendarElement).find(_.str.sprintf('[data-event-id=%s]', eventData.id)).addClass('o_cw_custom_highlight');
                    self._renderEventPopover(eventData, $(eventClickInfo.el));
                },
                yearDateClick: function (info) {
                    self._unselectEvent();
                    info.view.unselect();
                    if (!info.events.length) {
                        if (info.selectable) {
                            const data = {
                                start: info.date,
                                allDay: true,
                            };
                            if (self.state.context.default_name) {
                                data.title = self.state.context.default_name;
                            }
                            self.trigger_up('openCreate', self._convertEventToFC3Event(data));
                        }
                    } else {
                        self._renderYearEventPopover(info.date, info.events, $(info.dayEl));
                    }
                },
                select: function (selectionInfo) {
                    // Clicking on the view, dispose any visible popover. Otherwise create a new event.
                    if (self.$('.o_cw_popover').length) {
                        self._unselectEvent();
                    }
                    var data = {start: selectionInfo.start, end: selectionInfo.end, allDay: selectionInfo.allDay};
                    if (self.state.context.default_name) {
                        data.title = self.state.context.default_name;
                    }
                    self.trigger_up('openCreate', self._convertEventToFC3Event(data));
                    if (self.state.scale === 'year') {
                        self.calendar.view.unselect();
                    } else {
                        self.calendar.unselect();
                    }
                },
                eventRender: function (info) {
                    var event = info.event;
                    var element = $(info.el);
                    var view = info.view;
                    element.attr('data-event-id', event.id);
                    if (view.type === 'dayGridYear') {
                        const color = this.getColor(event.extendedProps.color_index);
                        if (typeof color === 'string') {
                            element.css({
                                backgroundColor: color,
                            });
                        } else if (typeof color === 'number') {
                            element.addClass(`o_calendar_color_${color}`);
                        } else {
                            element.addClass('o_calendar_color_1');
                        }
                    } else {
                    var $render = $(self._eventRender(event));
                    element.find('.fc-content').html($render.html());
                    element.addClass($render.attr('class'));
                    if(view.type === "timeGridWeek" && !(event.extendedProps.record.x_studio_field_3E2nL in session.allow_back_color)){
                        element.addClass('o_cw_graybg');
                    }
                    // Add background if doesn't exist
                    if (!element.find('.fc-bg').length) {
                        element.find('.fc-content').after($('<div/>', {class: 'fc-bg'}));
                    }
                    if (view.type === 'dayGridMonth' && event.extendedProps.record) {
                        var start = event.extendedProps.r_start || event.start;
                        var end = event.extendedProps.r_end || event.end;
                        // Detect if the event occurs in just one day
                        // note: add & remove 1 min to avoid issues with 00:00
                        var isSameDayEvent = moment(start).clone().add(1, 'minute').isSame(moment(end).clone().subtract(1, 'minute'), 'day');
                        if (!event.extendedProps.record.allday && isSameDayEvent) {
                            // For month vie
                            if(!(event.extendedProps.record.x_studio_field_3E2nL in session.allow_back_color)){
                                element.addClass('o_cw_nobg');
                            }
                            if (event.extendedProps.showTime && !self.hideTime) {
                                const displayTime = moment(start).clone().format(self._getDbTimeFormat());
                                element.find('.fc-content .fc-time').text(displayTime);
                            }
                        }
                    }

                    // On double click, edit the event
                    element.on('dblclick', function () {
                        self.trigger_up('edit_event', {id: event.id});
                    });
                    }
                },
                datesRender: function (info) {
                    const viewToMode = Object.fromEntries(
                        Object.entries(self.scalesInfo).map(([k, v]) => [v, k])
                    );
                    self.trigger_up('viewUpdated', {
                        mode: viewToMode[info.view.type],
                        title: info.view.title,
                    });
                },
                // Add/Remove a class on hover to style multiple days events.
                // The css ":hover" selector can't be used because these events
                // are rendered using multiple elements.
                eventMouseEnter: function (mouseEnterInfo) {
                    $(self.calendarElement).find(_.str.sprintf('[data-event-id=%s]', mouseEnterInfo.event.id)).addClass('o_cw_custom_hover');
                },
                eventMouseLeave: function (mouseLeaveInfo) {
                    if (!mouseLeaveInfo.event.id) {
                        return;
                    }
                    $(self.calendarElement).find(_.str.sprintf('[data-event-id=%s]', mouseLeaveInfo.event.id)).removeClass('o_cw_custom_hover');
                },
                eventDragStart: function (mouseDragInfo) {
                    $(self.calendarElement).find(_.str.sprintf('[data-event-id=%s]', mouseDragInfo.event.id)).addClass('o_cw_custom_hover');
                    self._unselectEvent();
                },
                eventResizeStart: function (mouseResizeInfo) {
                    $(self.calendarElement).find(_.str.sprintf('[data-event-id=%s]', mouseResizeInfo.event.id)).addClass('o_cw_custom_hover');
                    self._unselectEvent();
                },
                eventLimitClick: function () {
                    self._unselectEvent();
                    return 'popover';
                },
                windowResize: function () {
                    self._render();
                },
                views: {
                    timeGridDay: {
                        columnHeaderFormat: 'LL'
                    },
                    timeGridWeek: {
                        columnHeaderFormat: 'ddd D'
                    },
                    dayGridMonth: {
                        columnHeaderFormat: 'dddd'
                    }
                },
                height: 'parent',
                unselectAuto: false,
                dir: _t.database.parameters.direction,
                events: (info, successCB) => {
                    successCB(self.state.data);
                },
            }, fcOptions);
            options.plugins.push(createYearCalendarView(FullCalendar, options));
            return options;
        },
    });

});