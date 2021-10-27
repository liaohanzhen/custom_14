# -*- coding: utf-8 -*-
##########################################################################
#
#	Copyright (c) 2015-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>)
#   See LICENSE file for full copyright and licensing details.
#   "License URL : <https://store.webkul.com/license.html/>"
#
##########################################################################

from odoo import api, fields, models, _
from odoo.http import request

class ProductTemplate(models.Model):
    _inherit = "product.template"

    product_attachments = fields.One2many(
        'product.attachment', 'product_temp_id', string='Product Attachments')

    def getAttachmentCategories(self):
        categories, proAttachments = [], []
        attachments = self.product_attachments.sorted(key=lambda r: r.sequence)
        if not attachments:
            return False
        if request.env.user.id == request.website.user_id.id:
            for obj in attachments:
                if obj.allowed_user == 'public':
                    proAttachments.append(obj)
                    name = obj.attachment_category.name
                    if name not in categories:
                        categories.append(name)
        else:
            for obj in attachments:
                name = obj.attachment_category.name
                if name not in categories:
                    categories.append(name)
        proAttachments = proAttachments if proAttachments else attachments
        return {"categories":categories, "pro_attachments":proAttachments}
