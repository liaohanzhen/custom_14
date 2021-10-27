# -*- coding: utf-8 -*-
from odoo import api, models

class AttachmentWizard(models.TransientModel):
    _inherit = "attachment.wizard"

    def add_product_attachment(self):
        modelName = self._context.get('active_model')
        modelId = self._context.get('active_id')
        if modelName != 'product.product':
            return super(AttachmentWizard, self).add_product_attachment()
            
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
        active_id = self.env['product.attachment'].create({
            'name':res.id,
            'attachment_category':self.attachment_category.id,
            'description':self.description,
            'allowed_user':self.allowed_user,
            'product_id':modelId,
        })
        return True
    