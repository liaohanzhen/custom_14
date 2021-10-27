# -*- coding: utf-8 -*-

from odoo import models, fields, api
from lxml import etree

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self.env.user.has_group('frogblue_warehouse_exteral_user.warehouse_exteral_user'):
            wh_loc_ids = self.env.user.warehouse_ids.mapped('lot_stock_id').ids
            domain = ['|',('location_dest_id', 'in', wh_loc_ids),('location_id','in', wh_loc_ids)]
            return super().search(domain + args, offset=offset, limit=limit,order=order, count=count)
        else:
            return super().search(args, offset=offset, limit=limit,order=order, count=count)
        
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form',toolbar=False, submenu=False):
        res = super(StockPicking, self).fields_view_get(view_id=view_id, view_type=view_type,toolbar=toolbar, submenu=submenu)
        
        if self.env.user.has_group('frogblue_warehouse_exteral_user.warehouse_exteral_user'):   
            get_field_list = []
            all_fields = self._fields
            for i in all_fields:
                if all_fields.get(i).type in ['many2one']:  #'one2many'
                    get_field_list.append(i)
            
            doc = etree.fromstring(res['arch'])
            for modify_field in get_field_list:
                field_elem = doc.xpath("//field[@name='" + modify_field + "']") or []
                for ele in field_elem:
                    ele.set("widget", "selection")
          
            res['arch'] = etree.tostring(doc)
        return res
