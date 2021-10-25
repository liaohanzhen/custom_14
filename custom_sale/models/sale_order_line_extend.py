from odoo import models, fields


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    demo = fields.Char(string="Demo Field")

    # def _prepare_procurement_values(self, group_id=False):
    #     rtn = super()._prepare_procurement_values(group_id)
    #     rtn.update({'demo': self.demo})
    #     return rtn
    #


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    demo = fields.Char(string="Demo Field")

    # def create(self, val_list):
    #     rtn = super().create(val_list)
    #     print(rtn.move_id.demo)
    #     rtn.demo = rtn.move_id.demo
    #     return rtn

    # def write(self, vals):
    #     rtn = super(StockMoveLine, self).write(vals)
    #     rtn.demo = rtn.move_id.demo
    #     return rtn


class StockMove(models.Model):
    _inherit = 'stock.move'

    # demo = fields.Char(string='Demo Field')

    def _get_new_picking_values(self):
        rtn = super(StockMove, self)._get_new_picking_values()
        rtn.update({'transfer': self.sale_line_id.order_id.transfer})
        return rtn

    # def create(self, vals_list):
    #     rtn = super(StockMove, self).create(vals_list)
    #     print(rtn)
    #     return rtn

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        rtn = super(StockMove, self)._prepare_move_line_vals(quantity, reserved_quant)
        rtn.update({'demo': self.sale_line_id.demo})
        return rtn


#
# class StockRule(models.Model):
#     _inherit = 'stock.rule'
#
#     def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id,
#                                values):
#         rtn = super(StockRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name,
#                                                             origin, company_id, values)
#         demo = values.get('demo')
#         rtn.update({'demo': demo})
#         return rtn


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    transfer = fields.Char(string='Transfer')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    transfer = fields.Char(string='Transfer')
