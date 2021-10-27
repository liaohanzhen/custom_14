# -*- coding: utf-8 -*-
from . import models
from . import wizard

from odoo import api, SUPERUSER_ID
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import unquote
def _set_domain_in_task_action(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    #Only Show Regular task in all actions. No need to show template task.
    actions = env['ir.actions.act_window'].search([('res_model', '=', 'project.task')])
    for action in actions:
        domain_original = '[]'
        if action.domain:
            domain_original = action.domain
        if "is_template" not in domain_original:
            domain_original = domain_original.strip()
            if domain_original[-1:]==']':
                if len(domain_original)>2:
                    domain_original = domain_original[:-1]+",('is_template','=',False)"
                else:
                    domain_original = domain_original[:-1]+"('is_template','=',False)"
                #domain_original.append("('is_template','=',False)")
                action.write({'domain':domain_original})        
            
def _remove_domain_in_task_action(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    #Only Show Regular task in all actions. No need to show template task.
    actions = env['ir.actions.act_window'].search([('res_model', '=', 'project.task')])
    for action in actions:
        domain_original = '[]'
        domain_original = action.domain or ""
        
        if "is_template" in domain_original:
            domain_original = domain_original.replace(",('is_template','=',False)","")
            domain_original = domain_original.replace("('is_template','=',False)","")
            action.write({'domain':domain_original})    