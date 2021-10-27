# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    holding_partner_id = fields.Many2one('res.partner', 'Holding Partner', domain=[('is_company', '=', True)])
