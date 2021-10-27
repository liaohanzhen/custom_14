# -*- coding: utf-8 -*-
import time
import logging
from datetime import datetime
from collections import defaultdict
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class Picking(models.Model):
    _inherit = "stock.picking"

    force_date = fields.Datetime('Force Date')
    
#     @api.multi
    def action_set_stock_force_date(self):
        AccountMove = self.env['account.move']
        for picking in self:
            if not picking.force_date:
                continue
            Quants = self.env['stock.quant']
#             for move in picking.move_lines:
                #Quants += move.quant_ids.write({'in_date':picking.force_date})
#                 Quants |= move.quant_ids
            if Quants:
                Quants.write({'in_date':picking.force_date})
            picking.move_lines.write({'date': picking.force_date})
            picking.write({'date_done':picking.force_date})
            account_moves = AccountMove.search([('ref','=',picking.name)])
            if account_moves:
                date = picking.force_date #datetime.strptime(picking.force_date, '%Y-%m-%d %H:%M:%S')
                account_moves.write({'date':date})
                account_moves.mapped('line_ids').write({'date':date})
        return
    
class Quant(models.Model):
    _inherit = "stock.quant"
    
    @api.model
    def _quant_create_from_move(self, qty, move, lot_id=False, owner_id=False,
                                src_package_id=False, dest_package_id=False,
                                force_location_from=False, force_location_to=False):
        quant = super(Quant,self)._quant_create_from_move(qty, move, lot_id, owner_id,
                                src_package_id, dest_package_id,force_location_from, force_location_to)
        if move.picking_id.force_date:
            quant.write({'in_date': move.picking_id.force_date})
        return quant
    
#     @api.model
#     def quants_move(self, quants, move, location_to, location_from=False, lot_id=False, owner_id=False,
#                     src_package_id=False, dest_package_id=False, entire_pack=False):
#         """Moves all given stock.quant in the given destination location.  Unreserve from current move.
#         :param quants: list of tuple(browse record(stock.quant) or None, quantity to move)
#         :param move: browse record (stock.move)
#         :param location_to: browse record (stock.location) depicting where the quants have to be moved
#         :param location_from: optional browse record (stock.location) explaining where the quant has to be taken
#                               (may differ from the move source location in case a removal strategy applied).
#                               This parameter is only used to pass to _quant_create_from_move if a negative quant must be created
#         :param lot_id: ID of the lot that must be set on the quants to move
#         :param owner_id: ID of the partner that must own the quants to move
#         :param src_package_id: ID of the package that contains the quants to move
#         :param dest_package_id: ID of the package that must be set on the moved quant
#         """
#         # TDE CLEANME: use ids + quantities dict
#         if location_to.usage == 'view':
#             raise UserError(_('You cannot move to a location of type view %s.') % (location_to.name))
# 
#         quants_reconcile_sudo = self.env['stock.quant'].sudo()
#         quants_move_sudo = self.env['stock.quant'].sudo()
#         check_lot = False
#         for quant, qty in quants:
#             if not quant:
#                 # If quant is None, we will create a quant to move (and potentially a negative counterpart too)
#                 quant = self._quant_create_from_move(
#                     qty, move, lot_id=lot_id, owner_id=owner_id, src_package_id=src_package_id,
#                     dest_package_id=dest_package_id, force_location_from=location_from, force_location_to=location_to)
#                 if move.picking_id.force_date:
#                     quant.write({'in_date': move.picking_id.force_date})
#                 check_lot = True
#             else:
#                 _logger.info(quant)
#                 quant._quant_split(qty)
#                 _logger.info(quant)
#                 quants_move_sudo |= quant
#             quants_reconcile_sudo |= quant
# 
#         if quants_move_sudo:
#             moves_recompute = quants_move_sudo.filtered(lambda self: self.reservation_id != move).mapped(
#                 'reservation_id')
#             quants_move_sudo._quant_update_from_move(move, location_to, dest_package_id, lot_id=lot_id,
#                                                      entire_pack=entire_pack)
#             moves_recompute.recalculate_move_state()
# 
#         if location_to.usage == 'internal':
#             # Do manual search for quant to avoid full table scan (order by id)
#             self._cr.execute("""
#                 SELECT 0 FROM stock_quant, stock_location WHERE product_id = %s AND stock_location.id = stock_quant.location_id AND
#                 ((stock_location.parent_left >= %s AND stock_location.parent_left < %s) OR stock_location.id = %s) AND qty < 0.0 LIMIT 1
#             """, (move.product_id.id, location_to.parent_left, location_to.parent_right, location_to.id))
#             if self._cr.fetchone():
#                 quants_reconcile_sudo._quant_reconcile_negative(move)
# 
#         # In case of serial tracking, check if the product does not exist somewhere internally already
#         # Checking that a positive quant already exists in an internal location is too restrictive.
#         # Indeed, if a warehouse is configured with several steps (e.g. "Pick + Pack + Ship") and
#         # one step is forced (creates a quant of qty = -1.0), it is not possible afterwards to
#         # correct the inventory unless the product leaves the stock.
#         picking_type = move.picking_id and move.picking_id.picking_type_id or False
#         if check_lot and lot_id and move.product_id.tracking == 'serial' and (
#             not picking_type or (picking_type.use_create_lots or picking_type.use_existing_lots)):
#             other_quants = self.search([('product_id', '=', move.product_id.id), ('lot_id', '=', lot_id),
#                                         ('qty', '>', 0.0), ('location_id.usage', '=', 'internal')])
#             if other_quants:
#                 # We raise an error if:
#                 # - the total quantity is strictly larger than 1.0
#                 # - there are more than one negative quant, to avoid situations where the user would
#                 #   force the quantity at several steps of the process
#                 if sum(other_quants.mapped('qty')) > 1.0 or len([q for q in other_quants.mapped('qty') if q < 0]) > 1:
#                     lot_name = self.env['stock.production.lot'].browse(lot_id).name
#                     raise UserError(_('The serial number %s is already in stock.') % lot_name + _(
#                         "Otherwise make sure the right stock/owner is set."))

#     @api.multi
    def _quant_update_from_move(self, move, location_dest_id, dest_package_id, lot_id=False, entire_pack=False):
        super(Quant, self)._quant_update_from_move(move, location_dest_id, dest_package_id, lot_id,
                                                   entire_pack)
        if move.picking_id.force_date:
            self.write({'in_date': move.picking_id.force_date})

    def _create_account_move_line(self, move, credit_account_id, debit_account_id, journal_id):
        # group quants by cost
        quant_cost_qty = defaultdict(lambda: 0.0)
        for quant in self:
            quant_cost_qty[quant.cost] += quant.qty
        AccountMove = self.env['account.move']
        for cost, qty in quant_cost_qty.items():
            move_lines = move._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id)
            if move_lines:
                if move.picking_id.force_date:
                    date = move.picking_id.force_date #datetime.strptime(move.picking_id.force_date, '%Y-%m-%d %H:%M:%S')
                else:
                    date = self._context.get('force_period_date', fields.Date.context_today(self))
                new_account_move = AccountMove.create({
                    'journal_id': journal_id,
                    'line_ids': move_lines,
                    'date': date,
                    'ref': move.picking_id.name})
                new_account_move.post()


class StockMove(models.Model):
    _inherit = "stock.move"
    
#     @api.multi
#     def action_done(self):
    def _action_done(self, cancel_backorder=False):
        res = super(StockMove, self)._action_done()
        pickings = self.env['stock.picking']
        for move in self:
            if move.picking_id and move.picking_id.force_date:
                pickings |= move.picking_id
                move.write({'date': move.picking_id.force_date})
            for link in move.linked_move_operation_ids:
                if link.operation_id.picking_id and link.operation_id.picking_id.force_date:
                    pickings |= link.operation_id.picking_id
        for picking in pickings:
            if picking.state=='done':
                picking.write({'date_done':picking.force_date})
        return res
    
