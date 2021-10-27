# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class AccountAsset(models.Model):
    _inherit = 'account.asset'

    code = fields.Char(index=True)

    _sql_constraints = [('code_uniq', 'unique (code,company_id)',
                         "The Reference must be unique!")]

    hist_ahk = fields.Text(string="Hist. AHK")
    hist_purchase_date = fields.Date('Purchase Date')

    total_usage_time_type = fields.Selection([('daily', 'Day(s)'), ('weekly', 'Week(s)'),
                                            ('monthly', 'Month(s)'), ('yearly', 'Year(s)'), ],
                                           string='Type', tracking=True)
    total_usage_time = fields.Integer(string="Total Usage Time", tracking=True)

    inventoried = fields.Boolean('Inventoried')

    aml_ids = fields.One2many(
        'account.move.line',
        'asset_id',
        string='Associated AMLs',
    )
    # Remove this because field category is deprecated from account.asset
    #related_account_id = fields.Many2one(related='category_id.account_asset_id')
