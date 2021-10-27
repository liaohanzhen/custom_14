# -*- coding: utf-8 -*-
from odoo import models,fields,api

class ProjectChecklistItems(models.Model):
    _name='project.checklists.item'
    
#     @api.model
#     def default_get(self, field_list):
#         """ Set 'user_id' and 'date'. """
#         result = super(ProjectChecklistItems, self).default_get(field_list)
#         result['date'] = fields.Date.context_today(self)
#         result['user_id'] = self._uid 
#         return result
    
    checklist_done = fields.Boolean("Checklist")
    checklist_type = fields.Selection([('INFO','INFO'),('ACTION','ACTION'),('DOC','DOC'),('TICKET','TICKET')],string='Type')
    project_field_id = fields.Many2one("ir.model.fields",domain=[('model_id.model','=','project.project'),('ttype','in',['text','char']),('name','!=','display_name'),('store','=',True)],string='Related Field Project')
    related_field_project_id = fields.Many2one("project.base.field.value",string='Related Field Project')
    ticket_id = fields.Many2one("helpdesk.ticket",'Ticket')
    doc = fields.Binary("File Name")
    file_name = fields.Char("Filename")
    description = fields.Char("Description")
    responsible = fields.Many2one("res.users",'Responsible')
    user_id = fields.Many2one("res.users",'User')
    date = fields.Date("Date")
    task_id = fields.Many2one("project.task",'Task')
    project_id = fields.Many2one('project.project',string="Project",related='task_id.project_id',store=True)
    color = fields.Integer('Color Index', compute="change_colore_on_kanban",store=True)
    state = fields.Selection([('To Do','To Do'),('Done','Done')],string='State',compute="change_colore_on_kanban",store=True)
    
    @api.depends('checklist_done')
    def change_colore_on_kanban(self):
        """    this method is used to change color index base on checklists status
        :return: index of color for kanban view    """    
        for record in self:
            if record.checklist_done:
                record.color = 13
                record.state='Done'
            else:
                record.color = 11
                record.state='To Do'
    
    @api.onchange('related_field_project_id')
    def onchange_related_field_project_id(self):
#         if self.project_field_id and self.task_id.project_id:
#             self.description = getattr(self.task_id.project_id,self.project_field_id.name)
        if self.related_field_project_id:
            self.description = self.related_field_project_id.value    
    @api.model
    def create(self,vals):
        res = super(ProjectChecklistItems,self).create(vals)
        if res.checklist_type=='INFO' and res.related_field_project_id and res.description:
            res.related_field_project_id.write({'value':res.description})
#         if res.task_id.project_id and res.project_field_id:
#             res.task_id.project_id.write({res.project_field_id.name:res.description})
        if vals.get("doc") and res.task_id:
            self.env['ir.attachment'].create({'name':res.file_name,'datas':res.doc,'type':'binary', 'res_model':'project.task','res_id':res.task_id.id})
        return res
    
    def write(self,vals):
        res = super(ProjectChecklistItems,self).write(vals)
        if vals.get('checklist_type','')=='INFO' or vals.get("doc"):
            for checklist in self:
                if checklist.checklist_type=='INFO' and checklist.related_field_project_id and checklist.description:
                    checklist.related_field_project_id.write({'value':checklist.description})
#                 if checklist.task_id.project_id and checklist.project_field_id:
#                     checklist.task_id.project_id.write({checklist.project_field_id.name:checklist.description})
                if vals.get("doc") and checklist.task_id:
                    self.env['ir.attachment'].create({'name':checklist.file_name,'datas':checklist.doc,'type':'binary', 'res_model':'project.task','res_id':checklist.task_id.id})
        return res
    
    @api.onchange('checklist_type','description','doc')
    def onchange_checklist_type(self):
        if self.checklist_type=='INFO' and self.description:
            self.checklist_done=True
        elif self.doc:
            self.checklist_done=True
    
    @api.onchange('checklist_done')
    def onchange_checklist_done(self):
        if self.checklist_done:
            self.user_id=self._uid
            self.date = fields.Date.context_today(self)
        else:
            self.user_id=False
            self.date=False
        
    @api.onchange('ticket_id')
    def onchange_ticket_id(self):
        if self.ticket_id:
            self.description=self.ticket_id.stage_id.name
            if self.ticket_id.stage_id.is_close:
                self.checklist_done = True
            else:
                self.checklist_done = False
        
#     @api.onchange('doc')
#     def onchange_doc(self):
#         if self.doc:
#             self.checklist_done = True
#         else:
#             self.checklist_done = False
    