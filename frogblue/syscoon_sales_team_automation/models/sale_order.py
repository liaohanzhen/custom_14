'''
# -*- coding: utf-8 -*-
'''
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, values):
        res = super(SaleOrder, self).create(values)
        if res:
            partner_id = res.partner_id
            if partner_id.country_id and partner_id.state_id and partner_id.zip:
                team_id = self.env['sales.team.automation'].return_team_id(
                    partner_id.country_id.id, partner_id.state_id.id, partner_id.zip)
                if team_id:
                    res.team_id = team_id
                    res.partner_id.team_id = team_id
        return res
