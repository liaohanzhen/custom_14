# -*- coding: utf-8 -*-
from odoo import models,fields, api

class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    def _get_default_stage_id(self):
        """ Gives default stage_id """
        project_id = self.env.context.get('default_project_id')
        if not project_id:
            stage_template_id = self.env.context.get('default_stage_template_id')
            if not stage_template_id:
                return False
            else:
                stage_template = self.env['project.task.type.template'].browse(stage_template_id)
                stage_id = stage_template.stage_ids and stage_template.stage_ids[0].id or False 
                return stage_id
        return self.stage_find(project_id, [('fold', '=', False)])
    
    requirement_ids = fields.Many2many('project.requirement','project_requirement_task_rel','task_id','requirement_id',string='Project Requirements')
    is_template = fields.Boolean("Is Template Task ?",default=False, copy=False)
    project_tmpl_id = fields.Many2one("project.template",'Project Template')
    stage_template_id = fields.Many2one('project.task.type.template', string='Project stage template')
    stage_id = fields.Many2one('project.task.type', string='Stage', track_visibility='onchange', index=True,
        default=_get_default_stage_id, group_expand='_read_group_stage_ids',
        domain="[('project_ids', '!=', False),('project_ids', '=', project_id)]", copy=False)
    #domain="['|','&',('project_ids', '!=', False),('project_ids', '=', project_id), (),('stage_template_ids','=',stage_template_id)]"

    @api.onchange('is_template')
    def onchange_is_template(self):
        res={}
        if self.is_template:
            domain = {'stage_id': [('stage_template_ids', '=', self.stage_template_id.id)]}
            res['domain'] = domain
        return res