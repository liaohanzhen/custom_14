odoo.define('portal_document_upload.chatter', function(require) {
'use strict';

var utils = require('web.utils');
var PortalChatter = require('portal.chatter').PortalChatter
var ajax = require('web.ajax');
var core = require('web.core');

var qweb = core.qweb;

PortalChatter.include({
	events: _.extend({}, PortalChatter.prototype.events, {
		'change .o_portal_chatter_file_input': '_onFileInputChange',
        'click .o_portal_chatter_attachment_btn': '_onAttachmentButtonClick',
        'click .o_portal_chatter_attachment_delete': 'async _onAttachmentDeleteClick',
        'click .o_portal_chatter_composer_btn': 'async _onSubmitButtonClick',
	}),
	init: function(parent, options){
        this._super.apply(this, arguments);
        this.attachments = [];
	},
	/**
     * @override
     */
    start: function () {
        this.$attachmentButton = this.$('.o_portal_chatter_attachment_btn');
        this.$fileInput = this.$('.o_portal_chatter_file_input');
        this.$sendButton = this.$('.o_portal_chatter_composer_btn');
        this.$attachments = this.$('.o_portal_chatter_composer_form .o_portal_chatter_attachments');
        this.$attachmentIds = this.$('.o_portal_chatter_attachment_ids');
        this.$attachmentTokens = this.$('.o_portal_chatter_attachment_tokens');

        return this._super.apply(this, arguments);
    },
    _loadTemplates: function(){
        return $.when(this._super(), ajax.loadXML('/portal_document_upload/static/src/xml/portal_chatter.xml', qweb));
    },
    /**
     * @private
     */
    _onAttachmentButtonClick: function () {
        this.$fileInput.click();
    },
    _onSubmitButtonClick: function () {
        debugger;
    	return new Promise(function (resolve, reject) {});
    },
    /**
     * @private
     * @param {Event} ev
     * @returns {Promise}
     */
    _onAttachmentDeleteClick: function (ev) {
        var self = this;
        debugger;
        var attachmentId = $(ev.currentTarget).closest('.o_portal_chatter_attachment').data('id');
        var accessToken = _.find(this.attachments, {'id': attachmentId}).access_token;
        ev.preventDefault();
        ev.stopPropagation();

        this.$sendButton.prop('disabled', true);
        return ajax.jsonRpc("/portal/attachment/remove", 'call', {
            'attachment_id': attachmentId,
            'access_token': accessToken,
        }).then(function () {
        	self.attachments = _.reject(self.attachments, {'id': attachmentId});
            self._updateAttachments();
            self.$sendButton.prop('disabled', false);
        })
        /*return this._rpc({
            route: '/portal/attachment/remove',
            params: {
                'attachment_id': attachmentId,
                'access_token': accessToken,
            },
        }).then(function () {
            self.attachments = _.reject(self.attachments, {'id': attachmentId});
            self._updateAttachments();
            self.$sendButton.prop('disabled', false);
        });*/
    },
    getDataURLFromFile: function (file) {
        if (!file) {
            return Promise.reject();
        }
        return new Promise(function (resolve, reject) {
            var reader = new FileReader();
            reader.addEventListener('load', function () {
                resolve(reader.result);
            });
            reader.addEventListener('abort', reject);
            reader.addEventListener('error', reject);
            reader.readAsDataURL(file);
        });
    },
    /**
     * @private
     * @returns {Promise}
     */
    _onFileInputChange: function () {
        var self = this;

        this.$sendButton.prop('disabled', true);

        return Promise.all(_.map(this.$fileInput[0].files, function (file) {
            return self.getDataURLFromFile(file).then(function (result) {
                var params = {
                    'name': file.name,
                    'data': result.split(',')[1],
                    'res_id': self.options.res_id,
                    'res_model': self.options.res_model,
                    'access_token': self.options.token,
                };
                
                return ajax.jsonRpc("/portal/attachment/add_data", 'call', params
                ).then(function (attachment) {
                    self.attachments.push(attachment);
                    self._updateAttachments();
                });    
                /*return self._rpc({
                    route: '/portal/attachment/add_data',
                    params: params,
                }).then(function (attachment) {
                    self.attachments.push(attachment);
                    self._updateAttachments();
                });*/
            });
        })).then(function () {
            self.$sendButton.prop('disabled', false);
        });
    },
    _updateAttachments: function () {
        this.$attachmentIds.val(_.pluck(this.attachments, 'id'));
        this.$attachmentTokens.val(_.pluck(this.attachments, 'access_token'));
        this.$attachments.html(qweb.render('portal.Chatter.Attachments', {
            attachments: this.attachments,
            showDelete: true,
        }));
    },
})
});