# -*- coding: utf-8 -*-

from odoo import models,fields

class MrpECO(models.Model):
    _inherit = 'mrp.eco'
    
    ticket_id = fields.Many2one('helpdesk.ticket',string='Ticket', copy=False)