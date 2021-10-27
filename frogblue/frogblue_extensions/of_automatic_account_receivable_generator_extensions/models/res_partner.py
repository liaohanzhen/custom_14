# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _

PROPERTY_ACCOUNT_RECEIVABLE_ID = 'property_account_receivable_id'


class ResPartner(models.Model):
    _inherit = 'res.partner'

    has_custom_account_receivable = fields.Boolean(copy=False)
    ref = fields.Char(copy=False)

    def setup_custom_accounting_configurations(self):
        accounts = self.assign_custom_receivable_account()
        references = self.assign_custom_reference()

        return {
            'account_ids': accounts,
            'references': references
        }

    
    def assign_custom_reference(self):
        partner_refs = []

        for partner in self:
            if not partner.commercial_partner_id.ref:
                partner_seq = self.env.ref('of_automatic_account_receivable_generator.of_automatic_res_partner_ref')
                if partner.has_custom_account_receivable:
                    number = self.commercial_partner_id.property_account_receivable_id.code

                    partner_refs.append({partner.id: number})
                    partner.commercial_partner_id.ref = number
                else:
                    partner.commercial_partner_id.ref = ''
        return super(ResPartner, self).assign_custom_reference()
