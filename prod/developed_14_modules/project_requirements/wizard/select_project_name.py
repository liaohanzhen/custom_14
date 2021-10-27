# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SelectProjectName(models.TransientModel):
    _name = 'select.project.name'
    
    name = fields.Char("Name",required=True)
    stage_template_id = fields.Many2one('project.task.type.template','Project stage template')
    project_type_id = fields.Many2one("project.project.type", string="Project Type")
    category_id = fields.Many2one("portfolio.category",string="Project Category")
    
    
    def create_project_template_from_project(self):
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        if active_id and active_model=='project.project':
            project_tmpl_obj = self.env['project.template']
            project = self.env[active_model].browse(active_id)
            stage_template = self.stage_template_id or project.stage_template_id
            vals ={
                'name': self.name or project.name,
                'stage_template_id' : stage_template.id or False,
                'project_type_id' : self.project_type_id.id or project.project_type_id.id or False,
                'category_id' : self.category_id.id or project.category_id.id or False,
                }
            template = project_tmpl_obj.create(vals)
            
            stage_ids = stage_template.stage_ids.ids
            
            default_vals = {'project_id':False,'project_tmpl_id':template.id, 'is_template':True, 'stage_template_id':stage_template.id}
            if stage_ids:
                default_vals.update({'stage_id':stage_ids[0]})
            for task in project.tasks:
                default_vals.update({'name':task.name})
                task.copy(default=default_vals)
        return True