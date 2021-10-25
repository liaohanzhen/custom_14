from odoo import fields, models


class Picking(models.Model):
    _inherit = "stock.picking"

    sscc = fields.Char(string="SSCC")


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_new_picking_values(self):
        rtn = super(StockMove, self)._get_new_picking_values()
        origin = rtn.get('origin')[1:]
        prefix = '00008401012'
        rtn['sscc'] = prefix + "{:0>8}".format(origin) if len(origin) < 8 else origin[-8:]
        return rtn
