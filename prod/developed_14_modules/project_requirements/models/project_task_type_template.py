# -*- coding: utf-8 -*-
from odoo import models,fields

class ProjectTaskTypeTemplate(models.Model):
    _name = 'project.task.type.template'
    
    name = fields.Char("Name", required=1)
    stage_ids = fields.Many2many("project.task.type",'project_task_type_template_relation','template_id','stage_id','Stages')
