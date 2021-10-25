odoo.define('stock_removal_location_by_priority.LinesWidgetExt', function (require) {
'use strict';

var lines = require('stock_barcode.LinesWidget');

lines.include({
    _sortProductLines: function (lines) {
    console.log("===========")
        return lines.sort(function(a,b) {
            return a.display_name.localeCompare(b.display_name, {ignorePunctuation: true});
        });
    },
});

//return LinesWidget;

});
