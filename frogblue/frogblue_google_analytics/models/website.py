# -*- coding: utf-8 -*-
from odoo import fields, models


class Website(models.Model):
    _inherit = 'website'

    google_tagmanager_key = fields.Char('Google container ID')
