# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


class MailBlackList(models.Model):
    _inherit = 'mail.blacklist'

    def _remove(self, email):
        record = super(MailBlackList, self)._remove(email)
        partner_ids = self.env['res.partner'].search([('email', '=', email)])
        if partner_ids:
            partner_ids.write({'email_blacklist': False})
        return record

