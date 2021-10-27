from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        rtn = super(StockMove, self)._prepare_move_line_vals(quantity=quantity, reserved_quant=reserved_quant)
        if self.sale_line_id:
            if 'lot_id' in rtn:
                rtn.pop('lot_id')
        return rtn


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def write(self, vals):
        lot_id = vals.get('lot_id')
        if lot_id:
            for line in self:
                vals.pop('lot_id')
                self.env.cr.execute("UPDATE stock_move_line SET lot_id = %s WHERE id = %s", (lot_id, line.id))
        return super(StockMoveLine, self).write(vals)
