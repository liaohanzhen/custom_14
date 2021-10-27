odoo.define('cloud_base_documents.document_inspector', function (require) {
"use strict";
    
    const fieldRegistry = require('web.field_registry');
    const DocumentsInspector = require('documents.DocumentsInspector');
    const {qweb } = require('web.core');

    DocumentsInspector.include({
        /**
            * re-write to make cloud files not image
        */
        init: function(parent, params) {
            this._super(...arguments);
            for (const resID of params.recordIds) {
                const record = _.findWhere(params.state.data, {res_id: resID});
                if (record) {
                    if (record.data.cloud_key) {
                        this.recordsData[record.id].isGif = false;
                        this.recordsData[record.id].isImage = false;
                        this.recordsData[record.id].isCloud = true;
                    };
                };
            };
        },
        /**
            * re-write to make possible upload of cloud files
        */
        _updateButtons: function () {
            this._super(...arguments);
            const cloudFiles = _.some(this.records, function (record) {
                return record.data.cloud_key && record.data.mimetype !== 'application/octet-stream' && 
                       record.data.mimetype !== 'special_cloud_folder';
            });
            if (cloudFiles) {this.$('.o_inspector_download').prop('disabled', false);};
        },
        /**
            * re-write to make not possible multi upload of cloud files
        */
        _renderField: function (fieldName, options) {
            const record = this.records[0];
            if (fieldName == "url" && record.data.cloud_key) {
                const $row = $(qweb.render('documents.DocumentsInspector.infoRow'));
                const $label = $(qweb.render('documents.DocumentsInspector.fieldLabel', {
                    icon: options.icon,
                    label: options.label || record.fields[fieldName].string,
                    name: fieldName,
                }));
                $label.appendTo($row.find('.o_inspector_label'));
                const FieldWidget = fieldRegistry.get("link_button");
                const fieldWidget = new FieldWidget(this, fieldName, record, options);
                const prom = fieldWidget.appendTo($row.find('.o_inspector_value')).then(function() {
                    const elem = $('.o_inspector_value').find('.o_field_widget');
                    elem.attr('id', fieldName);
                    elem.addClass("cloud_link_docs");
                });
                $row.insertBefore(this.$('.o_inspector_fields tbody tr.o_inspector_divider'));
                return prom;
            }
            else {
                return this._super(fieldName, options);
            }            
        },
    });

    return DocumentsInspector

});
