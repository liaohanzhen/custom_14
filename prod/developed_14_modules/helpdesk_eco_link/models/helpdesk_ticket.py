# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'
    
    eco_ids = fields.One2many('mrp.eco','ticket_id','ECO Orders', copy=False)
    count_eco = fields.Integer(compute='_compute_eco_order_count', string='# of ECOs', store=True)
    
    @api.depends('eco_ids')        
    def _compute_eco_order_count(self):
        for ticket in self:
            ticket.count_eco = len(ticket.eco_ids)
        
    def action_create_eco_order(self):
        action = self.env.ref('mrp_plm.mrp_eco_action_main',False)
        if not action:
            return
        result = action.read()[0]
        res = self.env.ref('mrp_plm.mrp_eco_view_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        ctx = self._context.copy()
        ctx.update({'default_notes':self.description,'default_ticket_id':self.id, 'default_user_id' : self.user_id.id})
        result['context'] = ctx
        return result
    
    def action_view_eco_order(self):
        orders = self.eco_ids
        action = self.env.ref('mrp_plm.mrp_eco_action_main')
        
        result = action.read()[0]
        ctx = self._context.copy()
        ctx.update({'default_notes':self.description,'default_ticket_id':self.id})
        result['context'] = ctx
        if len(orders) > 1:
            result['domain'] = [('ticket_id', '=', self.id)]
        elif len(orders) == 1:
            res = self.env.ref('mrp_plm.mrp_eco_view_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = orders.ids[0]
        else:
            return True
        return result
    