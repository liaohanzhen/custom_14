# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    rma_id = fields.Many2one('crm.claim.ept', string='RMA Ticket', copy=False)
    crm_team_id = fields.Many2one('crm.team', string='Sales Channel', related='partner_id.team_id', store=True)
    partner_country_id = fields.Many2one(related='partner_id.country_id')