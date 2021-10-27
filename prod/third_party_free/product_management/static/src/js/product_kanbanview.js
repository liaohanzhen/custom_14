odoo.define('product_management.product_kanbanview', function (require) {
"use strict";

    const ProductKanbanController = require('product_management.product_kanbancontroller');
    const ProductKanbanModel = require('product_management.product_kanbanmodel');
    const ProductKanbanRenderer = require('product_management.product_kanbanrender');
    const KanbanView = require('web.KanbanView');
    const viewRegistry = require('web.view_registry');

    const { _lt } = require('web.core');

    const ProductKanbanView = KanbanView.extend({
        config: _.extend({}, KanbanView.prototype.config, {
            Controller: ProductKanbanController,
            Model: ProductKanbanModel,
            Renderer: ProductKanbanRenderer,
        }),
        display_name: _lt('Product Management'),
        groupable: false,
    });

    viewRegistry.add('product_kanban', ProductKanbanView);

    return ProductKanbanView;

});