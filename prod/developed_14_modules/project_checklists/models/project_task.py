# -*- coding: utf-8 -*-
from odoo import models,fields,api

class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    checklist_items = fields.One2many('project.checklists.item','task_id','Checklist Items')
    count_checklist = fields.Integer("Checklist Count",compute="_compute_checklist_count")
    checklist_progress = fields.Float(compute='_get_checklist_progress', store=True, string='Checklist Progress', group_operator="avg")
    color = fields.Integer('Color Index', compute="change_colore_on_kanban")
    #added_related_fields = fields.Char(string='Added Related Fields',compute='_get_checklist_progress',store=True)
    
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

        
    
    @api.depends('checklist_items.checklist_done')
    def _get_checklist_progress(self):
        for task in self:
            if task.checklist_items:
                #task.added_related_fields = str(task.checklist_items.mapped('related_field_project_id').ids)
                done_checklists = task.checklist_items.filtered(lambda x:x.checklist_done)
                task.checklist_progress = round(100.0 * (len(done_checklists)) / len(task.checklist_items), 2)
            else:
                #task.added_related_fields = str([])
                task.checklist_progress = 0.0
                    
    def _compute_checklist_count(self):
        for task in self:
            task.count_checklist = len(task.checklist_items)
    
    def task_checklist_items(self):
        self.ensure_one()
        action = self.env.ref('project_checklists.action_project_checklists_item')
        result = action.read()[0]
        ctx = dict() #self._context.copy()
        ctx.update({'default_task_id':self.id})
        result['context'] = ctx
        checklist_ids = self.mapped('checklist_items')
        result['domain'] = [('id', 'in', checklist_ids.ids)]
        return result
        