#################################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#################################################################################
from odoo import api, fields, models, _

class AttachmentWizard(models.TransientModel):
    _name = "attachment.wizard"
    _description = "Attachment Wizard"

    attachment = fields.Binary(
        string="Attachment", 
        required=True)
    name = fields.Char(
        string='Name')
    attachment_category = fields.Many2one('attachment.category', string="Attachment Category",required=True, help="Product Attachment Category")
    allowed_user = fields.Selection([('logged_in', 'Logged-in'), ('public', 'Public')], 'Allowed User', default="logged_in", help="""
    > logged_in : To make the attachments not visible to not logged in customers.
    > public : To make the attachments visible to not logged in customers.    
    """)
    description = fields.Text('Description', translate=True)

    def add_product_attachment(self):
        modelName = self._context.get('active_model')
        modelId = self._context.get('active_id')
        if modelName == 'product.attachment':
            attachmentObj = self.env['product.attachment'].browse(modelId)
            attachmentObj.write({
                'attachment_category':self.attachment_category.id,
                'description':self.description,
                'allowed_user':self.allowed_user,
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
                        #'datas_fname': self.name,
                        'res_name': attachName,
                    }
        attachmentModel = self.env['ir.attachment']
        res = attachmentModel.create(attachmentValue)
        active_id = self.env['product.attachment'].create({
            'name':res.id,
            'attachment_category':self.attachment_category.id,
            'description':self.description,
            'allowed_user':self.allowed_user,
            'product_temp_id':modelId,
        })
        return True