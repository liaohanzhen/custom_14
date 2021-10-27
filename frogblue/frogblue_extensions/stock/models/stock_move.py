# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError

class StockMove(models.Model):
    _inherit = 'stock.move'

    def onchange(self, values, field_name, field_onchange):
        #Disabled due to performance issues when prodlots gets selected on stock move line.
        if field_name == 'move_line_ids':
            return {}
        return super(StockMove, self).onchange(values, field_name, field_onchange)
    
    def _process_intercompany_dest_moves(self):
        if not self or self.env.context.get('frog_skip_intercompany_moves', False):
            return False

        if not self.picking_id.sale_id.auto_purchase_order_id:
            return False

        deliveries = self.picking_id

        outgoing_move_ids = []
        incoming_move_ids = []
        processed_in_move_ids = []

        for delivery in deliveries:
            sale_order = delivery.sale_id

            if not sale_order:
                continue

            if sale_order.auto_purchase_order_id:
                purchases = sale_order.sudo().auto_purchase_order_id
            else:
                purchases = self.env['purchase.order'].sudo().search([('auto_sale_order_id','=',sale_order.id)])

            if not purchases:
                continue

            outgoing_move_ids.extend(delivery.move_lines.ids)

            for po in purchases:
                if not po.company_id.auto_validate_shipments or not po.company_id.intercompany_user_id:
                    continue

                if po.state in ('draft', 'sent', 'to approve'):
                    po.button_confirm()

                for in_picking in po.picking_ids:
                    if in_picking.picking_type_id.code != 'incoming' or in_picking.state != 'assigned':
                        continue

                    in_picking.move_lines.write({'scrapped':False})
                    incoming_move_ids.extend(in_picking.move_lines.ids)

        if not (incoming_move_ids and outgoing_move_ids):
            return False

        incoming_moves = self.env['stock.move'].sudo().browse(incoming_move_ids)

        moves_to_process = {
            1: outgoing_move_ids,
            2: []
        }

        for process_type in sorted(moves_to_process.keys()):
            moves_collection = moves_to_process[process_type]

            for out_move_id in moves_collection:
                out_move = self.env['stock.move'].sudo().browse(out_move_id)

                if not out_move.company_id.intercompany_user_id:
                    continue

                product = out_move.product_id
                done_out_qty = out_move.product_qty

                matching_in_moves = incoming_moves.filtered(
                    lambda el: el.product_id.id == product.id and el.quantity_done < el.reserved_availability
                )

                if not matching_in_moves:
                    continue

                if product.tracking == 'none':
                    for in_move in matching_in_moves:

                        if not in_move.company_id.intercompany_user_id:
                            continue

                        ic_uid = in_move.company_id.intercompany_user_id.id
                        in_move = in_move.sudo()
                        product = product.sudo()

                        done_out_qty_uom = product.uom_id._compute_quantity(done_out_qty, in_move.product_uom)
                        remaining_in_qty = in_move.reserved_availability - in_move.quantity_done

                        if done_out_qty_uom >= remaining_in_qty:
                            in_move.write({'quantity_done': in_move.reserved_availability})
                            done_out_qty_uom -= remaining_in_qty

                        else:
                            in_move.write({'quantity_done': in_move.quantity_done + done_out_qty_uom})
                            done_out_qty_uom = 0

                        processed_in_move_ids.append(in_move.id)

                        if done_out_qty_uom <= 0:
                            break

                        done_out_qty = in_move.product_uom._compute_quantity(done_out_qty_uom, product.uom_id)

                elif product.tracking in ('serial', 'lot'):

                    for out_move_line in out_move.move_line_ids:
                        if out_move_line.qty_done == 0:
                            continue

                        found_matching_in_line = False
                        out_line_qty_done = out_move_line.product_uom_id._compute_quantity(out_move_line.qty_done, product.uom_id)

                        for in_move in matching_in_moves:
                            if not in_move.company_id.intercompany_user_id:
                                continue

                            for in_move_line in in_move.move_line_ids.filtered(lambda el: el.qty_done == 0):
                                lines_matches = in_move_line.product_qty == out_line_qty_done if process_type == 1 else in_move_line.product_qty <= out_line_qty_done

                                if lines_matches:
                                    in_line_qty_done = product.uom_id._compute_quantity(out_line_qty_done, in_move_line.product_uom_id) if process_type == 1 else in_move_line.product_uom_qty

                                    in_move_line.write({
                                        'qty_done': in_line_qty_done,
                                        'lot_id': out_move_line.lot_id.id,
                                    })

                                    found_matching_in_line = True
                                    processed_in_move_ids.append(in_move.id)
                                    break

                            if found_matching_in_line:
                                break

                        if not found_matching_in_line and process_type == 1:
                            moves_to_process[2].append(out_move.id)

        processed_in_move_ids = list(set(processed_in_move_ids))

        if processed_in_move_ids:
            processed_in_moves = self.env['stock.move'].sudo().browse(processed_in_move_ids)
            processed_receipts = processed_in_moves.mapped('picking_id')

            for receipt in processed_receipts:

                if not receipt.company_id.intercompany_user_id:
                    continue

                button_res = receipt.with_context(frog_skip_intercompany_moves=True).button_validate()

                if isinstance(button_res, dict):
                    if button_res.get('res_id'):
                        wizard_id = button_res['res_id']
                        wizard_model = button_res['res_model']
                        transfer_wizard = self.env[wizard_model].sudo().browse(wizard_id)

                        if wizard_model == 'stock.immediate.transfer':
                            transfer_res = transfer_wizard.with_context(frog_skip_intercompany_moves=True).process()

                            if isinstance(transfer_res, dict):
                                if transfer_res.get('res_model', '') == 'stock.backorder.confirmation' and transfer_res.get('res_id', False):
                                    backorder_confirm = self.env['stock.backorder.confirmation'].sudo().browse(transfer_res['res_id'])
                                    backorder_confirm.with_context(frog_skip_intercompany_moves=True).process()

                        # elif wizard_model == 'stock.overprocessed.transfer':
                        #     transfer_wizard.with_context(frog_skip_intercompany_moves=True).action_confirm()

                        elif wizard_model == 'stock.backorder.confirmation':
                            transfer_wizard.with_context(frog_skip_intercompany_moves=True).process()

        return True

    def _action_done(self,cancel_backorder=False):
        res = super(StockMove,self)._action_done(cancel_backorder=False)
        self._process_intercompany_dest_moves()
        return res

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description):
        rslt = super(StockMove, self)._generate_valuation_lines_data(partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description)
        for r in rslt.items():
            if self.picking_id and self.picking_id.name and r[1].get('ref'):
                r[1]['ref'] = self.picking_id.name
        return rslt    


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    lot_id = fields.Many2one(
        'stock.production.lot', 'Lot/Serial Number',
        domain="[('product_id', '=', product_id)]", check_company=False)

    @api.onchange('lot_name', 'lot_id')
    def onchange_serial_number(self):
        # Disabled due to performance issues when prodlots gets selected on stock move line.
        if self.product_id.tracking == 'serial':
            if not self.qty_done:
                self.qty_done = 1
        return {}