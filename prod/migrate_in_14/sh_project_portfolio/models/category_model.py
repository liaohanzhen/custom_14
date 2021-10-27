# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models,fields,api

class portfolio_category(models.Model):
    _name = "portfolio.category"
    
    name = fields.Char(string="Category", required=True)
    is_active = fields.Boolean(string="Active",default=True)
    