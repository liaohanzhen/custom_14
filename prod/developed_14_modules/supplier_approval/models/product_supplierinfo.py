# -*- coding: utf-8 -*-

from odoo import models,fields, api

class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'
    
    status = fields.Selection([('Approved','Approved'),('Not Approved','Not Approved')],string="Status",compute='_compute_supplier_status',store=True)
    
    @api.depends('name.approved_supplier')
    def _compute_supplier_status(self):
        for supplierinfo in self:
            if supplierinfo.name.approved_supplier:
                supplierinfo.status = 'Approved'
            else:
                supplierinfo.status = 'Not Approved'
    