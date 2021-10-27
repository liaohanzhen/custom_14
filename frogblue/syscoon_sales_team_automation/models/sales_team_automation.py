'''
# -*- coding: utf-8 -*-
'''
from odoo import api, fields, models


class SalesTeamAutomation(models.Model):
    _name = 'sales.team.automation'
    _description = 'Sales Team Automation'

    name = fields.Char(string='Name')
    team_id = fields.Many2one('crm.team')
    country_ids = fields.Many2many('res.country')
    state_ids = fields.Many2many('res.country.state')
    zip_from = fields.Char()
    zip_to = fields.Char()

    @api.model
    def create(self, values):
        ''''''
        name = self._create_name_sales_team(values)
        if name:
            values.update({'name': name})
        return super(SalesTeamAutomation, self).create(values)

    def write(self, values):
        res = super(SalesTeamAutomation, self).write(values)
        if res:
            sales_automation_id = self
            name = self._write_sales_team_name(sales_automation_id)
            if name and not self.env.context.get('sales_automation_name'):
                self.with_context({'sales_automation_name': True}).name = name
        return res

    def _create_name_sales_team(self, values):
        name = ''
        country_codes = ''
        if values.get('country_ids'):
            for code in values.get('country_ids')[0][2]:
                country_code = self.env['res.country'].browse(code)
                country_codes += country_code.code + ', '
        if country_codes:
            team_name = self.env['crm.team'].browse(values.get('team_id'))
            name = '{}, {}'.format(team_name.name, country_codes)
            if values.get('zip_from') and values.get('zip_to'):
                name += '{} - {}'.format(values.get('zip_from'), values.get('zip_to'))
        return name

    def _write_sales_team_name(self, sales_automation_id):
        county_code = ''
        name = ''
        for code in sales_automation_id.country_ids:
            county_code += code.code + ', '
        if county_code or sales_automation_id.zip_from or sales_automation_id.zip_to:
            name = '{}, {} '.format(sales_automation_id.team_id.name, county_code)
            if sales_automation_id.zip_from:
                name += '{}'.format(sales_automation_id.zip_from or 0)
            if sales_automation_id.zip_to:
                name += ' - {}'.format(sales_automation_id.zip_to or 0)
        return name

    def return_team_id(self, country_ids, state_ids, zip_code):
        sales_team_automation = self.env['sales.team.automation'].search(
            [('country_ids', '=', country_ids), ('state_ids', '=', state_ids), ('zip_from', '<=', zip_code),
             ('zip_to', '>=', zip_code)], limit=1)
        if sales_team_automation:
            return sales_team_automation.team_id
