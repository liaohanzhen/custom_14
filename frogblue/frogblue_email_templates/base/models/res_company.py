# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    use_email_footer = fields.Boolean("Use Email Footer", help="Check if you want 'Email Footer' to be printed in email.")
    email_footer = fields.Text("Email Footer", translate=True)
