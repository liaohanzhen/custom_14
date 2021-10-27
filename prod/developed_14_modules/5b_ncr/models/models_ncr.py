# -*- coding: utf-8 -*-

from odoo import models, fields, api

class FiveB_Nonconformity(models.Model):
    _inherit = "mgmtsystem.nonconformity"
    active = fields.Boolean('Active', default=True)
