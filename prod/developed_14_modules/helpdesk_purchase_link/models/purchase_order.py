# -*- coding: utf-8 -*-
from odoo import models,fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    ticket_id = fields.Many2one('helpdesk.ticket',string='Ticket', copy=False)
    account_analytic_id = fields.Many2one('account.analytic.account', related='order_line.account_analytic_id', string='Analytic Account')
    
    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            if order.ticket_id:
                open_stages = order.ticket_id.team_id.stage_ids.filtered(lambda x:x.is_open_stage)
                if open_stages:
                    ctx = self._context.copy()
                    ctx['purchase_order'] = order
                    order.ticket_id.with_context(ctx).write({'stage_id' : open_stages[0].id})
        return res