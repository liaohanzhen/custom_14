odoo.define('knowsystem.knowsystem_readonly_formcontroller', function (require) {
"use strict";

    const FormController = require('web.FormController');

    const KnowSystemReadonlyFormController = FormController.extend({
        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
            this.activeActions = false;
        },
    });
    return  KnowSystemReadonlyFormController;

});
