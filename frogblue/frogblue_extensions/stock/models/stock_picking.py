# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class StockReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    @api.model
    def default_get(self, fields_list):
        defaults = super(StockReturnPicking, self).default_get(fields_list)
        if self._context.get('active_model') == 'stock.picking':
            for return_move in defaults.get('product_return_moves', []):
                return_move[2]['to_refund'] = True
        return defaults


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_intercompany = fields.Boolean(
        'Is intercompany?',
        compute='_compute_is_intercompany'
    )
    
    def open_scheduled_date_update(self):
        self.ensure_one()

        result = {
            'name': "Update scheduled date",
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'ic.picking.date',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

        return result

    
    def _compute_is_intercompany(self):
        for record in self:
            ic_model, ic_ids = record._get_intercompany_records()
            res = len(ic_ids) > 0
            record.is_intercompany = res

    
    def _get_intercompany_records(self):
        self.ensure_one()
        self = self.sudo()

        result_model = 'stock.picking'
        result_ids = []
        picking_type = self.picking_type_id.code

        if picking_type == 'incoming' and self.purchase_id:
            result_model = 'sale.order'

            if self.purchase_id.auto_sale_order_id:
                result_ids = self.purchase_id.auto_sale_order_id.ids
            else:
                result_ids = self.env[result_model].search(
                    [('auto_purchase_order_id', '=', self.purchase_id.id)]
                ).ids

        elif picking_type == 'outgoing' and self.sale_id:
            result_model = 'purchase.order'

            if self.sale_id.auto_purchase_order_id:
                result_ids = self.sale_id.auto_purchase_order_id.ids
            else:
                result_ids = self.env[result_model].search(
                    [('auto_sale_order_id', '=', self.sale_id.id)]
                ).ids

        return result_model, result_ids
