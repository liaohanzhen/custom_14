# -*- coding: utf-8 -*-

from odoo import models, api, fields

class AssignContractWizard(models.TransientModel):
    _name = 'assign.contract.wizard'
    
    employee_id = fields.Many2one('hr.employee',"Employee",)
    contract_id = fields.Many2one('hr.contract',"Contract",)
    partner_ids = fields.Many2many('res.partner',string='Contacts')
    
#     @api.model
#     def default_get(self,fields_list):
#         res = super(AssignContractWizard, self).default_get(fields_list)
#         active_id = self._context.get('active_id')
#         active_model = self._context.get('active_model')
#         if active_model=='signature.request' and active_id:
#             sign_request = self.env[active_model].browse(active_id)
#             partners = sign_request.request_item_ids.mapped('partner_id')
#             #users = self.env['res.users'].sudo().search([('partner_id','in',partners.ids)])
#             #employees = self.env['hr.employee'].search([('user_id','in', users.ids)])
#             res['partner_ids'] = [(6, 0, partners.ids)]
#             
#         return res
        
    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            self.contract_id = self.employee_id.contract_id
        
#     @api.multi
    def action_assign_contract(self):
        active_id = self._context.get('active_id')
        active_model = self._context.get('active_model')
        if active_model=='sign.request' and active_id:
            sign_request = self.env[active_model].browse(active_id)
            if not sign_request.completed_document:
                sign_request.generate_completed_document()
            
            filename = sign_request.reference
#             if filename != sign_request.template_id.attachment_id.datas_fname:
#                 filename += sign_request.template_id.attachment_id.datas_fname[sign_request.template_id.attachment_id.datas_fname.rfind('.'):]
            user = self.env.user
            vals = dict(
                name=filename,
#                 datas_fname=filename,
                type='binary',
                datas=sign_request.completed_document,
                company_id=user.company_id.id,
                res_id = self.contract_id.id,
                res_model = self.contract_id._name, 
                )
            self.env['ir.attachment'].create(vals)
            
            str_message = '<p>Document <b>%s</b> attached from ODOO eSignature App by <b>%s</b></p>'%(filename,user.name) # on <b>%s</b> ,datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
            self.contract_id.message_post(body=str_message)
            
            str_message = '<p>Completed PDF document attached to <b>%s/%s - %s</b></p>'%(self.employee_id.name, self.contract_id.id,self.contract_id.name)
            sign_request.message_post(body=str_message)
        return True
    