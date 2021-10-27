# -*- coding: utf-8 -*-
from odoo import models, fields, api

class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'
    
    def add_follower(self, member_ids):
        if member_ids:
            self.message_subscribe(partner_ids=self.env['res.users'].browse(member_ids).mapped('partner_id').ids)
            
            
    @api.model
    def create(self, values):
        team = super(HelpdeskTeam, self).create(values)
        team.add_follower(team.member_ids.ids)
        return team
    
    def write(self, values):
        result = super(HelpdeskTeam, self).write(values)
        member_ids = values.get('member_ids',False)
        if member_ids:
            members = self.resolve_2many_commands('member_ids',member_ids)
            member_ids = [m.get('id') for m in members if m.get('id')]
            self.add_follower(member_ids)
        return result
    
class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'
    
    purchase_order_ids = fields.One2many('purchase.order','ticket_id','Purchase Orders', copy=False)
    count_pos = fields.Integer(compute='_compute_purchase_order_count', string='# of POs', store=True)
    
    @api.depends('purchase_order_ids')        
    def _compute_purchase_order_count(self):
        for ticket in self:
            ticket.count_pos = len(ticket.purchase_order_ids)
        
    def action_create_purchase_order(self):
        action = self.env.ref('purchase.purchase_rfq',False)
        if not action:
            return
        result = action.read()[0]
        res = self.env.ref('purchase.purchase_order_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        ctx = self._context.copy()
        ctx.update({'default_notes':self.description,'default_ticket_id':self.id})
        result['context'] = ctx
        return result
    
    def action_view_purchase_order(self):
        purchase_orders = self.purchase_order_ids
        if purchase_orders.filtered(lambda x:x.state not in ['draft']):
            action = self.env.ref('purchase.purchase_form_action')
        else:
            action = self.env.ref('purchase.purchase_rfq')
        result = action.read()[0]
        ctx = self._context.copy()
        ctx.update({'default_notes':self.description,'default_ticket_id':self.id})
        result['context'] = ctx
        if len(purchase_orders) > 1:
            result['domain'] = [('ticket_id', '=', self.id)]
        elif len(purchase_orders) == 1:
            res = self.env.ref('purchase.purchase_order_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = purchase_orders.ids[0]
        else:
            return True
        return result

class HelpdeskStage(models.Model):
    _inherit = 'helpdesk.stage'
    
    is_open_stage = fields.Boolean('Open Kanban Stage', help='Tickets in this stage are considered as Open.')
    
    