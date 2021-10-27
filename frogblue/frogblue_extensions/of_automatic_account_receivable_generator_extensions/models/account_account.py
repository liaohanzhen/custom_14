# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields


class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.model
    def _prepare_custom_account_receivable_data(self, partner):
        record = super(AccountAccount,self)._prepare_custom_account_receivable_data(partner)
        record.update({
            'tag_ids': [(4, tag.id, False) for tag in self.env['res.company']._company_default_get().account_tag_ids]
        })
        return record
