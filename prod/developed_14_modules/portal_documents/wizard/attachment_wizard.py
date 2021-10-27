# -*- coding: utf-8 -*-

from odoo import api, fields, models

class PortalAttachmentWizard(models.TransientModel):
    _name = "portal.attachment.wizard"
    _description = "Portal Attachment Wizard"

    attachment = fields.Binary(
        string="Attachment", 
        required=True)
    name = fields.Char(
        string='Name')
    attachment_category = fields.Many2one('attachment.category', string="Attachment Category", help="Attachment Category", required=True)
#     allowed_user = fields.Selection([('logged_in', 'Logged-in'), ('public', 'Public')], 'Allowed User', default="logged_in", help="""
#     > logged_in : To make the attachments not visible to not logged in customers.
#     > public : To make the attachments visible to not logged in customers.    
#     """)
    description = fields.Text('Description', translate=True)
    group_ids = fields.Many2many('res.groups','res_groups_portal_attachments_wizard','att_wizard_id','group_id',string='Allowed Groups', help='Selected groups users can see the documents in the portal. If no groups selected, than its shown to all user.')
    user_ids = fields.Many2many('res.users','res_users_portal_attachments_wizard','att_wizard_id','user_id',string='Allowed Users', help='Selected users can see the documents in the portal. If no users selected, than its shown to all user.')
    
    def add_portal_attachment(self):
        modelName = self._context.get('active_model')
        modelId = self._context.get('active_id')
        if modelName == 'portal.user.attachment':
            attachmentObj = self.env['portal.user.attachment'].browse(modelId)
            attachmentObj.write({
                'attachment_category':self.attachment_category.id,
                'description':self.description,
                #'allowed_user':self.allowed_user,
                'group_ids' : [(6,0,self.group_ids.ids)],
                'user_ids' : [(6,0,self.user_ids.ids)],
            })
            return True
        attachName = self.name
        attachName = attachName.encode('ascii', 'ignore').decode('ascii') if attachName else ''
        attachmentValue = {
                        'name': self.name,
                        'datas': self.attachment,
                        'res_model': modelName,
                        'res_id': modelId,
                        'type': 'binary',
                        'db_datas': attachName,
#                         'datas_fname': self.name,
                        'res_name': attachName,
                    }
        attachmentModel = self.env['ir.attachment']
        res = attachmentModel.create(attachmentValue)
        self.env['portal.user.attachment'].create({
            'name':res.id,
            'attachment_category':self.attachment_category.id,
            'description':self.description,
            #'allowed_user':self.allowed_user,
            'res_id':modelId,
            'res_model': modelName,
            'group_ids' : [(6,0,self.group_ids.ids)],
            'user_ids' : [(6,0,self.user_ids.ids)],
        })
        return True