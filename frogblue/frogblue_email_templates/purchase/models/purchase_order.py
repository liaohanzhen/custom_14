# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields
from odoo.tools.misc import format_date
from datetime import datetime


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def get_partner_lang(self, shipping=False, invoice=False):
        partner = self.partner_id
        if not partner:
            return self.env['res.lang'].search([('code', '=', 'en_EN')])
        return self.env['res.lang'].search([('code', '=', partner.lang)])

    def get_formated_date(self, date=False, lang_code=False, date_format=False, now=False):
        if now:
            date = datetime.now()
        res = format_date(self.env, date, lang_code=lang_code, date_format=date_format)
        return res

    def action_rfq_send(self):
        '''
        This function opens a window to compose an email, with the frogblue edi invoice template message loaded by default
        '''
        action_dict = super(PurchaseOrder, self).action_rfq_send()
        try:
            if self.env.context.get('send_rfq', False):
                template_id = self.env['ir.model.data'].get_object_reference(
                    'frogblue_email_templates',
                    'frogblue_email_template_edi_purchase'
                )[1]
            else:
                template_id = self.env['ir.model.data'].get_object_reference(
                    'frogblue_email_templates',
                    'frogblue_email_template_edi_purchase'
                )[1]
            # assume context is still a dict, as prepared by super
            ctx = action_dict['context']
            ctx['default_template_id'] = template_id
            ctx['default_use_template'] = True
            # ctx['custom_layout'] = 'frogblue_email_templates.frogblue_email_template_edi_purchase',
        except Exception as e:
            pass
        return action_dict
