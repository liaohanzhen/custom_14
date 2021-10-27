# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Lead(models.Model):
    _inherit = 'crm.lead'

    firstname = fields.Char(string='First Name', index=True)
    lastname = fields.Char(string='Last Name', index=True)
    contact_name = fields.Char(compute='_compute_contact_name', store=True, required=False)

    @api.model
    def _get_computed_contact_name(self, firstname, lastname):
        return " ".join((p for p in (firstname, lastname) if p))

    @api.depends('firstname', 'lastname')
    def _compute_contact_name(self):
        for record in self:
            if record.type == 'lead':
                record.contact_name = record._get_computed_contact_name(record.firstname, record.lastname)
