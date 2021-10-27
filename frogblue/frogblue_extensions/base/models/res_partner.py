# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # firstname = fields.Char("First name")
    # lastname = fields.Char("Last name")

    fax = fields.Char("Fax")

    double_opt_in = fields.Boolean("Double Opt-in", default=True)
    department = fields.Char("Department")
    parent_id = fields.Many2one(string="Parent ID", tracking=True)
    property_payment_term_id = fields.Many2one(string="Property Payment Term ID", tracking=True)
    property_supplier_payment_term_id = fields.Many2one(string="Property Supplier Payment Term ID", tracking=True)
    property_product_pricelist = fields.Many2one(string="Property Product Pricelist", tracking=True)
    property_delivery_carrier_id = fields.Many2one(string="Property Delivery Carrier ID", tracking=True)
    property_account_position_id = fields.Many2one(string="Property Account Position ID", tracking=True)
    property_account_payable_id = fields.Many2one(string="Property Account Payable ID", tracking=True)
    property_account_receivable_id = fields.Many2one(string="Property Account Receivble ID", tracking=True)
    name = fields.Char(string="Name", tracking=True)
    customer = fields.Boolean(default=False)
    ref = fields.Char(string='Debitoren-/Kreditorennr.')
    webshop_customer_no = fields.Integer(string='Kundennr. Webshop')
    salutation = fields.Char(string='Salutation')
    status_customer = fields.Selection([
            ('unsorted', 'Unsorted'),
            ('focus_customer', 'Focus Customer'),
            ('test_customer', 'Test Customer'),
            ('project_customer', 'Project Customer'),
            ('retail_partner', 'Retail Partner'),
    ], string = 'Status Customer', tracking=True)
    sales_channel = fields.Text(string='Sales Channel')
    rma_ticket_ids = fields.One2many('crm.claim.ept', 'partner_id',string="Invoicess", readonly=True, copy=False)
    rma_ticket_count = fields.Integer(compute='_compute_rma_ticket_count', string='RMA Tickets', type='integer')
    attachment_ids = fields.One2many('ir.attachment', 'partner_id', string='Attachments', copy=False)
    email_blacklist = fields.Boolean('Email Blacklist')
    first_order_date = fields.Date('First Order Date', compute='_compute_first_order_date', store=True)
    assigned_partner_ids = fields.Many2many(
        'res.partner', 'res_partner_assigned_partner_rel','partner_id','assigned_id',string='Implemented by',
    )
    def name_get(self):
        res = []
        for partner in self:
            name = partner.name or ''

            if partner.company_name or partner.parent_id:
                if not name and partner.type in ['invoice', 'delivery', 'other']:
                    name = dict(self.fields_get(['type'])['type']['selection'])[partner.type]
                if not partner.is_company:
                    name = "%s, %s, %s, %s" % (partner.commercial_company_name or partner.parent_id.name, name, partner.zip, partner.city)
            if not partner.parent_id:
                name = "%s, %s, %s" % (name, partner.zip, partner.city)
            if self._context.get('show_address_only'):
                name = partner._display_address(without_company=True)
            if self._context.get('show_address'):
                name = name + "\n" + partner._display_address(without_company=True)
            name = name.replace('\n\n', '\n')
            name = name.replace('\n\n', '\n')
            if self._context.get('show_email') and partner.email:
                name = "%s <%s>" % (name, partner.email)
            if self._context.get('html_format'):
                name = name.replace('\n', '<br/>')
            res.append((partner.id, name))
        return res

    @api.depends('is_company', 'name', 'parent_id.name', 'type', 'company_name', 'zip', 'city')
    def _compute_display_name(self):
        super(ResPartner, self)._compute_display_name()

    
    def _compute_rma_ticket_count(self):
        RMATickets = self.env['crm.claim.ept']
        for partner in self:
            partner.rma_ticket_count = RMATickets.search_count([('partner_id', '=', partner.id)])

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['company_id'] = self.env.company.id
            if vals.get('email_blacklist') and vals.get('email'):
                blacklist = self.env['mail.blacklist']
                if not blacklist.search([('email', '=', vals['email'])]):
                    blacklist._add(vals['email'])
        return super(ResPartner, self).create(vals_list)
 
    def action_view_partner_rma_tickets(self):
        rmas = self.mapped('rma_ticket_ids')
        action = self.env.ref('rma_ept.crm_claim_ept_action').read()[0]
        if len(rmas) > 1:
            action['domain'] = [('id', 'in', rmas.ids)]
        elif len(rmas) == 1:
            action['views'] = [(self.env.ref('rma_ept.crm_claims_ept_form_view').id, 'form')]
            action['res_id'] = rmas.ids[0]
        return action

    @api.depends('sale_order_ids')
    def _compute_first_order_date(self):
        for rec in self:
            if rec.sale_order_ids:
                first_order = self.env['sale.order'].search([('id', 'in', rec.sale_order_ids.ids)], order='date_order asc', limit=1)
                if first_order:
                    rec.first_order_date = first_order.date_order
        
        
        