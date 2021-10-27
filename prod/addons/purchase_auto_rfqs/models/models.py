# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, SUPERUSER_ID, _
import base64
import logging
from datetime import datetime, timedelta
from odoo.exceptions import UserError
_logger = logging.getLogger(__name__)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    confirm_pa_and_generate_rfqs = fields.Boolean("Confirm PA and Generate RFQs", _default="True", store="True")
    
    
class PurchaseRequisitionType(models.Model):
    _inherit = "purchase.requisition.type"

    x_confirm_pa_and_generate_rfqs = fields.Boolean("Confirm PA and Generate RFQs")
    
class ProductReplenish(models.TransientModel):
    _inherit = "product.replenish"

    x_type_id = fields.Many2one('purchase.requisition.type', string='Agreement Type')
    
class ProductTemplateInherit(models.Model):
    _inherit = "product.template"

    x_type_id = fields.Many2one('purchase.requisition.type', string='Agreement Type')

class purchase_auto_rfqs(models.Model):
    _inherit = 'purchase.requisition'
    
    @api.model
    def create(self,vals):
        res = super(purchase_auto_rfqs, self).create(vals)
        _logger.error("Create ID : [" + str(res) + "]["+str(res.type_id.x_confirm_pa_and_generate_rfqs)+"]["+str(vals)+"]["+str(self.env['ir.config_parameter'].sudo().get_param('x_confirm_pa_and_generate_rfqs'))+"]")
        if res.type_id.x_confirm_pa_and_generate_rfqs or (self.env['ir.config_parameter'].sudo().get_param('confirm_pa_and_generate_rfqs') or False):
            #self.action_in_progress2()
            if not res.line_ids:
                raise UserError(_("You cannot confirm agreement '%s' because there is no product line.", res.name))
            if res.type_id.quantity_copy == 'none' and res.vendor_id:
                for requisition_line in res.line_ids:
                    if requisition_line.price_unit <= 0.0:
                        raise UserError(_('You cannot confirm the blanket order without price.'))
                    if requisition_line.product_qty <= 0.0:
                        raise UserError(_('You cannot confirm the blanket order without quantity.'))
                    requisition_line.create_supplier_info()
                #self.write({'state': 'ongoing'})
                res.state = 'ongoing'
            else:
                #self.write({'state': 'in_progress'})
                res.state = 'in_progress'
            # Set the sequence number regarding the requisition type
            if res.name == 'New':
                if res.is_quantity_copy != 'none':
                    res.name = self.env['ir.sequence'].next_by_code('purchase.requisition.purchase.tender')
                else:
                    res.name = self.env['ir.sequence'].next_by_code('purchase.requisition.blanket.order')
            res.generate_related_rfqs()
        return res
        
    def action_in_progress2(self):
        #self.ensure_one()
        if not self.line_ids:
            raise UserError(_("You cannot confirm agreement '%s' because there is no product line.", self.name))
        if self.type_id.quantity_copy == 'none' and self.vendor_id:
            for requisition_line in self.line_ids:
                if requisition_line.price_unit <= 0.0:
                    raise UserError(_('You cannot confirm the blanket order without price.'))
                if requisition_line.product_qty <= 0.0:
                    raise UserError(_('You cannot confirm the blanket order without quantity.'))
                requisition_line.create_supplier_info()
            self.write({'state': 'ongoing'})
        else:
            self.write({'state': 'in_progress'})
        # Set the sequence number regarding the requisition type
        if self.name == 'New':
            if self.is_quantity_copy != 'none':
                self.name = self.env['ir.sequence'].next_by_code('purchase.requisition.purchase.tender')
            else:
                self.name = self.env['ir.sequence'].next_by_code('purchase.requisition.blanket.order')    
                
    def _select_purchase_order_by_rank(self, requisition_id):
        return self.env['purchase.order'].search([('requisition_id','=',requisition_id)], order = "amount_total asc", limit = 1)
        
    def generate_related_rfqs(self):
        requisition_id = self.id
        _logger.error("Agreement ID : [" + str(requisition_id) + "]")
        order_lines = []
        for line in self.line_ids:
            if len(line.product_id.route_ids) > 0:
                if line.product_id.route_ids[0].name == 'Buy' and line.product_id.x_type_id and line.product_id.x_type_id.x_confirm_pa_and_generate_rfqs:
                    #_logger.error("All items : [" + str(line.product_id.name) + "][" + str(line.product_id.route_ids[0].name) + "][" + str(line.product_id.seller_ids) + "]")
                    
                    purchase_line_id = None
                    already_exist = []
                    
                    for sellers in line.product_id.seller_ids:
                        if sellers.name.id not in already_exist:
                            _date_order = self.env['purchase.order.line']._get_date_planned(sellers)
                            vals_list = {
                                'requisition_id' : requisition_id,
                                'partner_id' : sellers.name.id,
                                'date_order': _date_order
                            }
                            #_logger.error("All Sellers : [" + str(sellers.name.name) + "][ " + str( vals_list ) + "]")
                            purchase_id = self.env['purchase.order'].create(vals_list)
                            #_logger.error("All Sellers : [" + str(purchase_id) + "][ " + str( vals_list ) + "]")
                            
                            line_vals_list = self.env['purchase.order.line']._prepare_purchase_order_line(line.product_id, line.product_qty, line.product_uom_id, self.company_id, sellers, purchase_id)
                            '''
                            line_vals_list = {
                                'order_id' : purchase_id.id,
                                'product_id' : line.product_id.id,
                                'date_planned': datetime.today().date(),
                                'product_qty':line.product_qty,
                                'product_uom': line.product_uom_id.id,
                                'name':line.product_id.name,
                            }
                            '''
                            _logger.error("All Sellers Line : [ " + str( line_vals_list ) + "]")
                            purchase_line_id = self.env['purchase.order.line'].create(line_vals_list)
                            #_logger.error("All Sellers Line : [" + str(purchase_line_id) + "][ " + str( line_vals_list ) + "]")
                            already_exist.append(sellers.name.id)
                        
                    if purchase_line_id:
                        if requisition_id:
                            select_one = self._select_purchase_order_by_rank(requisition_id)
                            select_one.button_confirm()
                        ctx = {
                            'default_requisition_id': requisition_id
                        }
                        return {
                            'name': _('Request for Quotations'),
                            'view_mode': 'tree',
                            'res_model': 'purchase.order',
                            'view_id': self.env.ref('purchase.purchase_order_tree').id,
                            'type': 'ir.actions.act_window',
                            'target': 'self',
                            'context':ctx,
                            'domain':[('requisition_id','=',requisition_id)]
                        }