# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _prepare_sale_order_data(self, name, partner, company, direct_delivery_address):

        if not direct_delivery_address:
            direct_delivery_address = self.picking_type_id and \
                                      self.picking_type_id.warehouse_id and \
                                      self.picking_type_id.warehouse_id.partner_id and \
                                      self.picking_type_id.warehouse_id.partner_id.id or False

        return super(PurchaseOrder, self)._prepare_sale_order_data(name, partner, company, direct_delivery_address)
