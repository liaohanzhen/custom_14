# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    _order = 'write_date desc, name asc'

    def action_quotation_send(self):
        result = super(SaleOrder, self).action_quotation_send()
        if self.env.context.get('proforma', False):
            prepayment_tag = self.env['crm.tag'].search([('name', '=', 'Vorkasse')])
            if not prepayment_tag:
                prepayment_tag = self.env['crm.tag'].create({'name': 'Vorkasse'})
            self.write({
                'tag_ids': [(4, prepayment_tag.id)]
            })
        return result

    @api.onchange('user_id')
    def onchange_user_id(self):
        self.team_id = self.partner_id.team_id.id


