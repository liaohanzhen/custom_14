# -*- coding: utf-8 -*-
from odoo import models, api

class StockPicking(models.Model):
    _inherit = "stock.picking"
    
#     @api.multi
#     def check_quality(self):
#         if self.check_ids:
#             if self.pack_operation_product_ids:
#                 serial_packs = self.pack_operation_product_ids.filtered(lambda x: x.product_id.tracking == 'serial')
#                 for pack in serial_packs:
#                     check_serial = self.check_ids.filtered(lambda x: x.product_id.id==pack.product_id.id)
#                     check_serial.filtered(lambda x:x.lot_id==False)
#         res = super(StockPicking, self).check_quality()
#         return res
    
#     @api.multi
#     def action_confirm(self):
#         res = super(StockPicking, self).action_confirm()
#         operation_lot_obj = self.env['stock.pack.operation.lot']
#         for picking in self:
#             if picking.check_ids and picking.pack_operation_product_ids:
#                 for operation in picking.pack_operation_product_ids:
#                     operation_product_checklists = picking.check_ids.filtered(lambda x:x.product_id.id==operation.product_id.id)
#                     checlist_lots = operation_product_checklists.mapped("lot_id")
#                     if checlist_lots:
#                         for lot in checlist_lots:
#                             operation_lot_obj.create({'operation_id':operation.id, 'lot_id':lot.id,'lot_name' : lot.name,})
#                     #operation._onchange_packlots()
#                     operation.qty_done = sum([x.qty for x in operation.pack_lot_ids])
#         return res