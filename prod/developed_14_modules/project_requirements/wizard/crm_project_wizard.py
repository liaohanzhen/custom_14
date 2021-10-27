# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class CrmProjectWizard(models.TransientModel):
    _name = 'crm.project.wizard'
    
    project_template_id = fields.Many2one("project.template",'Please select a Project template')
    
    def create_project_from_lead(self):
        lead_id = self._context.get('lead_id')
        if lead_id:
            lead = self.env['crm.lead'].browse(lead_id)
            project_obj = self.env['project.project']
            project_template = self.project_template_id
            vals = {
                'project_code' : lead.project_code,
                'name' : lead.name,
                'description' : lead.description,
                'partner_id' : lead.partner_id.id,
                'lead_id' : lead.id,
                'stage_template_id' : project_template.stage_template_id.id,
                'project_type_id' : project_template.project_type_id.id,
                'category_id' : project_template.category_id.id,
                'project_template_id' : project_template.id
                }
            if lead.project_eng_id:
                vals.update({'user_id' : lead.project_eng_id.id})
            project_obj.create(vals)
        return True