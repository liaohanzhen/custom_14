# -*- coding: utf-8 -*-

from odoo import fields, models, api

class CrmStage(models.Model):
    _inherit = 'crm.stage'
    
    checklist_ids = fields.One2many("crm.lead.checklist",'stage_id','Checklists')
    no_need_of_checklist = fields.Boolean("No need for checklist")