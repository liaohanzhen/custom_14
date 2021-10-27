odoo.define('product_management.product_kanbanrender', function (require) {
"use strict";

    const ProductKanbanRecord = require('product_management.product_kanbanrecord');
    const KanbanRenderer = require('web.KanbanRenderer');

    const ProductKanbanRenderer = KanbanRenderer.extend({
        config: _.extend({}, KanbanRenderer.prototype.config, {
            KanbanRecord: ProductKanbanRecord,
        }),
        updateSelection: function (selectedRecords) {
            // To keep selected products when switching between pages and filters
            _.each(this.widgets, function (widget) {
                var selected = _.contains(selectedRecords, widget.id);
                widget._updateRecordView(selected);
            });
        },
    });

    return ProductKanbanRenderer;

});
