# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import models, api

class qualityCheck(models.Model):
    _inherit = 'quality.check'
    
    def do_pass_all(self):
        if self.picking_id:
            checks = self.picking_id.check_ids.filtered(lambda x: x.quality_state == 'none')
            checks.write({'quality_state': 'pass',
                    'user_id': self.env.user.id,
                    'control_date': datetime.now()})
        else:
            self.write({'quality_state': 'pass',
                    'user_id': self.env.user.id,
                    'control_date': datetime.now()})
        return {'type': 'ir.actions.act_window_close'}
    