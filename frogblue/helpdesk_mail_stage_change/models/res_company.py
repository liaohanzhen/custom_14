
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"
    
    auto_move_tickets_to_new_stage = fields.Boolean('Automatically move tickets to a new stage when mail is received')
    stagechange_source_stage = fields.Many2many('helpdesk.stage',string='Source Stage/s')
    stagechange_destination_stage = fields.Many2one('helpdesk.stage','Destination Stage')
    