# -*- coding: utf-8 -*-
from collections import defaultdict

from odoo import models

class StockMove(models.Model):
    _inherit = "stock.move"

    def _create_quality_checks(self):
        # Used to avoid duplicated quality points
        quality_points_list = set([])

        pick_moves = defaultdict(lambda: self.env['stock.move'])
        for move in self:
            pick_moves[move.picking_id] |= move
        quality_check_obj = self.env['quality.check']
        for picking, moves in pick_moves.items():
            for check in picking.sudo().check_ids:
                point_key = (check.picking_id.id, check.point_id.id, check.team_id.id, check.product_id.id)
                quality_points_list.add(point_key)
            quality_points = self.env['quality.point'].sudo().search([
                ('picking_type_id', '=', picking.picking_type_id.id),
                '|', ('product_id', 'in', moves.mapped('product_id').ids),
                '&', ('product_id', '=', False), ('product_tmpl_id', 'in', moves.mapped('product_id').mapped('product_tmpl_id').ids)])
            seqial_tracking_point_products = defaultdict(lambda: self.env['product.product'])
            for point in quality_points:
                if point.source_location_ids and point.dest_location_ids:
                    if picking.location_id.id not in point.source_location_ids.ids or picking.location_dest_id.id not in point.dest_location_ids.ids:
                        continue
                elif point.source_location_ids and picking.location_id.id not in point.source_location_ids.ids:
                    continue
                elif point.dest_location_ids and picking.location_dest_id.id not in point.dest_location_ids.ids:
                    continue
                
                if point.check_execute_now():
                    if point.product_id:
                        #Added cusom code Nilesh
                        if point.product_id.tracking=='serial':
                            seqial_tracking_point_products[point] |= point.product_id
                            continue
                        
                        point_key = (picking.id, point.id, point.team_id.id, point.product_id.id)
                        if point_key in quality_points_list:
                            continue
                        quality_check_obj.sudo().create({
                            'picking_id': picking.id,
                            'point_id': point.id,
                            'team_id': point.team_id.id,
                            'product_id': point.product_id.id,
                        })
                        quality_points_list.add(point_key)
                    else:
                        products = picking.move_lines.filtered(lambda move: move.product_id.product_tmpl_id == point.product_tmpl_id).mapped('product_id')
                        for product in products:
                            #Added cusom code Nilesh
                            if product.tracking=='serial':
                                seqial_tracking_point_products[point] |= product 
                                continue
                            point_key = (picking.id, point.id, point.team_id.id, product.id)
                            if point_key in quality_points_list:
                                continue
                            quality_check_obj.sudo().create({
                                'picking_id': picking.id,
                                'point_id': point.id,
                                'team_id': point.team_id.id,
                                'product_id': product.id,
                            })
                            quality_points_list.add(point_key)
            #Added cusom code Nilesh
            #lot_obj = self.env['stock.production.lot']
            #operation_lot_obj = self.env['stock.pack.operation.lot']
            for point, products in seqial_tracking_point_products.items():
                for product in products:
                    exist_quality_checks = quality_check_obj.search([('picking_id','=',picking.id),('point_id','=',point.id),('team_id','=',point.team_id.id),('product_id','=',product.id)])
                    #total_product_qty = sum(moves.filtered(lambda x:x.product_id.id==product.id).mapped("product_uom_qty"))
                    total_product_qty = sum(picking.move_lines.filtered(lambda x:x.product_id.id==product.id).mapped("product_uom_qty"))
                    
                    if point.quality_check_percent:
                        total_product_qty = round(point.quality_check_percent*total_product_qty/100)
                        
                    #pack_operation = picking.pack_operation_product_ids.filtered(lambda x:x.product_id.id==product.id)
                    if len(exist_quality_checks) < total_product_qty:
                        qc_need_to_create = int(total_product_qty - len(exist_quality_checks))
                        if picking.backorder_id:
                            backorder_qty_done = sum(picking.backorder_id.pack_operation_product_ids.filtered(lambda x:x.product_id.id==product.id).mapped('qty_done'))
                            if point.quality_check_percent:
                                backorder_qty_done = round(point.quality_check_percent*backorder_qty_done/100.0)
                                
                            exist_quality_checks_backorder = quality_check_obj.search([('picking_id','=',picking.backorder_id.id),('point_id','=',point.id),('team_id','=',point.team_id.id),('product_id','=',product.id)], order='id')
                            if len(exist_quality_checks_backorder) > backorder_qty_done:
                                extra_qc_backorder = exist_quality_checks_backorder[int(backorder_qty_done):]
                                if extra_qc_backorder:
                                    extra_qc_backorder[:qc_need_to_create].write({'picking_id' : picking.id})
                                    qc_need_to_create = qc_need_to_create - len(extra_qc_backorder)
                                    
                        
                        for i in range(0,qc_need_to_create):
                            #lot = lot_obj.create({'product_id': product.id,'product_qty':1,})
#                             if pack_operation and pack_operation.product_qty < pack_operation.qty_done:
#                                 operation_lot_obj.create({'operation_id':pack_operation.id, 'lot_id':lot.id,'lot_name' : lot.name,})
                            quality_check_obj.sudo().create({
                                            'picking_id': picking.id,
                                            'point_id': point.id,
                                            'team_id': point.team_id.id,
                                            'product_id': product.id,
                                            #'lot_id' :lot.id,
                                        })
                            