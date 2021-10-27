# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from collections import defaultdict

Sequence = map(lambda x:(str(x),str(x)),range(1,101))

class SignSendRequest(models.TransientModel):
    _inherit = 'sign.send.request'
    
    sequence_ids = fields.One2many('sign.send.sequence','request_id', string="Sequences")
    
    @api.model
    def default_get(self, fields_list):
        res = super(SignSendRequest, self).default_get(fields_list)
        if res:
            template = self.env['sign.template'].browse(res['template_id'])
            roles = template.mapped('sign_item_ids.responsible_id')
            sequence_obj = self.env['sign.send.sequence']
            seq_ids =[]
            for index in range(1,len(roles)+1):
                seq = sequence_obj.create({'name': index})
                seq_ids.append(seq.id)
            res['sequence_ids'] = [(6,0,seq_ids)]#[(0, 0, {'name': index,}) for index in range(1,len(roles)+1)]
        return res
    
    def create_request(self, send=True, without_mail=False):
        template_id = self.template_id.id
        if self.signers_count:
            signers = [{'partner_id': signer.partner_id.id, 'role': signer.role_id.id,'sequence': signer.seq_id.name or 0} for signer in self.signer_ids]
        else:
            signers = [{'partner_id': self.signer_id.id, 'role': False,'sequence':0}]
        followers = self.follower_ids.ids
        reference = self.filename
        subject = self.subject
        message = self.message
        return self.env['sign.request'].initialize_new(template_id, signers, followers, reference, subject, message, send, without_mail)
            
    def send_request(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Confirm Signature Sequence/Stages'),
            'view_mode': 'form',
            'res_model': 'sign.send.sequence.dialog',
            'context' : {'default_sign_request_id':self.id},
            'target' : 'new'
        }
        

class SignSendSequenceDialog(models.TransientModel):
    _name = "sign.send.sequence.dialog"
    
    data_html = fields.Html("Flow Dialog")
    sign_request_id = fields.Many2one("sign.send.request",'Sign Request')
    
    @api.model
    def default_get(self, fields_list):
        res = super(SignSendSequenceDialog, self).default_get(fields_list)
        sign_request_id = self._context.get('default_sign_request_id')
        if sign_request_id:
            sign_request = self.env['sign.send.request'].browse(sign_request_id)
            
            signers = defaultdict(self.env['sign.send.request.signer'].browse)
            for signer in sign_request.signer_ids:
                signers[signer.seq_id.name] |= signer
            
            signer_sequences = sorted(signers.keys())
            all_buttons = ""
            for seq in signer_sequences:
                bt_data = """<button type="button" style="color: white;background-color: #7F7F7F;" class="btn  disabled">"""
                signs = signers[seq]
                for s in signs:
                    bt_data+="<span>%s</span>"%(s.partner_id.name)
                bt_data += "</button>"
                all_buttons += bt_data
            data = """
            <div class="form-horizontal">
                <div class="o_sign_request_signers_sequence">
                    %s
                </div>
                <hr/>
            </div>"""%(all_buttons)
            res['data_html'] = data
        return res
    
    def send_request(self):
        res = self.sign_request_id.create_request()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Signature(s)'),
            'view_mode': 'form',
            'res_model': 'sign.request',
            'res_id': res['id']
        }
        
class SignSendSequence(models.TransientModel):
    _name = "sign.send.sequence"
    
    name = fields.Integer("Sequence")
    request_id = fields.Many2one('sign.send.request')
    
class SignSendRequestSigner(models.TransientModel):
    _inherit = "sign.send.request.signer"
    
    seq_id = fields.Many2one('sign.send.sequence','Sequence')
    partner_id = fields.Many2one('res.partner', required=False)