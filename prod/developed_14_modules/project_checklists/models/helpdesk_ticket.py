# -*- coding: utf-8 -*-
from odoo import models,fields,api

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'
    
    checklist_item_ids = fields.One2many('project.checklists.item','ticket_id','Checklist Items')
    
    def write(self, vals):
        res = super(HelpdeskTicket, self).write(vals)
        if vals.get('stage_id'):
            for ticket in self:
                if ticket.checklist_item_ids:
                    new_vals = {'description':ticket.stage_id.name}
                    if ticket.stage_id.is_close:
                        new_vals.update({'checklist_done':True,'user_id':ticket.user_id.id or self._uid,'date': fields.Date.context_today(self)})
                    ticket.sudo().checklist_item_ids.write(new_vals)
        return res