odoo.define('cloud_base/static/src/models/thread/thread.js', function (require) {
'use strict';

    const { 
        registerInstancePatchModel,
        registerFieldPatchModel,
    } = require('mail/static/src/model/model_core.js');
    const { attr, } = require('mail/static/src/model/model_field.js');

    registerInstancePatchModel('mail.thread', 'cloud_base/static/src/models/thread/thread.js', {               
        /** 
          * Re-write to calculate wheter related object has a cloud folder
        */
        async fetchAttachments() {
            this._super(...arguments);
            const checkSync = await this.async(() => this.env.services.rpc({
                model: "sync.object",
                method: 'is_this_document_synced',
                args: [this.model, this.id],
            }));
            this.update({ isCloudSynced: checkSync });
        },
        /**
          * The method to calculate and open cloud folder
        */ 
        async openCloudFolder() {
            const action = await this.env.services.rpc({
                model: 'ir.attachment',
                method: 'open_cloud_folder',
                args: [{
                    "res_model": this.model,
                    "res_id": this.id,
                }],
            });
            if (action) {this.env.bus.trigger('do-action', {action,});};
        },
    });

    registerFieldPatchModel('mail.thread', 'cloud_base/static/src/models/thread/thread.js', {
        /**
         * Boolean that determines whether this thread has a Google Drive Folder
         */
        isCloudSynced: attr({default: false,}),

    });

});
        