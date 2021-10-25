from odoo import http, _
from odoo.http import request
from odoo.addons.stock_barcode.controllers.main import StockBarcodeController


class StockBarcodeControllerExtend(StockBarcodeController):

    @http.route('/stock_barcode/get_set_barcode_view_state', type='json', auth='user')
    def get_set_barcode_view_state(self, model_name, record_id, mode, write_field=None, write_vals=None):
        rtn = super(StockBarcodeControllerExtend, self).get_set_barcode_view_state(model_name, record_id, mode, write_field=write_field, write_vals=write_vals)
        for picking in rtn:
            lines = picking.pop('move_line_ids')
            picking['move_line_ids'] = sorted(lines, key=lambda line: line['display_name'])
        return rtn
