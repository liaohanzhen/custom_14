# -*- coding: utf-8 -*-
#############################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
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
#############################################################################

from odoo import models, fields
from odoo.http import request
from odoo.tools.safe_eval import safe_eval
import logging
_logger = logging.getLogger(__name__)

class Website(models.Model):
    _inherit = 'website'

    mp_multi_step_signup = fields.Boolean(string="Enable")

    def get_active_register_groups(self):
        website_id = self.env['website'].get_current_website()
        if website_id:
            active_rec = self.env['seller.register.group'].sudo().search([
                ('website_id', '=', website_id.id),('reg_group_status', '=', True)])
            return active_rec
        return False
    
    def get_all_attributes_values(self, attribute_id):
        attr_values = {}
        attribute = self.env['seller.register.attributes'].browse(int(attribute_id))
        domain = attribute.attribute_domain or []
        obj_rel = attribute.sudo().get_attribute_obj_relation()

        if domain:
            domain = safe_eval(domain)
        objs = self.env[obj_rel].sudo().search(domain)
        if objs:
            for rec in objs:
                attribute_type = attribute.sudo().attribute
                if attribute_type.name.startswith('property_'):
                    attr_values[attribute_type.relation + ',' + str(rec.id)] = rec.name
                else:
                    attr_values[rec.id] = rec.name
        return attr_values
    

    def get_signup_attributes(self):
        signup_group_obj = self.get_active_register_groups()
        signup_group_dict = {}
        
        for signup_group in signup_group_obj:
            if signup_group and signup_group.attribute_ids:
                for attribute in signup_group.attribute_ids:
                    if attribute.attribute_status:
                        attribute_dict = {}
                        attr_name = attribute.attribute.name
                        attr_input_type = attribute.attribute_input_type
                        attribute_dict[attr_name] = {
                            'input_type': attribute.attribute_input_type,
                            'placeholder': attribute.placeholder or '',
                            'label': attribute.attribute_label or attribute.attribute.field_description or '',
                            'is_required': attribute.is_required,
                        }

                        if attr_input_type == 'selection':
                            attr_values = dict(request.env['res.partner']._fields[attr_name].selection)
                            attribute_dict[attr_name].update({'attr_values': attr_values})
                        if attr_input_type in ['selection_m2o', 'selection_m2m']:
                            attr_values = self.get_all_attributes_values(attribute.id)
                            attribute_dict[attr_name].update({'attr_values': attr_values})
                        if signup_group_dict.get(signup_group.name):
                            signup_group_dict[signup_group.name].update(attribute_dict)
                        else:
                            signup_group_dict[signup_group.name] = attribute_dict
        return signup_group_dict
