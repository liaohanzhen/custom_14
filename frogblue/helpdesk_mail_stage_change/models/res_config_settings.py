# -*- coding: utf-8 -*-

from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    auto_move_tickets_to_new_stage = fields.Boolean('Automatically move tickets to a new stage when mail is received',related="company_id.auto_move_tickets_to_new_stage", readonly=False,)
    stagechange_source_stage = fields.Many2many('helpdesk.stage',string='Source Stage/s',related="company_id.stagechange_source_stage", readonly=False,
                                                help='Please select the Stages from which a ticket should be moved to another stage, if and when a mail is received.')
    stagechange_destination_stage = fields.Many2one('helpdesk.stage','Destination Stage',related="company_id.stagechange_destination_stage", readonly=False,
                                                    help='Please select the stage to which tickets should be move when a mail is received.')
    