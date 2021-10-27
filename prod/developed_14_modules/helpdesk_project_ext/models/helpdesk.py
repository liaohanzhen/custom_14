# -*- coding: utf-8 -*-
from odoo import models, fields, api, tools

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'
    
    task_ids = fields.One2many('project.task','ticket_id','Tasks', copy=False)
    count_tasks = fields.Integer(compute='_compute_task_count', string='# of Tasks', store=True)
    description_html = fields.Html("Description")
    
    mgmtsystem_ids = fields.One2many('mgmtsystem.action','ticket_id','Cars', copy=False)
    count_mgmtsystem = fields.Integer(compute='_compute_mgmtsystem_count', string='# of Cars', store=True)
    
        
    @api.depends('mgmtsystem_ids')
    def _compute_mgmtsystem_count(self):
        for ticket in self:
            ticket.count_mgmtsystem = len(ticket.mgmtsystem_ids)
    
    @api.depends('task_ids')        
    def _compute_task_count(self):
        for ticket in self:
            ticket.count_tasks = len(ticket.task_ids)

    def action_create_mgmtsystem_action(self):
        action = self.env.ref('mgmtsystem_action.open_mgmtsystem_action_list',False)
        if not action:
            return
        result = action.read()[0]
        res = self.env.ref('mgmtsystem_action.view_mgmtsystem_action_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        ctx = self._context.copy()
        ctx.update({'default_description':self.description,'default_ticket_id':self.id, 'default_user_id':self.user_id.id, 'default_name': self.name})
        result['context'] = ctx
        return result
    
    def action_create_task(self):
        action = self.env.ref('project.action_view_task',False)
        if not action:
            return
        result = action.read()[0]
        res = self.env.ref('project.view_task_form2', False)
        result['views'] = [(res and res.id or False, 'form')]
        ctx = self._context.copy()
        ctx.update({'default_partner_id':self.partner_id.id,'default_description':self.description,'default_ticket_id':self.id, 'default_user_id':self.user_id.id, 'default_name': self.name})
        result['context'] = ctx
        return result
     
    def action_view_mgmtsystem_action(self):
        action = self.env.ref('mgmtsystem_action.open_mgmtsystem_action_list')
        result = action.read()[0]
        
        ctx = self._context.copy()
        ctx.update({'default_description':self.description,'default_ticket_id':self.id, 'default_user_id':self.user_id.id, 'default_name': self.name})
        result['context'] = ctx
        
        mgmtsystems = self.mgmtsystem_ids
        if len(mgmtsystems) > 1:
            result['domain'] = [('ticket_id', '=', self.id)]
        elif len(mgmtsystems) == 1:
            res = self.env.ref('mgmtsystem_action.view_mgmtsystem_action_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = mgmtsystems.ids[0]
        else:
            return True #result = {'type': 'ir.actions.act_window_close'}
        return result
    
    def action_view_tasks(self):
        action = self.env.ref('project.action_view_task')
        result = action.read()[0]
        
        ctx = self._context.copy()
        ctx.update({'default_partner_id':self.partner_id.id,'default_description':self.description,'default_ticket_id':self.id, 'default_user_id':self.user_id.id, 'default_name': self.name})
        result['context'] = ctx
        
        task_ids = self.task_ids
        if len(task_ids) > 1:
            result['domain'] = [('ticket_id', '=', self.id)]
        elif len(task_ids) == 1:
            res = self.env.ref('project.view_task_form2', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = task_ids.ids[0]
        else:
            return True #result = {'type': 'ir.actions.act_window_close'}
        return result