# -*- coding: utf-8 -*-

from odoo import models, fields

class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    allowed_group_ids = fields.Many2many('res.groups','res_groups_portal_task_access','task_id','group_id',string='Allowed Groups', help='Selected groups users can see the tasks in the portal.')
    allowed_user_ids = fields.Many2many('res.users','res_users_portal_task_access','task_id','user_id',string='Allowed Users', help='Selected users can see the tasks in the portal.')