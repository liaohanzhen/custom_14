# -*- coding: utf-8 -*-
from odoo import models,fields, api

class QualityPoint(models.Model):
    _inherit = 'quality.point'
    
    iframe_url = fields.Char("iFrame URL")
    