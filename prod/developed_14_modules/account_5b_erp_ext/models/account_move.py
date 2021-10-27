# -*- coding: utf-8 -*-
from odoo import models,fields

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    account_analytic_id = fields.Many2one('account.analytic.account', related='invoice_line_ids.analytic_account_id', string='Analytic Account')
    