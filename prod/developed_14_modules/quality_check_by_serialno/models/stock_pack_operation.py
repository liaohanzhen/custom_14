# -*- coding: utf-8 -*-
from odoo import api, models

class PackOperationLot(models.Model):
    _inherit = "stock.pack.operation.lot"
    
    @api.model
    def create(self, vals):
        res = super(PackOperationLot, self).create(vals)
        pack = res.operation_id
        Lot = self.env['stock.production.lot']
        if pack.product_id.tracking == 'serial' and pack.picking_id and pack.picking_id.check_ids:
            picking = pack.picking_id
            if not res.lot_id: 
                lot = Lot.create({'name': res.lot_name, 'product_id': pack.product_id.id})
                res.write({'lot_id': lot.id})
            pack_lots = pack.pack_lot_ids.filtered(lambda x:x.qty >0.0).mapped('lot_id')
            if not pack_lots:
                pack_lots = pack.pack_lot_ids.mapped('lot_id')
                
            quality_checks = picking.check_ids.filtered(lambda x:x.product_id.id==pack.product_id.id)
            
#             pack_operation_products = picking.pack_operation_product_ids.filtered(lambda x:x.product_id.id==pack.product_id.id)
#             pack_lots = pack_operation_products.mapped('pack_lot_ids').mapped('lot_id')
            
            alloted_quality_checks = quality_checks.filtered(lambda x:x.lot_id.id in pack_lots.ids)
            unalloted_quality_checks = quality_checks - alloted_quality_checks
            
            quality_check_lots = alloted_quality_checks.mapped('lot_id')
            unalloted_lot = pack_lots - quality_check_lots
            for i in range(min([len(unalloted_quality_checks),len(unalloted_lot)])):
                unalloted_quality_checks[i].write({'lot_id':unalloted_lot[i].id})
        return res
    
    def write(self, vals):
        if 'lot_id' in vals:
            new_lot_id = vals.get('lot_id',False)
            for pack_lot in self:
                if pack_lot.lot_id and pack_lot.operation_id.product_id.tracking == 'serial' and pack_lot.operation_id.picking_id:
                    try:
                        #pack_lot.lot_id.unlink()
                        pack_lot.operation_id.picking_id.check_ids.filtered(lambda x:x.product_id.id==pack_lot.operation_id.product_id.id and x.lot_id.id==pack_lot.lot_id.id).write({'lot_id':new_lot_id})
                    except Exception:
                        pass
        res = super(PackOperationLot, self).write(vals)
        return res
    
    def unlink(self):
        for pack_lot in self:
            if pack_lot.lot_id and pack_lot.operation_id.product_id.tracking == 'serial' and pack_lot.operation_id.picking_id: #and pack_lot.operation_id.picking_id.check_ids.filtered(lambda x:x.product_id.id==pack_lot.operation_id.product_id.id and x.lot_id.id==pack_lot.lot_id.id)
                try:
                    #pack_lot.lot_id.unlink()
                    pack_lot.operation_id.picking_id.check_ids.filtered(lambda x:x.product_id.id==pack_lot.operation_id.product_id.id and x.lot_id.id==pack_lot.lot_id.id).write({'lot_id':False})
                except Exception:
                    pass
        return super(PackOperationLot,self).unlink()
    
    