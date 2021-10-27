# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    def onchange(self, values, field_name, field_onchange):
        #Disabled due to performance issues when there is a huge number of inventory lines.
        if field_name == 'line_ids':
            return {}
        return super(StockInventory, self).onchange(values, field_name, field_onchange)


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    prod_lot_id = fields.Many2one(
        'stock.production.lot', 'Lot/Serial Number', check_company=False,
        domain="[('product_id','=',product_id), ('company_id', '=', company_id)]")
    product_barcode = fields.Char(compute='_compute_barcode', store=True)
    
    @api.depends('product_id', 'product_id.barcode')
    def _compute_barcode(self):
        for line in self:
            if not line.product_id:
                line.product_barcode = False
                return
            line.product_barcode = line.product_id.barcode
