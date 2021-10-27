# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.onchange("firstname", "lastname")
    def _compute_name(self):
        for rec in self:
            rec.name = rec.partner_id._get_computed_name(rec.lastname, rec.firstname)
