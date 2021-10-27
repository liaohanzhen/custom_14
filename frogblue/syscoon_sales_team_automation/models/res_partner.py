'''
# -*- coding: utf-8 -*-
'''
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def create(self, values):
        res = super(ResPartner, self).create(values)
        if res and res.country_id:
            team_id = self.env['sales.team.automation'].return_team_id(res.country_id.id, res.state_id.id, res.zip)
            if team_id:
                res.team_id = team_id.id
        return res
