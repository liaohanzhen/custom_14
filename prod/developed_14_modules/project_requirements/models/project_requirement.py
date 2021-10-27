# -*- coding: utf-8 -*-
from odoo import models,fields,api

class ProjectRequirement(models.Model):
    _name = 'project.requirement'
    
    name = fields.Char("Title", required=1)
    description = fields.Text("Description")
    project_id = fields.Many2one("project.project",string="Project")
    task_ids = fields.Many2many('project.task','project_requirement_task_rel','requirement_id','task_id',string="Tasks")
    