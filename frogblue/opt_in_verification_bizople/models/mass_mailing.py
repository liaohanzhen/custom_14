# -*- coding: utf-8 -*-
# Part of Odoo Module Developed by Bizople Solutions Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.addons.http_routing.models.ir_http import slug
import string
import random
from random import randint


class MassMailingContact(models.Model):
    _inherit = 'mailing.contact'

    def _get_opt_in_link(self):
        for obj in self:
            link = "/user-opt-in?contact=%s" % obj.contact_uniq_number or ""
            obj.opt_in_link = link

    opt_out = fields.Boolean(string='Opt Out', default=True,
                             help='The contact has chosen not to receive '
                                  'mails anymore from this list')
    opt_in_link = fields.Char("Opt In Link", compute="_get_opt_in_link")
    ip_address = fields.Char("IP Address")
    city_name = fields.Char("City")
    country_name = fields.Char("Country")
    contact_uniq_number = fields.Char("Uniq Number")

    def key_gen(self):
        letters = string.ascii_lowercase
        return "%s%s" % (''.join(random.choice(letters) for i in range(10)), randint(0000000000,9999999999))

    @api.model
    def create(self, vals):
        uniq_number = self.key_gen()
        avail = True
        while avail:
            mass_mail_ids = self.env['mailing.contact'].search([('contact_uniq_number', '=', uniq_number)])
            if mass_mail_ids:
               uniq_number = self.key_gen()
            else:
                avail = False
        vals.update({
            'contact_uniq_number': uniq_number
        })
        res = super(MassMailingContact, self).create(vals)
        return res
