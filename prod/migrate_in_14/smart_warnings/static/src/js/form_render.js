odoo.define('smart_warnings.form_render', function (require) {
"use strict";

    var core = require('web.core');
    var formRenderer = require('web.FormRenderer');

    var qweb = core.qweb;
    var _t = core._t;

    formRenderer.include({
        _updateView: function ($newContent) {
            //  the method to find existing alerts anad them to the form
            this._super.apply(this, arguments);
            this.$('.smart_alert').remove();
            var self = this;
            if (self.state && self.state.model && self.state.data && self.state.data.id) {
                self._rpc({
                    model: "smart.warning",
                    method: "return_warnings",
                    args: [self.state.model, self.state.data.id],
                    context: {},
                }).then(function (alerts) {
                    if (alerts.length > 0) {
                        var $alertsHTML = qweb.render('SmartAlerts', {"alerts": alerts});
                        if (self.$('.o_form_statusbar').length) {
                            self.$('.o_form_statusbar').after($alertsHTML);
                        } else if (self.$('.o_form_sheet_bg').length) {
                            self.$('.o_form_sheet_bg').prepend($alertsHTML);
                        }
                        else {
                            self.$el.prepend($alertsHTML);
                        }
                    };
                });
            };
        },
    });

    return formRenderer;

});
