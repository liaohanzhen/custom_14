# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.http import request

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    def getAttachmentCategories(self):
        res = super(ProductTemplate, self).getAttachmentCategories()
        if not res:
            res = {}
        categories = res.get('categories',[])
        pro_attachments = res.get('pro_attachments',[])
        for variant in self.product_variant_ids:
            var_res = variant.getAttachmentCategories(categories)
            if var_res:
                categories = var_res.get('categories')
                pro_attachments += var_res.get('pro_attachments')
        if categories or pro_attachments:
            res.update({'categories' : categories, 'pro_attachments' : pro_attachments})
                
        return res
    
class ProductProduct(models.Model):
    _inherit = "product.product"

    product_attachments = fields.One2many('product.attachment', 'product_id', string='Product Attachments')
    
    def getAttachmentCategories(self,categories = [], proAttachments = []):
        #categories, proAttachments = [], []
        attachments = self.product_attachments.sorted(key=lambda r: r.sequence)
        if not attachments:
            return {}
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
    
    