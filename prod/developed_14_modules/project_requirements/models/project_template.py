# -*- coding: utf-8 -*-

from odoo import models, fields, api

class project_template_task(models.Model):
    _inherit = "project.task.type"

    project_check = fields.Boolean(string="Project Check")
    stage_template_ids = fields.Many2many("project.task.type.template",'project_task_type_template_relation','stage_id', 'template_id','Stage Templates')
    
class project_template(models.Model):
    _name = "project.template"
    
    name = fields.Char("Name")
    stage_template_id = fields.Many2one('project.task.type.template','Project stage template')
    project_type_id = fields.Many2one("project.project.type", string="Project Type")
    category_id = fields.Many2one("portfolio.category",string="Project Category")
    default_task_ids = fields.One2many('project.task', 'project_tmpl_id', string="Task Activities")
    
    @api.model
    def create(self, vals):
        stage_template_id = vals.get('stage_template_id')
        if vals.get('default_task_ids') and stage_template_id:
            stage_template = self.env['project.task.type.template'].browse(stage_template_id)
            stage_ids = stage_template.stage_ids.ids
            if stage_ids:
                for v in vals['default_task_ids']:
                    if len(v)>=2 and v[0]==0 and not v[2].get('state_id'):
                        v[2].update({'stage_id':stage_ids[0]})
        return super(project_template, self).create(vals)
        
    def write(self, vals):
        if vals.get('default_task_ids'):
            original_task_vals = list(vals['default_task_ids'])
            for template in self:
                stage_ids = template.stage_template_id.stage_ids.ids
                if stage_ids:
                    for v in vals['default_task_ids']:
                        if len(v)>=2 and v[0]==0 and not v[2].get('state_id'):
                            v[2].update({'stage_id':stage_ids[0]})
                res = super(project_template, template).write(vals)
                vals['default_task_ids'] = original_task_vals
        #res = super(project_template, self).write(vals)
        return True