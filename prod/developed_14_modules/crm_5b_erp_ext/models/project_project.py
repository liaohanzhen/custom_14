# -*- coding: utf-8 -*-

from odoo import models, fields

    
class ProjectProject(models.Model):
    _inherit = 'project.project'
    
    lead_id = fields.Many2one("crm.lead","Opportinity")
    
    def open_tasks(self):
        ctx = dict(self._context)
        if not ctx.get('active_model') =='crm.lead':
            ctx={}
        ctx.update({'search_default_project_id': self.id})
        action = self.with_context({}).env['ir.actions.act_window'].for_xml_id('project', 'act_project_project_2_project_task_all')
        return dict(action, context=ctx)