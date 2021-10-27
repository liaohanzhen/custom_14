odoo.define('frogblue_webshop_fixes.wishlist_animate', function (require) {
    "use strict";

    var publicWidget = require('web.public.widget');
    //var core = require('web.core');
	//var QWeb = core.qweb;

	publicWidget.registry.ProductWishlist.include({
		_updateWishlistView: function () {
	        const $wishButton = $('.o_wsale_my_wish');
	        /*if ($wishButton.hasClass('o_wsale_my_wish_hide_empty')) {
	            $wishButton.toggleClass('d-none', !this.wishlistProductIDs.length);
	        }*/
	        $wishButton.find('.my_wish_quantity').text(this.wishlistProductIDs.length);
	    },
	});

	//QWeb.add_template('/frogblue_webshop_fixes/static/src/xml/customise_option.xml');
});
