# -*- coding: utf-8 -*-
from odoo import models,fields,api

class SignatureWizard(models.TransientModel):
    _name = 'employee.signature.wizard'
    
    signature = fields.Binary("Signature")

#     @api.multi
#     def draw_signature(self):
#         ctx = self._context.copy()
#         record_id = ctx.get('record_id')
#         record_model = ctx.get('record_model')
#         record_field = ctx.get('record_field')
#         if record_id and record_model and record_field:
#             record = self.env[record_model].browse(record_id)
#             record.write({record_field:self.signature,'signed':True})
#             if record_model=='hr.employee.trainee':
#                 record.session_id.training_ids.filtered(lambda x:x.employee_id.id==record.employee_id.id).write({'employee_signature':self.signature,'signed_employee':True})
#                 signed = list(set(record.session_id.trainee_ids.mapped('signed')))
#                 if len(signed)==1 and signed[0]==True and record.session_id.trainer_signature:
#                     record.session_id.write({'state':'SIGNED'})
#                     action = self.env.ref('employee_training.action_training_session')
#                     result = action.read()[0]
#                     ctx = self._context.copy()
#                     ctx.update({'default_session_id':self.id})
#                     result['context'] = ctx
#                     result['res_id'] = record.session_id.id
#                     result['views'] = [(self.env.ref('employee_training.view_training_session_form').id, 'form')]
#                     return result
#             elif record_model=='training.session':
#                 record.training_ids.write({'trainer_signature':self.signature,'signed_trainer':True})
#                 signed = list(set(record.trainee_ids.mapped('signed')))
#                 if len(signed)==1 and signed[0]==True and record.trainer_signature:
#                     record.write({'state':'SIGNED'})
#                     
#         return True
    
#     @api.multi
    def draw_signature(self):
        ctx = self._context.copy()
        record_id = ctx.get('record_id')
        record_model = ctx.get('record_model')
        record_field = ctx.get('record_field')
        if record_id and record_model and record_field:
            record = self.env[record_model].browse(record_id)
            #record.write({record_field:self.signature,'signed':True})
            
#             if record_model=='hr.employee.trainee':
#                 record.session_id.training_ids.filtered(lambda x:x.employee_id.id==record.employee_id.id).write({'employee_signature':self.signature,'signed_employee':True})
#                 signed = list(set(record.session_id.trainee_ids.mapped('signed')))
#                 if len(signed)==1 and signed[0]==True and record.session_id.trainer_signature:
#                     record.session_id.write({'state':'SIGNED'})
#                     action = self.env.ref('employee_training.action_training_session')
#                     result = action.read()[0]
#                     ctx = self._context.copy()
#                     ctx.update({'default_session_id':self.id})
#                     result['context'] = ctx
#                     result['res_id'] = record.session_id.id
#                     result['views'] = [(self.env.ref('employee_training.view_training_session_form').id, 'form')]
#                     return result
            if record_model=='training.session':
                record.write({'trainer_signature':self.signature})
                
                record.training_ids.write({'trainer_signature':self.signature,'signed_trainer':True})
#                 signed = list(set(record.training_ids.mapped('signed_employee')))
#                 if len(signed)==1 and signed[0]==True and record.trainer_signature:
#                     record.write({'state':'SIGNED'})
                trainings = record.training_ids.filtered(lambda x:x.signed_employee or x.state=='Cancelled')
                if len(trainings)==len(record.training_ids) and record.trainer_signature:
                    record.write({'state':'SIGNED'})
            elif record_model=='training.training':
                record.write({'employee_signature':self.signature, 'signed_employee' : True,'state':'SIGNED'})
#                 signed = list(set(record.session_id.training_ids.mapped('signed_employee')))
#                 if len(signed)==1 and signed[0]==True and record.session_id.trainer_signature:
#                     record.session_id.write({'state':'SIGNED'})
                training_ids = record.session_id.training_ids
                trainings = training_ids.filtered(lambda x:x.signed_employee or x.state=='Cancelled')
                if len(trainings)==len(training_ids) and record.session_id.trainer_signature:
                    record.session_id.write({'state':'SIGNED'})
                
        return True