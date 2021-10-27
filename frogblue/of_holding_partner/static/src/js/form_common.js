odoo.define("hologram_extensions.form_common_extension", function (require) {
    "use strict";

    var form_common = require('web.form_common');
    var core = require('web.core');
    var data = require('web.data');
    var _t = core._t;
    var CompletionFieldMixin = form_common.CompletionFieldMixin;

    var get_search_result = function (search_val) {
        var self = this;

        var dataset = new data.DataSet(this, this.field.relation, self.build_context());
        this.last_query = search_val;
        var exclusion_domain = [], ids_blacklist = this.get_search_blacklist();
        if (!_(ids_blacklist).isEmpty()) {
            exclusion_domain.push(['id', 'not in', ids_blacklist]);
        }

        return this.orderer.add(dataset.name_search(
            search_val, new data.CompoundDomain(self.build_domain(), exclusion_domain),
            'ilike', this.limit + 1, self.build_context())).then(function (_data) {
            self.last_search = _data;
            // possible selections for the m2o
            var values = _.map(_data, function (x) {
                var y = x[1].split("\n");
                x[1] = y[0];
                x[2] = y[1];
                var value = (self.view.model == 'sale.order' && self.dont_split_newline) ? x[1] + " | " + x[2] : x[1];
                return {
                    label: _.str.escapeHTML(value),
                    value: value,
                    name: value,
                    id: x[0],
                };
            });

            // search more... if more results that max
            if (values.length > self.limit) {
                values = values.slice(0, self.limit);
                values.push({
                    label: _t("Search More..."),
                    action: function () {
                        dataset.name_search(search_val, self.build_domain(), 'ilike', 160).done(function (_data) {
                            self._search_create_popup("search", _data);
                        });
                    },
                    classname: 'o_m2o_dropdown_option'
                });
            }
            // quick create
            var raw_result = _(_data.result).map(function (x) {
                return x[1];
            });
            if (search_val.length > 0 && !_.include(raw_result, search_val) &&
                !(self.options && (self.options.no_create || self.options.no_quick_create))) {
                self.can_create && values.push({
                    label: _.str.sprintf(_t('Create "<strong>%s</strong>"'),
                        $('<span />').text(search_val).html()),
                    action: function () {
                        self._quick_create(search_val);
                    },
                    classname: 'o_m2o_dropdown_option'
                });
            }
            // create...
            if (!(self.options && (self.options.no_create || self.options.no_create_edit)) && self.can_create) {
                values.push({
                    label: _t("Create and Edit..."),
                    action: function () {
                        self._search_create_popup("form", undefined, self._create_context(search_val));
                    },
                    classname: 'o_m2o_dropdown_option'
                });
            }
            else if (values.length === 0) {
                values.push({
                    label: _t("No results to show..."),
                    action: function () {
                    },
                    classname: 'o_m2o_dropdown_option'
                });
            }

            return values;
        });
    };

    var prev_init = CompletionFieldMixin.init;
    CompletionFieldMixin.init = function () {
        prev_init.apply(this, arguments);
        this.dont_split_newline = (this.node.attrs.dont_split_newline == "true" || this.getParent().fields_view.fields[this.name].relation === "res.partner") ? true : false;
        this.get_search_result = get_search_result.bind(this);
    };

});
