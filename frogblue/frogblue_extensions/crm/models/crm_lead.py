# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    # firstname = fields.Char("First name")
    # lastname = fields.Char("Last name")

    double_opt_in = fields.Boolean("Double Opt-in")

    parent_id = fields.Many2one('res.partner', string='Related Company', index=True)
    parent_name = fields.Char(related='parent_id.name', readonly=True, string='Parent name')
    company_name = fields.Char('Company Names')

    fax = fields.Char("Fax")
    salutation = fields.Char(string='Salutation')

    
    def _create_lead_partner_data(self, name, is_company, parent_id=False):
        res = super(CrmLead, self)._create_lead_partner_data(name, is_company, parent_id=parent_id)
        # res['firstname'] = self.firstname
        # res['lastname'] = self.lastname
        res['double_opt_in'] = self.double_opt_in
        res['parent_id'] = self.parent_id and self.parent_id.id or False
        res['company_name'] = self.company_name
        return res


    def _onchange_partner_id_values(self, partner_id):
        res = super(CrmLead, self)._onchange_partner_id_values(partner_id)
        res['fax'] = self.partner_id.fax
        return res

    def action_new_quotation(self):
        if self.partner_id:
            if self.partner_assigned_id and self.partner_assigned_id.id not in self.partner_id.sudo().assigned_partner_ids.ids:
                self.partner_id.sudo().write({'assigned_partner_ids':[(4,self.partner_assigned_id.id)]})
        res = super(CrmLead, self).action_new_quotation()
        return res
    
    @api.model
    def create(self, vals):
        res = super(CrmLead, self).create(vals)
        if res.partner_id and res.partner_assigned_id and res.partner_assigned_id.id not in res.partner_id.sudo().assigned_partner_ids.ids:
            res.partner_id.sudo().write({'assigned_partner_ids':[(4,res.partner_assigned_id.id)]})
            
        return res
    
    def write(self, vals):
        res = super(CrmLead, self).write(vals)
        if vals.get('partner_assigned_id'):
            for rec in self:
                if rec.partner_id and rec.partner_assigned_id and rec.partner_assigned_id.id not in rec.partner_id.sudo().assigned_partner_ids.ids:
                    rec.partner_id.sudo().write({'assigned_partner_ids':[(4,rec.partner_assigned_id.id)]})
            
        return res
        