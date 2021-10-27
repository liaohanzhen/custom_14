odoo.define('cloud_base/static/src/components/attachment/attachment.js', function (require) {
'use strict';

    const components = {Attachment: require('mail/static/src/components/attachment/attachment.js'),};
    const { patch } = require('web.utils');

    patch(components.Attachment, 'cloud_base/static/src/components/attachment/attachment.js', {
        /**
         * Re-write to open a cloud link if no preview available
         */  
        _onClickImage(ev) {
            ev.stopPropagation();
            if (this.attachment.cloudSynced && this.attachment.cloudURL && !this.attachment.isViewable) {
                this.attachment.openCloudLink();
            }
            else {this._super(ev);}
        },
        /**
         * The mouse event method to open a cloud link
         */  
        _onClickCloudOpen(ev) {
            ev.stopPropagation();
            this.attachment.openCloudLink();
        },
    });

});
