# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models 


class WeeeNumber(models.Model):
    _name = "weee.number"
    _description = "Wee Numbers"

    country_id = fields.Many2one('res.country', string='Country', required=True)
    weee_number = fields.Char('WEEE Number', required=True, size=50)
    company_id = fields.Many2one('res.company', string='Company', required=True)


class Company(models.Model):
    _inherit = "res.company"

    auto_validate_shipments = fields.Boolean('Auto validate shipments when delivering to this company?')
    fax = fields.Char(related='partner_id.fax',string="Fax")
    weee_numbers = fields.One2many('weee.number', 'company_id', string='Weee Numbers')
    account_tag_ids = fields.Many2many('account.account.tag', 'res_company_account_tag', string='Tags')

    
    def get_weee_number(self, company_id, country_id=False, country_name=False, country_code=False):
        self.ensure_one()
        weee_number = False
        weee_country_id = False
        weee_company_id = company_id and company_id.id or False
        if not weee_company_id:
            return weee_number
        if country_id:
            weee_country_id = country_id and country_id.id or False
        elif country_name:
            country_id = self.env['res.country'].search([('name', '=', country_name)])
            weee_country_id = country_id and country_id[0] and country_id[0].id or False
        elif country_code:
            country_id = self.env['res.country'].search([('code', '=', country_code)])
            weee_country_id = country_id and country_id[0] and country_id[0].id or False
        if not weee_country_id:
            return weee_number
        weee_number_ids = self.env['weee.number'].search(
            [('country_id', '=', weee_country_id), ('country_id', '=', weee_country_id)]
        )
        weee_number = weee_number_ids and weee_number_ids[0] and weee_number_ids[0].weee_number or False
        return weee_number
