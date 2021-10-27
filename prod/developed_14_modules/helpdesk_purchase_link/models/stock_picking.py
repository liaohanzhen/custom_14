# -*- coding: utf-8 -*-
from odoo import models, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    def _write(self, vals):
        res = super(StockPicking, self)._write(vals)
        if vals.get('state','')=='done':
            purchase_pickings = self.filtered(lambda picking: picking.purchase_id and picking.purchase_id.ticket_id)
            for picking in purchase_pickings:
                if picking.purchase_id.is_shipped and (len(picking.purchase_id.ticket_id.purchase_order_ids)==1\
                    or all(picking.purchase_id.ticket_id.purchase_order_ids.mapped("is_shipped"))):
                    close_stages = picking.purchase_id.ticket_id.team_id.stage_ids.filtered(lambda x:x.is_close)
                    if close_stages:
                        ctx = self._context.copy()
                        ctx['purchase_order'] = picking.purchase_id
                        picking.purchase_id.ticket_id.with_context(ctx).write({'stage_id' : close_stages[0].id})
        return res