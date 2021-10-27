# -*- coding: utf-8 -*-
from odoo import models,fields,api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    checklist_items = fields.One2many('hr.employee.checklists.item','employee_id','Onboarding')
    checklist_items_offboaring_ids = fields.One2many('hr.employee.checklists.item','offboarding_employee_id','Offboarding')
    count_checklist = fields.Integer("Checklist Count",compute="_compute_checklist_count")
    count_offboaring_checklist = fields.Integer("Offboarding Checklist Count",compute="_compute_offboarding_checklist_count")
    checklist_progress = fields.Float(compute='_get_checklist_progress', store=True, string='Onboarding Progress', group_operator="avg")
    offboaring_checklist_progress = fields.Float(compute='_get_offboaring_checklist_progress', store=True, string='Offboarding Progress', group_operator="avg")
    color = fields.Integer('Color Index', compute="change_colore_on_kanban")
    #added_related_fields = fields.Char(string='Added Related Fields',compute='_get_checklist_progress',store=True)
    checklist_item_template_id = fields.Many2one("checklist.item.package","Onboarding template")
    checklist_item_off_template_id = fields.Many2one("checklist.item.package","Offboarding template")
    parent_id = fields.Many2one('hr.employee', string='Manager',track_visibility='always')
    
    @api.onchange('checklist_item_off_template_id')
    def onchange_checklist_item_off_template_id(self):
        if self.checklist_item_off_template_id:
            checklist_items_lines = self.checklist_items_offboaring_ids
            for item in self.checklist_item_off_template_id.emp_checklist_item_ids:
                vals = {
                    'checklist_done':item.checklist_done,
                    'checklist_type' : item.checklist_type,
                    'related_field_id' : item.related_field_id.id,
                    'training_session_id' : item.training_session_id.id,
                    'ticket_id' : item.ticket_id.id,
                    'doc' : item.doc,
                    'file_name' : item.file_name,
                    'description' : item.description,
                    'responsible' : item.responsible.id,
                    'user_id' : item.user_id.id,
                    'date' : item.date,
                    }
                checklist_items_lines += checklist_items_lines.new(vals)
            self.checklist_items_offboaring_ids = checklist_items_lines
            
    @api.onchange('checklist_item_template_id')
    def onchange_checklist_item_template_id(self):
        if self.checklist_item_template_id:
            checklist_items_lines = self.checklist_items
            for item in self.checklist_item_template_id.emp_checklist_item_ids:
                vals = {
                    'checklist_done':item.checklist_done,
                    'checklist_type' : item.checklist_type,
                    'related_field_id' : item.related_field_id.id,
                    'training_session_id' : item.training_session_id.id,
                    'ticket_id' : item.ticket_id.id,
                    'doc' : item.doc,
                    'file_name' : item.file_name,
                    'description' : item.description,
                    'responsible' : item.responsible.id,
                    'user_id' : item.user_id.id,
                    'date' : item.date,
                    }
                checklist_items_lines += checklist_items_lines.new(vals)
            self.checklist_items = checklist_items_lines
            
    @api.depends('checklist_progress','checklist_items')
    def change_colore_on_kanban(self):
        """    this method is used to change color index base on checklists status
        :return: index of color for kanban view    """    
        for record in self:
            color = 0
            if not record.checklist_items:
                color=0
            elif record.checklist_progress == 0:
                color = 11
            elif 1 <= record.checklist_progress <= 99:
                color = 12
            elif record.checklist_progress == 100.0:
                color = 13
            record.color = color
    
    @api.depends('checklist_items_offboaring_ids.checklist_done')
    def _get_offboaring_checklist_progress(self):
        for employee in self:
            if employee.checklist_items_offboaring_ids:
                done_checklists = employee.checklist_items_offboaring_ids.filtered(lambda x:x.checklist_done)
                employee.offboaring_checklist_progress = round(100.0 * (len(done_checklists)) / len(employee.checklist_items_offboaring_ids), 2)
            else:
                employee.offboaring_checklist_progress = 0.0
                
    @api.depends('checklist_items.checklist_done')
    def _get_checklist_progress(self):
        for employee in self:
            if employee.checklist_items:
                done_checklists = employee.checklist_items.filtered(lambda x:x.checklist_done)
                employee.checklist_progress = round(100.0 * (len(done_checklists)) / len(employee.checklist_items), 2)
            else:
                employee.checklist_progress = 0.0
    
    @api.depends("checklist_items_offboaring_ids")
    def _compute_offboarding_checklist_count(self):
        for employee in self:
            employee.count_offboaring_checklist = len(employee.checklist_items_offboaring_ids)
            
    @api.depends('checklist_items')
    def _compute_checklist_count(self):
        for employee in self:
            employee.count_checklist = len(employee.checklist_items)
    
#     @api.multi
    def employee_checklist_items(self):
        self.ensure_one()
        action = self.env.ref('employee_checklists.action_hr_employee_checklists_item')
        result = action.read()[0]
        ctx = dict() #self._context.copy()
        
        if self._context.get('employee_checklist_items_clicked'):
            employee_id = 'offboarding_employee_id'
            #checklist_ids = self.checklist_items_offboaring_ids.ids
        else:
            employee_id = 'employee_id'
            #checklist_ids = self.checklist_items.ids
        ctx.update({'default_'+employee_id:self.id})
        
        result['context'] = ctx
        #checklist_ids = self.mapped('checklist_items')
        #result['domain'] = [('id', 'in', checklist_ids)]
        result['domain'] = [(employee_id, '=', self.id)]
        return result
        