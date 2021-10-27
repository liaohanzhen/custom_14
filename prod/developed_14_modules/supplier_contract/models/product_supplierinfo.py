# -*- coding: utf-8 -*-

from odoo import models,fields, api

class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'
    
    contract_status = fields.Selection([('Account','Account'),('No Account','No Account')],string="Status",compute='_compute_supplier_contract_status')
    
    @api.depends('name.active_contract')
    def _compute_supplier_contract_status(self):
        for supplierinfo in self:
            if supplierinfo.name.active_contract:
                supplierinfo.contract_status = 'Account'
            else:
                supplierinfo.contract_status = 'No Account'
    