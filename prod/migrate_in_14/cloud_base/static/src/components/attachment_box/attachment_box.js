odoo.define('cloud_base/static/src/components/attachment_box/attachment_box.js', function (require) {
'use strict';

    const components = {AttachmentBox: require('mail/static/src/components/attachment_box/attachment_box.js'),};
    const { patch } = require('web.utils');
    const { useState } = owl;

    patch(components.AttachmentBox, 'cloud_base/static/src/components/attachment_box/attachment_box.js', {
        /**
         * @private
         * @param {Event} ev
         */
        _onOpenCloudFolder(ev) {
            ev.preventDefault();
            ev.stopPropagation();
            this.thread.openCloudFolder()
        },
    });

});
