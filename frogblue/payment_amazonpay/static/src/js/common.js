odoo.define('payment_amazonpay.common', function (require) {
"use strict";


const utils = require('web.utils');


function onLogout()
{
    // do logout if loaded
    if (window.amazon && amazon.Login)
    {
        amazon.Login.logout();
    }

    // and remove cookie
    utils.set_cookie('amazon_Login_accessToken', '', -1)
    utils.set_cookie('amazon_Login_state_cache', '', -1)
    utils.set_cookie('apay-session-set', '', -1)
}


return {
    onLogout: onLogout,
}


});
