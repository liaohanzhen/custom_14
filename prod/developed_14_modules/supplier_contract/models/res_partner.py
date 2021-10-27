# -*- coding: utf-8 -*-

from odoo import models,api, fields
from datetime import datetime

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    partner_contract_ids = fields.One2many("res.partner.contract",'partner_id','Contracts')
    active_contract = fields.Boolean("Active Contract",compute="_compute_active_contract")
    @api.depends("partner_contract_ids.validity_date")
    def _compute_active_contract(self):
        active_contract = False
        for contract in self.partner_contract_ids:
            if contract.validity_date:
                validity_date = contract.validity_date #datetime.strptime(contract.validity_date,'%Y-%m-%d %H:%M:%S')
                if validity_date > datetime.now():
                    active_contract=True
                    break
        self.active_contract = active_contract
        
    
class ResPartnerContract(models.Model):
    _name = 'res.partner.contract'
    
    @api.model
    def _default_date(self):
        return datetime.now()
        
    date = fields.Datetime("Date",default=_default_date)
    user_id = fields.Many2one('res.users','Create By',default=lambda self: self.env.user)
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms',help="This payment term will be used instead of the default one for purchase orders and vendor bills")
    payment_term_id_tmp = fields.Many2one('account.payment.term', string='Payment Term Tmp')
    validity_date = fields.Datetime("Validity Date")
    partner_id = fields.Many2one("res.partner",'Supplier',domain=[('supplier','=',True)])
    file = fields.Binary("Attachment")
    
    @api.onchange('date','validity_date')
    def onchange_date_validity_date(self):
        if self.date and self.validity_date:
            date = self.date #datetime.strptime(self.date,'%Y-%m-%d %H:%M:%S')
            validity_date = self.validity_date #datetime.strptime(self.validity_date,'%Y-%m-%d %H:%M:%S')
            if validity_date > date:
                self.payment_term_id_tmp = self.payment_term_id.id                
            