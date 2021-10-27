# -*- coding: utf-8 -*-

from odoo import fields, models, api
from odoo.exceptions import Warning

class CRMLeadChecklist(models.Model):
    _name = 'crm.lead.checklist'
    _description = 'CRM Checklist'

    name = fields.Char(required="True")
    groups_ids = fields.Many2many("res.groups","crm_checklist_groups_rel", 'checklist_id', 'group_id', "User Groups")
    stage_id = fields.Many2one('crm.stage',"Stage")
    description = fields.Text()


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    crm_lead_checklist = fields.Many2many('crm.lead.checklist', 'crm_lead_checklist_rel', 'checklist_id', 'crm_id', 'CRM Checklist')
    #check_marked = fields.Float('Checklist status', compute='_compute_check_marked',store=True)
    #max_exit_value = fields.Float(compute='_get_max_exit_count', default=0.0)
    #max_value = fields.Float(default=100.0)
    
    def write(self, vals):
        stage_id = vals.get("stage_id")
        crm_lead_checklist = vals.get('crm_lead_checklist')
        if stage_id:
            for lead in self:
                if lead.stage_id.no_need_of_checklist:
                    continue
                if not set(lead.stage_id.checklist_ids.ids).issubset(set(lead.crm_lead_checklist.ids)):
                    raise Warning("Please enter checklist for the opportunity '%s'!\nYou can't move this case forward until you confirm all jobs have been done."%(lead.name))
        if crm_lead_checklist:
            old_vals_dict = {}
            lead_checklist_obj = self.env['crm.lead.checklist']
            #new_checklists = lead_checklist_obj.browse()
            user_groups = self.env.user.groups_id.ids
            new_checklist = crm_lead_checklist[0][2]
            for lead in self:
                old_checklists = lead.crm_lead_checklist
                old_vals_dict[lead.id] = old_checklists.mapped('name')
                old_checklist_ids = old_checklists.ids
                newely_added_ids = list(set(new_checklist)-set(old_checklist_ids))
                newely_removed_ids = list(set(old_checklist_ids)-set(new_checklist))
                if newely_added_ids:
                    newely_added = lead_checklist_obj.browse(newely_added_ids)
                    #new_checklists +=newely_added
                    for checklist in newely_added:
                        if not set(checklist.groups_ids.ids).issubset(set(user_groups)):
                            raise Warning("Sorry, but you don't have rights to confirm/disapprove '%s'!\nContact your system administrator for assistance."%(checklist.name))
                if newely_removed_ids:
                    newely_removed = lead_checklist_obj.browse(newely_removed_ids)
                    #new_checklists +=newely_removed
                    for checklist in newely_removed:
                        if not set(checklist.groups_ids.ids).issubset(set(user_groups)):
                            raise Warning("Sorry, but you don't have rights to confirm/disapprove '%s'!\nContact your system administrator for assistance."%(checklist.name))
                
        res = super(CrmLead, self).write(vals)
        if vals.get("crm_lead_checklist"):
            for lead in self:
                old_vals = old_vals_dict.get(lead.id, [])
                new_vals = lead.crm_lead_checklist.mapped('name')
                
                len_old = len(old_vals)
                len_new = len(new_vals)
                str_data = "<table><tr><td style='font-weight:bold;border:1px black solid;' colspan='2'>Gate Checklist</td></tr>"
                str_data += "<tr><td style='font-weight:bold;border:1px black solid;'>Old</td><td style='font-weight:bold;border:1px black solid;'>New</td></tr>"
                for index in range(max(len_old,len_new)):
                    old_val = old_vals[index] if index < len_old else '&nbsp; &nbsp;'
                    new_val = new_vals[index] if index < len_new else '&nbsp; &nbsp;'
                    
                    str_data =  str_data + """
                        <tr>
                            <td style="border:1px black solid;"> %s </td>
                            <td style="border:1px black solid;"> %s </td> 
                        </tr>
                    """%(old_val, new_val)
                str_data +='</table>'    
                lead.message_post(body=str_data)
            
        return res
    
    
#     def _get_max_exit_count(self):
#         for rec in self:
#             all_checklist = self.env['crm.lead.checklist'].search([])
#             rec.max_exit_value = len(all_checklist)
# 
#     @api.depends('crm_lead_checklist')
#     def _compute_check_marked(self):
#         all_checklist = self.env['project.checklist'].search([])
#         if len(all_checklist) >=1 : 
#             for rec in self:
#                 selected_checklist = rec.crm_lead_checklist
#                 rec.check_marked = (len(selected_checklist)* 100)/len(all_checklist)

