# -*- coding: utf-8 -*-
from odoo import models,fields,api

class IrModelFields(models.Model):
    _inherit = 'ir.model.fields'
    
    project_field_type = fields.Selection([('char','char'),('text','text')],string="Field Type")
    is_project_custom_field = fields.Boolean("Is Project Custom Field", defaul=False)
    
    @api.onchange('project_field_type')
    def onchange_project_field_type(self):
        if self.project_field_type:
            self.ttype = self.project_field_type
            
    def action_save_custom_field(self):
        return {'type': 'ir.actions.client', 'tag': 'reload'}
    
    def action_save_and_new_custom_field(self):
        form = self.env.ref("project_checklists.view_model_fields_form_project_project",False)
        ctx = self._context.copy()
#         project_model = self.env.ref('project.model_project_project',False)
        ctx.update({'default_model_id':self.model_id.id,'default_is_project_custom_field':True, 'default_project_field_type':'char'})
#         if project_model:
#             ctx.update({'default_model_id':self.model_id.id})
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ir.model.fields',
            'views': [(form.id, 'form')],
            'view_id': form.id,
            'target': 'new',
            'context': ctx,
        }
    
    def name_get(self):
        ctx = self._context.copy()
        res = []
        if ctx.get('show_field_name_only'):
            for record in self:
                res.append((record.id, record.field_description))
            return res
        return super(IrModelFields, self).name_get()
    