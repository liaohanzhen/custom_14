# -*- coding: utf-8 -*-
#################################################################################
#
#   Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   If not, see <https://store.webkul.com/license.html/>
#
#################################################################################

from odoo import api, fields, models, _

class ProductAttachment(models.Model):
    _name = 'product.attachment'
    _description = "Product Attachment"
    _order = "sequence, name"

    description = fields.Text('Description', required=True, translate=True)
    allowed_user = fields.Selection([('logged_in', 'Logged-in'), ('public', 'Public')], 'Allowed User', help="""
    > logged_in : To make the attachments not visible to not logged in customers.
    > public : To make the attachments visible to not logged in customers.    
    """)
    attachment_category = fields.Many2one('attachment.category', string="Attachment Category", help="Product Attachment Category")
    name = fields.Many2one('ir.attachment', help="Product Attachment")
    file_size = fields.Integer(related="name.file_size", string="File Size(KB)", readonly=True, store=True)
    downloads = fields.Integer('Downloads')
    product_temp_id = fields.Many2one('product.template', help="Product")
    sequence = fields.Integer(related='attachment_category.sequence', help="Gives the sequence order when displaying a list of attachment categories.")

    def update_attachment(self):
        partial = self.env['attachment.wizard'].create({
            'name':self.name.name,
            'attachment':self.name.datas,
            'attachment_category':self.attachment_category.id,
            'allowed_user':self.allowed_user,
            'description':self.description,
        })
        return {'name': "Update Product Attachment",
                'view_mode': 'form',
                'view_id': False,
                'view_type': 'form',
                'res_model': 'attachment.wizard',
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
