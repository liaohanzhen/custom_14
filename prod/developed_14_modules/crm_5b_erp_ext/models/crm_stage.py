# -*- coding: utf-8 -*-

from odoo import models, fields

    
class CrmStage(models.Model):
    _inherit = 'crm.stage'
    
    create_project = fields.Boolean("Create a project when opportunity reaches this stage")