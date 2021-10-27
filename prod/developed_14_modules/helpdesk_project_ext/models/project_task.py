# -*- coding: utf-8 -*-
from odoo import models,fields

class ProjectTask(models.Model):
    _inherit = 'project.task'
    
    ticket_id = fields.Many2one('helpdesk.ticket',string='Ticket', copy=False)
