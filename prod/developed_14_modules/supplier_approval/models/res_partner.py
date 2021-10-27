# -*- coding: utf-8 -*-

from odoo import models,api, fields,_

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    approved_supplier = fields.Boolean("Approved Supplier")
    approved_supplier_tmp = fields.Boolean("Approved Supplier Temp")
    approval_history_ids = fields.One2many('res.partner.approval.history','partner_id',string='Approval History')
    
    def approve_disapprove_supplier(self):
        form = self.env.ref("supplier_approval.view_partner_approval_wizard_form",False)
        ctx = self._context.copy()
        flag = not self.approved_supplier
        ctx.update({'default_partner_id':self.id,'flag':flag})
#         if ctx.get('approve_press'):
#             ctx.update({'button_name':'Approved'})
#         else:
#             ctx.update({'button_name':'Not Approved'})
        return {
                'name': _('Approval/Not Approval'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'partner.approval.wizard',
                'view_id': form.id,
                'type': 'ir.actions.act_window',
                'context': ctx,
                'target': 'new'
            }
    
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not args:
            args = []
        if not self.user_has_groups('purchase.group_purchase_manager'):
            args += [['approved_supplier', '=', True]]
        res = super(ResPartner, self).name_search(name, args, operator, limit)
        return res
            
class ResPartnerApprovalHistory(models.Model):
    _name = 'res.partner.approval.history'
    
    date = fields.Datetime("Date")
    status = fields.Selection([('Accepted','Accepted'),('Not Accepted','Not Accepted')],string="Status")
    user_id = fields.Many2one('res.users','User')
    reason = fields.Char("Reason")
    partner_id = fields.Many2one("res.partner",'Supplier',domain=[('supplier','=',True)])
    
    
    
    
    