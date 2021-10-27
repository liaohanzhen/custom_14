# -*- coding: utf-8 -*-

from odoo import models,fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    supplier_status = fields.Selection([('Approved','Approved'),('Not Approved','Not Approved')],string="Supplier Status",compute='_compute_supplier_status',store=True)
    
    @api.depends('partner_id.approved_supplier')
    def _compute_supplier_status(self):
        for purchase_order in self:
            if purchase_order.partner_id.approved_supplier:
                purchase_order.supplier_status = 'Approved'
            else:
                purchase_order.supplier_status = 'Not Approved'
    