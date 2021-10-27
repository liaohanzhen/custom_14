odoo.define('popular_menu', function (require) {
    "use strict";

    const WebClient = require('web.WebClient');

    WebClient.include({
        show_application: function () {
            const self = this;
            return this._super.apply(this, arguments).then(function () {
                self.menu.on('menu_clicked', self, self.save_menu)
            });
        },

        save_menu: function (menu) {
            let menu_id = menu['data']['id']
            this._rpc({
                model: 'xf.dashboard.popular.menu',
                method: 'save_menu',
                args: [menu_id]
            });
        },
    });
});