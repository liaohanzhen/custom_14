odoo.define('payment_amazonpay.web.framework', function (require) {
"use strict";


const framework = require('web.framework');     // it's for dependency sequence
const core = require('web.core');

const amzp_common = require('payment_amazonpay.common');


// patch backend logout action
const origLogoutAction = core.action_registry.get('logout');
core.action_registry.add('logout', function ()
{
    amzp_common.onLogout.apply(this, arguments);
    return origLogoutAction.apply(this, arguments);
});


});
