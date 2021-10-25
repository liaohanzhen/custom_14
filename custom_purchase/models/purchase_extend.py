from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    demo = fields.Char(string='Demo Field')

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        rtn = super()._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom)
        rtn.update({'demo': self.demo})
        return rtn

    def _prepare_account_move_line(self, move=False):
        rtn = super(PurchaseOrderLine, self)._prepare_account_move_line(move)
        rtn.update({'demo': self.demo})
        return rtn


class StockMove(models.Model):
    _inherit = "stock.move"

    demo = fields.Char(string='Demo Field')


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    demo = fields.Char(string='Demo Field')


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    transfer = fields.Char(string='Transfer')

    def _prepare_picking(self):
        rtn = super()._prepare_picking()
        rtn['transfer'] = self.transfer
        return rtn


class Picking(models.Model):
    _inherit = "stock.picking"

    transfer = fields.Char(string='Transfer')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _prepare_invoice_line(self, **kwargs):
        rtn = super()._prepare_invoice_line(**kwargs)
        rtn['demo'] = self.demo
        return rtn
