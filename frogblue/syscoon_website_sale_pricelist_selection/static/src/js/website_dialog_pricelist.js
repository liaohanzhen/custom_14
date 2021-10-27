odoo.define('syscoon_website_sale_pricelist_selection.pricelist_popup', function (require) {
'use strict';

var publicWidget = require('web.public.widget');
var Dialog = require('web.Dialog');
var core = require('web.core');
var utils = require('web.utils');
var session = require('web.session');
var _t = core._t;
var QWeb = core.qweb;

publicWidget.registry.PricelistPopup = publicWidget.Widget.extend({
    template: 'syscoon_website_sale_pricelist_selection.pricelist.popup',
    xmlDependencies: ['/syscoon_website_sale_pricelist_selection/static/src/xml/pricelist.xml'],
    selector: '.o_pricelist_popup',

    /**
     * @override
     */
    start: function () {
        var selected_pricelist = utils.get_cookie('selected_pricelist');
        if (!selected_pricelist && (session.is_public_user || !session.is_user_pricelist_set)) {
            this.initPriceListDialog();
        }
    },
    initPriceListDialog: async function() {
        var self = this;
        const pricelists = await this._rpc({
            route: "/shop/get/pricelist",
        })
        var dialog = new Dialog(this, {
            size: 'medium',
            title: _t('Select Pricelist'),
            $content: QWeb.render('websitePricelist', {
                pricelists: pricelists
            }),
            buttons: [
                {
                    text: _t("Continue"),
                    classes: 'btn-primary pricelist-dialog',
                    close: true,
                    click: function() {
						dialog.close();
						var args = ''
						if (!session.is_public_user){
							args = '?hide_pricelist_dropdown=1'
						}
                        var selected_pricelist = this.$('#pricelist_popup').val();
                        if (selected_pricelist) {
                            utils.set_cookie('selected_pricelist', selected_pricelist, 30 * 60)
                            return window.location = '/shop/change_pricelist/' + parseInt(selected_pricelist) + args;
                        }
                    },
                },
            ],
        }).open();
    },
});
});


