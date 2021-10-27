# -*- coding: utf-8 -*-
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

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

SIGNUP_ATTRIBUTE_TYPES = [
    'char',
    'integer',
    'float',
    'boolean',
    'text',
    'selection',
    'many2one',
    'many2many',
]

ATTRIBUTE_INPUT_TYPE = [
    ('char', 'text'),
    ('integer', 'number'),
    ('float', 'float'),
    ('boolean', 'checkbox'),
    ('text', 'textarea'),
    ('selection', 'selection'),
    ('many2one', 'selection_m2o'),
    ('many2many', 'selection_m2m'),
]
class SellerRegisterGroup(models.Model):
    _name = "seller.register.group"
    _description = "Seller Registration Group"
    _order = "sequence"

    _sql_constraints = [('unique_name', 'unique(name)', 'Group already exist')]

    name = fields.Char(string="Name")
    reg_group_status = fields.Boolean(string="Registration Group Status")
    sequence = fields.Integer(string="Registration Group Sequence")
    attribute_ids = fields.One2many(comodel_name="seller.register.attributes", inverse_name="group_id", string="Attributes")

    def toggle_active(self):
        for rec in self:
            rec.reg_group_status = not rec.reg_group_status

    @api.model
    def get_active_website_setting(self, website_id):
        active_rec = self.search([('website_id','=',int(website_id)),('active','=',True)], limit=1)
        return active_rec

    def _default_website(self):
        return self.env['website'].search([
            ('company_id', '=', self.env.user.company_id.id)],
            limit=1,
        )

    website_id = fields.Many2one('website',
        string= "Website",
        default= _default_website,
        ondelete= 'cascade',
        required= True,
        )


class SellerRegisterAttributes(models.Model):
    _name = "seller.register.attributes"
    _description = "Seller Registration Attributes"
    _order = "sequence"
    _rec_name = "attribute"

    attribute = fields.Many2one("ir.model.fields", "Signup Attribute", size=32,
        required=True, help="Associated attribute in the SignUp form.",
        domain="[('model', 'in', ['res.partner']),('ttype', 'in', %s),('name','not in',['email','name','country_id'])]" % SIGNUP_ATTRIBUTE_TYPES,
        ondelete= 'cascade',
    )
    attribute_type = fields.Selection("Attribute Type",
            related = "attribute.ttype",
            store = True,
            help="Associated attribute type in the SignUp form.",)
    attribute_input_type = fields.Char("Input Type", help="Field input type in signup form",
        compute = "_compute_attribute_input_type", store=True)
    attribute_status = fields.Boolean(string="Registration Attributes Status", help="Enable/Disable this attribute in signup form")
    sequence = fields.Integer(string="Registration Attributes Sequence", help="Sorting order number for this attribute in signup form")
    code = fields.Char(string="Code")
    attribute_label = fields.Char("Attribute Label",help="Label for this attribute in signup form", translate=True)
    is_required = fields.Boolean("Is Required", help="Enable if associated attribute will be required")
    group_id = fields.Many2one(comodel_name="seller.register.group", string="Seller Registration Group")
    placeholder = fields.Char("Placeholder", help="Placeholder value for this field in signup form", translate=True)
    attribute_domain = fields.Char("Attribute Domain")

    @api.constrains('attribute', 'group_id')
    def _check_unique_attribute(self):
        for rec in self:
            attr_obj = self.env["seller.register.attributes"].search([])
            if attr_obj:
                filtered_attributes =  attr_obj.filtered(lambda x: x.attribute.id == rec.attribute.id)
                list_of_total = []
                for attr in filtered_attributes:
                    grp_id = attr.group_id.id
                    website_id =  attr.group_id.website_id.id
                    total = grp_id + website_id
                    if total in list_of_total:
                        raise ValidationError("Attribute already exist.")
                    list_of_total.append(total)

    @api.onchange("attribute")
    def _compute_attribute_label(self):
        for rec in self:
            if rec.attribute:
                rec.attribute_label = rec.attribute.field_description
                rec.attribute_domain = ''

    @api.depends("attribute_type")
    def _compute_attribute_input_type(self):
        for rec in self:
            attribute_type = rec.attribute_type
            if attribute_type:
                input_type = [item for item in ATTRIBUTE_INPUT_TYPE if attribute_type in item[0]]
                if input_type and input_type[0] and input_type[0][1]:
                    rec.attribute_input_type = input_type[0][1]

    def get_attribute_obj_relation(self):
        for rec in self:
            obj_relation = None
            attribute = rec.attribute
            if attribute and rec.attribute_type in ['many2one', 'many2many']:
                obj_relation = attribute.relation
        return obj_relation

    def action_add_domain(self):
        obj_relation = self.get_attribute_obj_relation()
        view_id = self.env["field.add.domain"].create({})
        vals = {
            'name' : _("Add Domain"),
            'view_mode' : 'form',
            'res_model' : 'field.add.domain',
            'res_id' : view_id.id,
            'context' : "{'obj_relation': '%s'}" % obj_relation,
            'type' : "ir.actions.act_window",
            'target' : 'new',
         }
        return vals
