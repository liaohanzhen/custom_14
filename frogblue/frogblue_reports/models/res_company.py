# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    # Field declarations
    footer_report = fields.Html('Footer Report')
