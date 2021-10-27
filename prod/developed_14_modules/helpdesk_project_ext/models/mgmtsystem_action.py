# -*- coding: utf-8 -*-
from odoo import models,fields

class MgmtsystemAction(models.Model):
    _inherit = 'mgmtsystem.action'
    
    ticket_id = fields.Many2one('helpdesk.ticket',string='Ticket', copy=False)
