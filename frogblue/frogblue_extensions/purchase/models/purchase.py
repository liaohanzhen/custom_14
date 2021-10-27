# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class Purchase(models.Model):
    _inherit = 'purchase.order'

    confirmed_lt_date = fields.Date('Confirmed LT', copy=False)

