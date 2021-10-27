odoo.define('knowsystem.knowsystem_readonly_formview', function (require) {
"use strict";

    const KnowSystemReadonlyFormController = require('knowsystem.knowsystem_readonly_formcontroller');
    const FormView = require('web.FormView');
    const viewRegistry = require('web.view_registry');

    const KnowSystemReadonlyFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {Controller: KnowSystemReadonlyFormController}),
    });

    viewRegistry.add('knowsystem_readonly_form', KnowSystemReadonlyFormView);

    return KnowSystemReadonlyFormView;

});
