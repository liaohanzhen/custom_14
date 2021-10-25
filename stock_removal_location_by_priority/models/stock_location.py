# -*- coding: utf-8 -*-

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    removal_priority = fields.Integer(
        string="Removal Priority", default=10,
        help="This priority applies when removing stock and incoming dates are equal.")
