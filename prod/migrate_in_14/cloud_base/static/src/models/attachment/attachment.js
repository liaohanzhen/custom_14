odoo.define('cloud_base/static/src/models/attachment/attachment.js', function (require) {
'use strict';

    const { 
        registerInstancePatchModel,
        registerClassPatchModel,
        registerFieldPatchModel,
    } = require('mail/static/src/model/model_core.js');
    const { attr, } = require('mail/static/src/model/model_field.js');


    registerClassPatchModel('mail.attachment', 'cloud_base/static/src/models/attachment/attachment.js', {
        /**
         * Re-write to pass data important for synced attachments
         */
        convertData(data) {
            const data2 = this._super(data);
            if ('cloud_key' in data && data.cloud_key) {
                data2.cloudSynced = true;
            }; 
            if ('mimetype' in data) {
                if (data.mimetype != 'application/octet-stream' && data.mimetype != 'special_cloud_folder') {
                    data2.cloudDownloadable = true;;
                }
            };
            if ('url' in data) {
                if (data.url) {
                    data2.cloudURL = data.url;
                };
            };
            return data2
        },
    });


    registerInstancePatchModel('mail.attachment', 'cloud_base/static/src/models/attachment/attachment.js', {               
        /**
         * The method to open Google Drive Link
         */
        openCloudLink() {
            const action = {
                type: 'ir.actions.act_url',
                target: 'new',
                url: this.cloudURL,
            };
            this.env.bus.trigger('do-action', {action,});
        },
    });

    registerFieldPatchModel('mail.attachment', 'cloud_base/static/src/models/attachment/attachment.js', {
        cloudURL: attr({
            default: false,
        }),
        /**
         * Whether this atatchment was already synced
         */
        cloudSynced: attr({
            default: false,
        }),
        /**
         * Whether this atatchment me downloaded from clouds
         */
        cloudDownloadable: attr({
            default: false,
        }),
    });



});
        