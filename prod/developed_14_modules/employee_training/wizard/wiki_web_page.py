# -*- coding: utf-8 -*-
from odoo import models, fields

class WikiWebPageWizard(models.TransientModel):
    _name = 'wiki.web.page.wizard'
    
    iframe_url = fields.Char("iFrame URL")
    
    