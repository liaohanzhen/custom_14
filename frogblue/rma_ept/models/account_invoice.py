# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields,models,api

class AccountInvoice(models.Model):
    _inherit = 'account.move'

    claim_id = fields.Many2one('crm.claim.ept', string='Claim')
    
    @api.model
    def _prepare_refund(self, *args, **kwargs):
        result = super(AccountInvoice, self)._prepare_refund(*args, **kwargs)
        if self.env.context.get('claim_id'):
            result['claim_id'] = self.env.context['claim_id']
        return result