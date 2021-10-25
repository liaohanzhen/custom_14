odoo.define('hospital.LinesWidgetExt', function (require) {
'use strict';

var lines = require('stock_barcode.LinesWidget');

lines.include({
    _sortProductLines: function (lines) {
//        return lines
        lines = this._super.apply(this, arguments);
        console.log("===========", lines);
        return lines.reverse();
    },
});

//return LinesWidget;

});
