# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    firstname = fields.Char(string='First Name', index=True)
    lastname = fields.Char(string='Last Name', index=True)
    name = fields.Char(compute='_compute_name', inverse="_inverse_name_after_cleaning_whitespace",
                       store=True, required=False)

    @api.model
    def create(self, vals):
        context = dict(self.env.context)
        name = vals.get("name", context.get("default_name"))

        if name is not None:
            # Calculate the splitted fields
            inverted = self._get_inverse_name(
                self._get_whitespace_cleaned_name(name),
                vals.get("is_company", self.default_get(["is_company"])["is_company"]))
            for key, value in inverted.items():
                    vals[key] = value

            # Remove the combined fields
            if "name" in vals:
                del vals["name"]
            if "default_name" in context:
                del context["default_name"]

        return super(ResPartner, self.with_context(context)).create(vals)

    def copy(self, default=None):
        return super(ResPartner, self.with_context(copy=True)).copy(default)

    @api.model
    def default_get(self, fields_list):
        result = super(ResPartner, self).default_get(fields_list)
        inverted = self._get_inverse_name(
            self._get_whitespace_cleaned_name(result.get("name", "")),
            result.get("is_company", False))

        for field in list(inverted.keys()):
            if field in fields_list:
                result[field] = inverted.get(field)

        return result

    @api.model
    def _get_computed_name(self, firstname, lastname):
        return " ".join((p for p in (firstname, lastname) if p))

    @api.depends('firstname', 'lastname')
    def _compute_name(self):
        for record in self:
            record.name = record._get_computed_name(record.firstname, record.lastname)

    def _inverse_name_after_cleaning_whitespace(self):

        for record in self:
            clean = record._get_whitespace_cleaned_name(record.name)
            if record.name != clean:
                record.name = clean
            else:
                record._inverse_name()

    @api.model
    def _get_whitespace_cleaned_name(self, name, comma=False):
        try:
            name = " ".join(name.split()) if name else name
        except UnicodeDecodeError:
            name = ' '.join(name.decode('utf-8').split()) if name else name
        return name

    @api.model
    def _get_inverse_name(self, name, is_company=False):
        if is_company or not name:
            parts = [name or False, False]
        else:
            name = self._get_whitespace_cleaned_name(
                name, comma=False)
            parts = name.split(" ", 1)
            if len(parts) > 1:
                parts = [" ".join(parts[1:]), parts[0]]
            else:
                while len(parts) < 2:
                    parts.append(False)
        return {"lastname": parts[0], "firstname": parts[1]}

    def _inverse_name(self):
        for record in self:
            parts = record._get_inverse_name(record.name, record.is_company)
            record.lastname = parts['lastname']
            record.firstname = parts['firstname']

    @api.constrains('firstname', 'lastname')
    def _check_name(self):
        for record in self:
            if all((
                    record.type == 'contact' or record.is_company,
                    not (record.firstname or record.lastname)
            )):
                raise ValidationError(_('No name is set'))

    _sql_constraints = [(
        'check_name',
        "CHECK( 1=1 )",
        'Contacts require a name.'
    )]
