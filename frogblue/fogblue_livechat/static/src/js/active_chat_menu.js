odoo.define('fogblue_livechat.ActiveChatMenu', function(require) {
"use strict";
    var config = require('web.config');
    var core = require('web.core');
    var session = require('web.session');
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    const rpc = require("web.rpc");


    var _t = core._t;

    var ActiveChatMenu = Widget.extend({
        template: 'ActiveChatMenu',
        events: {
            'click #active_for_chat': '_onChangeActiveForChat',
        },
        /**
         * @override
         */
        init: function () {
            var self = this;
            this.chat = session.active_for_chat
            this._super.apply(this, arguments);
        },
        toggleChatStatus: function(change=false){
            rpc.query({
                model: 'res.users',
                method: 'toggle_active_for_chat',
                args: [session.uid, change, ],
            }).then(function(res) {
                console.log(res)
                $("#active_for_chat").prop("checked", res)
            });
        },
        _onChangeActiveForChat: function (ev) {
            var self = this;
            self.toggleChatStatus(true)
        },

    });

    SystrayMenu.Items.push(ActiveChatMenu);

    return ActiveChatMenu;

});
