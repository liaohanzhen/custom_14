# -*- coding: utf-8 -*-

from odoo import api, fields, models

class PortalUserAttachment(models.Model):
    _name = 'portal.user.attachment'
    _description = "Attachment"
    _order = "sequence, name"

    description = fields.Text('Description', required=True, translate=True)
#     allowed_user = fields.Selection([('logged_in', 'Logged-in'), ('public', 'Public'),('all','All')], 'Allowed User', help="""
#     > logged_in : To make the attachments not visible to not logged in customers.
#     > public : To make the attachments visible to not logged in customers.    
#     """)
    attachment_category = fields.Many2one('attachment.category', string="Attachment Category", help="Product Attachment Category")
    name = fields.Many2one('ir.attachment', help="Product Attachment")
    file_size = fields.Integer(related="name.file_size", string="File Size(KB)", readonly=True, store=True)
    downloads = fields.Integer('Downloads')
    #product_temp_id = fields.Many2one('product.template', help="Product")
    sequence = fields.Integer(related='attachment_category.sequence', help="Gives the sequence order when displaying a list of attachment categories.", store=True)
    res_model = fields.Char('Resource Model', readonly=True, help="The database object this attachment will be attached to.")
    res_id = fields.Integer('Resource ID', readonly=True, help="The record id this is attached to.")
    #portal_attachment_ids = fields.One2many('portal.user.attachment', 'res_id', domain=lambda self:[('res_model', '=', self._name)], string='Attachments')
    group_ids = fields.Many2many('res.groups','res_groups_portal_attachments','attachment_id','group_id',string='Allowed Groups', help='Selected groups users can see the documents in the portal. If no groups selected, than its shown to all user.')
    user_ids = fields.Many2many('res.users','res_users_portal_attachments','attachment_id','user_id',string='Allowed Users', help='Selected users can see the documents in the portal. If no users selected, than its shown to all user.')
    
    def update_attachment(self):
        partial = self.env['portal.attachment.wizard'].create({
            'name':self.name.name,
            'attachment':self.name.datas,
            'attachment_category':self.attachment_category.id,
            #'allowed_user':self.allowed_user,
            'description':self.description,
            'group_ids' : [(6,0,self.group_ids.ids)],
            'user_ids' : [(6,0,self.user_ids.ids)],
        })
        return {'name': "Update Attachment",
                'view_mode': 'form',
                'view_id': False,
                'view_type': 'form',
                'res_model': 'portal.attachment.wizard',
                'res_id': partial.id,
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'domain': '[]',
                }
    
    def delete_attachment(self):
        for obj in self:
            obj.name.unlink()
            obj.unlink()
        return True
