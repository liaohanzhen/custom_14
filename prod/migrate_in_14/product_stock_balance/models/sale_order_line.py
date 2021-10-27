# -*- coding: utf-8 -*-

from odoo import api, models


class sale_order_line(models.Model):
    _inherit = "sale.order.line"

#     @api.multi
    def action_show_stocks_by_locations(self):
        """
        Method to open product form only with locations

        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        context = {"form_view_ref": "product_stock_balance.product_product_form_only_locations"}
        return {
            'name': self.product_id.name,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product.product',
            'res_id': self.product_id.id,
            'type': 'ir.actions.act_window',
            'context': context,
            'target': 'new',
        }
