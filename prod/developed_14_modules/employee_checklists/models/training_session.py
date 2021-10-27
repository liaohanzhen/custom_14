# -*- coding: utf-8 -*-
from odoo import models,fields,api, _

class TrainingSession(models.Model):
    _inherit = 'training.session'
    
    employee_checklist_item_ids = fields.One2many('hr.employee.checklists.item','training_session_id','Checklist Items')
    
#     @api.multi
    def write(self, vals):
        res = super(TrainingSession, self).write(vals)
        if vals.get('state'):
            for session in self:
                if session.employee_checklist_item_ids:
                    new_vals = {'description':session.state}
                    if session.state=='DONE':
                        new_vals.update({'checklist_done':True,'user_id': self._uid,'date': fields.Date.context_today(self)})
                    session.sudo().employee_checklist_item_ids.write(new_vals)
        return res