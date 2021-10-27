# -*- coding: utf-8 -*-
from odoo import models,fields,api

class HrEmployeeChecklistItems(models.Model):
    _name='hr.employee.checklists.item'
    
    checklist_done = fields.Boolean("Checklist")
    checklist_type = fields.Selection([('INFO','INFO'),('ACTION','ACTION'),('DOC','DOC'),('TICKET','TICKET'),('TRAINING','TRAINING')],string='Type')
    related_field_id = fields.Many2one("ir.model.fields",domain=[('model_id.model','=','hr.employee'),('ttype','in',['text','char']),('name','!=','display_name'),('store','=',True)],string='Related Field')
    training_session_id = fields.Many2one("training.session", "Training Session")
    #related_field_project_id = fields.Many2one("project.base.field.value",string='Related Field Project')
    ticket_id = fields.Many2one("helpdesk.ticket",'Ticket')
    doc = fields.Binary("File Name")
    file_name = fields.Char("Filename")
    description = fields.Char("Description")
    responsible = fields.Many2one("res.users",'Responsible')
    user_id = fields.Many2one("res.users",'User')
    date = fields.Date("Date")
    employee_id = fields.Many2one("hr.employee",'Onboarding Checklist Employee')
    offboarding_employee_id = fields.Many2one("hr.employee",'Offboarding Checkilist Employee')
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
    
    @api.onchange('related_field_id')
    def onchange_related_field_employee_id(self):
        if self.related_field_id and self.employee_id: # and self.task_id.project_id:
            self.description = getattr(self.employee_id,self.related_field_id.name)
        elif self.related_field_id and self.offboarding_employee_id:
            self.description = getattr(self.offboarding_employee_id,self.related_field_id.name)
            
#         if self.related_field_project_id:
#             self.description = self.related_field_project_id.value    
    
    @api.model
    def create(self,vals):
        res = super(HrEmployeeChecklistItems,self).create(vals)
#         if res.checklist_type=='INFO' and res.related_field_project_id and res.description:
#             res.related_field_project_id.write({'value':res.description})
        if res.checklist_type=='INFO' and res.related_field_id and res.employee_id:
            res.employee_id.write({res.related_field_id.name:res.description})
        elif res.checklist_type=='INFO' and res.related_field_id and res.offboarding_employee_id:
            res.offboarding_employee_id.write({res.related_field_id.name:res.description})
            
        if vals.get("doc") and (res.employee_id or res.offboarding_employee_id) :
            self.env['ir.attachment'].create({'name':res.file_name,'datas':res.doc,'type':'binary', 'res_model':'hr.employee','res_id':res.employee_id and res.employee_id.id or res.offboarding_employee_id.id, 'datas_fname' : res.file_name})
        return res
    
#     @api.multi
    def write(self,vals):
        res = super(HrEmployeeChecklistItems,self).write(vals)
        if vals.get('description','') or vals.get("doc"):
            for checklist in self:
                if vals.get('description','') and checklist.checklist_type =='INFO' and checklist.employee_id and checklist.related_field_id:
                    checklist.employee_id.write({checklist.related_field_id.name:checklist.description})
                elif vals.get('description','') and checklist.checklist_type  == 'INFO' and checklist.offboarding_employee_id and checklist.related_field_id:
                    checklist.offboarding_employee_id.write({checklist.related_field_id.name:checklist.description})
                if vals.get("doc") and (checklist.employee_id or res.offboarding_employee_id):
                    self.env['ir.attachment'].create({'name':checklist.file_name,'datas':checklist.doc,'type':'binary', 'res_model':'hr.employee','res_id':checklist.employee_id and checklist.employee_id.id or res.offboarding_employee_id.id, 'datas_fname' : checklist.file_name})
        return res
    
    @api.onchange('checklist_type','description','doc')
    def onchange_checklist_type(self):
        if self.checklist_type=='INFO' and self.description:
            self.checklist_done = True
        elif self.doc:
            self.checklist_done = True
    
    @api.onchange('checklist_done')
    def onchange_checklist_done(self):
        if self.checklist_done:
            self.user_id=self._uid
            self.date = fields.Date.context_today(self)
        else:
            self.user_id = False
            self.date = False
    
    @api.onchange('training_session_id')
    def onchange_training_session_id(self):
        if self.training_session_id:
            self.description=self.training_session_id.state
            if self.training_session_id.state=='DONE':
                self.checklist_done = True
            else:
                self.checklist_done = False
                
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
    