# -*- coding: utf-8 -*-
from odoo import models, api, fields
import time
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class SignRequest(models.Model):
    _inherit = "sign.request"
    
    signature_subject = fields.Char("Signature Request Subject")
    signature_message = fields.Text("Signature Request Message")
        
#     @api.one
    def set_signers(self, signers):
        self.request_item_ids.filtered(lambda r: not r.partner_id or not r.role_id).unlink()
        ids_to_remove = []
        for request_item in self.request_item_ids:
            for i in range(0, len(signers)):
                if signers[i]['partner_id'] == request_item.partner_id.id and signers[i]['role'] == request_item.role_id.id:
                    signers.pop(i)
                    break
            else:
                ids_to_remove.append(request_item.id)

        SignRequestItem = self.env['sign.request.item']
        SignRequestItem.browse(ids_to_remove).unlink()
        for signer in signers:
            sequence = signer.get('sequence')
            SignRequestItem.create({
                'partner_id': signer['partner_id'],
                'sequence': sequence,
                'sign_request_id': self.id,
                'role_id': signer['role']
            })
        
    @api.model
    def initialize_new(self, id, signers, followers, reference, subject, message, send=True, without_mail=False):
        sign_request = self.create({'template_id': id, 
                                    'reference': reference, 
                                    'favorited_ids': [(4, self.env.user.id)],
                                    'signature_subject':subject,
                                    'signature_message' :message})
        sign_request.message_subscribe(partner_ids=followers)
        sign_request.set_signers(signers)
        
        if send:
            no_sign_needed = sign_request.request_item_ids.filtered(lambda x:not x.partner_id or not x.partner_id.email)
            if no_sign_needed:
                no_sign_needed.write({'state':'sent'})
            request_items = sign_request.request_item_ids.filtered(lambda r: r.partner_id.id not in no_sign_needed.ids or r.state=='draft')
            sequences = request_items.mapped('sequence')
            if sequences:
                sequences.sort()
                request_items = request_items.filtered(lambda x:x.sequence==sequences[0])
                request_items.send_signature_accesses(subject, message)
                request_items.write({'state':'sent'})
                sign_request.write({'state': 'sent'})
            else:
                sign_request.action_sent(subject, message) 
            
            followers = sign_request.message_follower_ids.mapped('partner_id')
            followers -= sign_request.create_uid.partner_id
            followers -= sign_request.request_item_ids.mapped('partner_id')
            if followers:
                sign_request.send_follower_accesses(followers, subject, message)  
            #signature_request.action_sent(subject, message)
            #sign_request._message_post(_('Waiting for signatures.'), type='comment', subtype='mt_comment')
        
        sign_token = sign_request.request_item_ids.filtered(lambda r: r.partner_id == self.env.user.partner_id)
        access_token = ''
        if sign_token:
            access_token = sign_token[0].access_token
        return {
            'id': sign_request.id,
            'token': sign_request.access_token,
            'sign_token': access_token, #signature_request.request_item_ids.filtered(lambda r: r.partner_id == self.env.user.partner_id).access_token,
        }
        
class SignRequestItem(models.Model):
    _inherit = "sign.request.item"
    
    sequence = fields.Integer("Sequence")
    
#     @api.multi
    def action_completed(self):
        self.write({'signing_date': time.strftime(DEFAULT_SERVER_DATE_FORMAT), 'state': 'completed'})
        
        signature_request = self.mapped('sign_request_id')
        request_items = signature_request.request_item_ids.filtered(lambda x:x.sequence==self.sequence)
        state = list(set(request_items.mapped('state')))
        if len(state)==1 and state[0]=='completed':
            request_items = signature_request.request_item_ids.filtered(lambda r: not r.partner_id or r.state=='draft')
            sequences = request_items.mapped('sequence')
            if sequences:
                sequences.sort()
                request_items = request_items.filtered(lambda x:x.sequence==sequences[0])
                request_items.send_signature_accesses(signature_request.signature_subject, signature_request.signature_message)
                request_items.write({'state':'sent'})
                if signature_request.nb_closed == len(signature_request.request_item_ids) and len(signature_request.request_item_ids) > 0:
                    signature_request._check_after_compute()

            else:
                signature_request._check_after_compute()    