odoo.define('product_management.product_kanbanrecord', function (require) {
"use strict";

    const KanbanRecord = require('web.KanbanRecord');

    const ProductKanbanRecord = KanbanRecord.extend({
        events: _.extend({}, KanbanRecord.prototype.events, {
            'click .product_select': '_productSelect',
            'click .o_kanban_image': '_realOpenRecord',
        }),
        _updateSelect: function (event, selected) {
            // The method to pass selection to the controller
            this.trigger_up('select_record', {
                originalEvent: event,
                resID: this.id,
                selected: selected,
            });
        },
        _updateRecordView: function (select) {
            // Mark the product selected / disselected in the interface
            var kanbanCard = this.$el;
            var checkBox = this.$el.find(".product_select");
            if (select) {
                checkBox.removeClass("fa-square-o");
                checkBox.addClass("fa-check-square-o");
                kanbanCard.addClass("prodkanabanselected");
            }
            else {
                checkBox.removeClass("fa-check-square-o");
                checkBox.addClass("fa-square-o");
                kanbanCard.removeClass("prodkanabanselected");
            };
        },
        _productSelect: function (event) {
            // The method to add to / remove from selection
            event.preventDefault();
            event.stopPropagation();
            var checkBox = this.$el.find(".product_select");
            if (checkBox.hasClass("fa-square-o")) {
                this._updateRecordView(true)
                this._updateSelect(event, true);
            }
            else {
                this._updateRecordView(false);
                this._updateSelect(event, false);
            }
        },
        _openRecord: function (real) {
            // re-write to make selection instead of opening a record
            if (!real) {
                this.$('.product_select').click();
            }
            else {
                this._super.apply(this, arguments);
            }
        },
        _realOpenRecord: function (event) {
            this._openRecord(true);
        },
    });

    return ProductKanbanRecord;

});