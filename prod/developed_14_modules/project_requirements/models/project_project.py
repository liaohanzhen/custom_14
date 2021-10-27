# -*- coding: utf-8 -*-
from odoo import models,fields,api

class ProjectProject(models.Model):
    _inherit = 'project.project'
    
    @api.model
    def _search_is_project_manager(self,operator, operand):
        group_project_manager = self.env.ref('project.group_project_manager',False)
        user_groups = self.env.user.groups_id.ids
        if group_project_manager.id in user_groups:
            return []
        else:
            return [('id', 'in', [])]
        
    def _compute_is_project_manager(self):
        group = self.env.ref('project.group_project_manager',False)
        
        user_groups = self.env.user.groups_id.ids
        group_id = group.id
        for project in self:
            if group_id in user_groups:
                project.is_project_manager=True
            else:
                project.is_project_manager=False
        
            
    stage_template_id = fields.Many2one('project.task.type.template','Project Workflow')
    requirement_ids = fields.One2many('project.requirement','project_id',string='Project Requirements')
    project_template_id = fields.Many2one("project.template",'Project Template')
    is_project_manager = fields.Boolean('Is Project Manager?',compute=_compute_is_project_manager, search=_search_is_project_manager)
    
    
            
    
    @api.onchange('project_template_id')
    def onchange_project_template_id(self):
        if self.project_template_id:
            self.stage_template_id = self.project_template_id.stage_template_id.id
            self.project_type_id = self.project_template_id.project_type_id.id
            self.category_id = self.project_template_id.category_id.id
            
        
    @api.model
    def create(self, vals):
        if vals.get('stage_template_id'):
            template = self.env['project.task.type.template'].browse(vals.get('stage_template_id'))
            vals['type_ids'] = [(6,0,template.stage_ids.ids)]
        project = super(ProjectProject, self).create(vals)
        if vals.get('project_template_id'):
            template = project.project_template_id
            
            stage_template = project.stage_template_id or template.stage_template_id
            stage_ids = stage_template.stage_ids.ids
            defaul_vals = {'project_id': project.id,'project_tmpl_id':False,'stage_template_id':False}
            if stage_ids:
                defaul_vals.update({'stage_id':stage_ids[0]})
            for task in template.default_task_ids:
                defaul_vals.update({'name':task.name})
                task.copy(default=defaul_vals)
        return project
        
