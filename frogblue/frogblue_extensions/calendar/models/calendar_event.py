# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Meeting(models.Model):
    _inherit = 'calendar.event'

    team_id = fields.Many2one('crm.team', compute="_compute_sales_team", store=True)
    related_partner_id = fields.Many2one('res.partner', compute='_compute_sales_team', store=True)

    @api.onchange('partner_ids')
    def _compute_sales_team(self):
        team = partner_id = False
        for event in self:
            if event.partner_ids:
                users = self.env['res.users'].sudo().search([('partner_id', 'in', event.partner_ids.ids)])
                users_partner = users.mapped('partner_id.id')
                for partner in event.partner_ids:
                    if not partner._origin.id in users_partner and not partner.parent_id:
                        team = partner._origin.commercial_partner_id.team_id.id
                        partner_id = partner._origin.commercial_partner_id.id
            event.team_id = team
            event.related_partner_id = partner_id
