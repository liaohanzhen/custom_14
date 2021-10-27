# -*- coding: utf-8 -*-
from collections import OrderedDict

from odoo import fields, models

    

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    
    def _prepare_categories_for_display(self):
        """On the comparison page group on the same line the values of each
        product that concern the same attributes, and then group those
        attributes per category.

        The returned categories are ordered following their default order.

        :return: OrderedDict [{
            product.attribute.category: OrderedDict [{
                product.attribute: OrderedDict [{
                    product: [product.template.attribute.value]
                }]
            }]
        }]
        """
        #attributes = self.product_tmpl_id.valid_product_template_attribute_line_ids._without_no_variant_attributes().attribute_id.sorted()
        attributes = self.product_tmpl_id.valid_product_template_attribute_line_ids.attribute_id.sorted()
        categories = OrderedDict([(cat, OrderedDict()) for cat in attributes.category_id.sorted()])
        if any(not pa.category_id for pa in attributes):
            # category_id is not required and the mapped does not return empty
            categories[self.env['product.attribute.category']] = OrderedDict()
        for pa in attributes:
            data = []
            for product in self:
                if pa.create_variant == 'no_variant':
                    tmpl_val_line = product.product_tmpl_id.valid_product_template_attribute_line_ids.filtered(lambda x: x.attribute_id==pa)
                    data.append((product,tmpl_val_line and tmpl_val_line[0].value_ids[0] or product.product_template_attribute_value_ids.filtered(lambda ptav: ptav.attribute_id == pa)))
                else:
                    data.append((product,product.product_template_attribute_value_ids.filtered(lambda ptav: ptav.attribute_id == pa)))
            categories[pa.category_id][pa] = OrderedDict(data)
            
        # for pa in attributes:
            # categories[pa.category_id][pa] = OrderedDict([(
                # product,
                # product.product_template_attribute_value_ids.filtered(lambda ptav: ptav.attribute_id == pa)
            # ) for product in self])
            
        print(categories)
        return categories
    
    



    
    