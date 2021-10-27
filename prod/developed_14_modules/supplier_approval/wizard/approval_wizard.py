# -*- coding: utf-8 -*-
from odoo import models,fields, api
from datetime import datetime

class ParnterApprovalWizard(models.TransientModel):
    _name='partner.approval.wizard'
    
    name = fields.Char('Reason')
    partner_id = fields.Many2one('res.partner','Partner')
    
    def approve_disapprove_supplier(self):
        flag = not self.partner_id.approved_supplier
        partners = self.partner_id+self.partner_id.child_ids
        partners.write({'approved_supplier':flag, 'approved_supplier_tmp':flag})
#         self.partner_id.approved_supplier = flag
#         self.partner_id.approved_supplier_tmp = flag
#         self.partner_id.child_ids
        
        
        if self.partner_id.approved_supplier: #self._context.get('approve_press')
#             self.partner_id.approved_supplier=True
#             self.partner_id.approved_supplier_tmp = True
            status = 'Accepted'
        else:
#             self.partner_id.approved_supplier=False
#             self.partner_id.approved_supplier_tmp = False
            status = 'Not Accepted'
        for partner in partners:    
            self.env['res.partner.approval.history'].create({'partner_id':partner.id,'date':datetime.now(),'user_id':self._uid,'status':status,'reason':self.name})
        
        return {'type': 'ir.actions.act_window_close'}