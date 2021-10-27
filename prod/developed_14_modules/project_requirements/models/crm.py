# -*- coding: utf-8 -*-

from odoo import models, api

    
class CrmStage(models.Model):
    _inherit = 'crm.stage'
    
    @api.model
    def get_create_project(self, stage_id):
        if self.env.user.has_group('project.group_project_user') or self.env.user.has_group('project.group_project_manager'):
            return self.browse(stage_id).create_project
        else:
            return False

class CrmLead(models.Model):
    _inherit = 'crm.lead'
    
    #Override method, so it not create project from Lead. It is created using popup.
    def create_project_from_opp(self):
        return True