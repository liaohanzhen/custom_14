odoo.define('website_5b.print_action_item_check', function (require) {
'use strict';
var core = require('web.core');
var ajax = require('web.ajax');
var qweb = core.qweb;
console.log("Extended called")
console.log(qweb)

ajax.loadXML('/website_5b/static/src/js/extended_template.xml', qweb);
});