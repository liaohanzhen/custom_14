# -*- coding: utf-8 -*-

from odoo import models, api, fields, tools
from dateutil.relativedelta import relativedelta
import math
from odoo.addons.mrp_workorder.models.mrp_production import MrpProduction

class MRPProduction(models.Model):
    _inherit = 'mrp.production'
    
    parent_id = fields.Many2one('mrp.production', 'Parent MO', index=True, ondelete='cascade')
    child_ids = fields.One2many('mrp.production', 'parent_id', 'Child Mos')
    
    @api.model
    def create(self,vals):
        if vals.get('origin'):
            origin = vals.get('origin').split(":")
            if len(origin)>=2:
                parent_mo = self.search([('name','=',origin[1])], limit=1)
                if parent_mo:
                    vals.update({'parent_id':parent_mo.id})
        res = super(MRPProduction, self).create(vals)
        
        return res
    
#     @api.multi
    def button_plan(self):
        res = super(MrpProduction, self).button_plan()
        WorkOrder = self.env['mrp.workorder']
        ProductUom = self.env['uom.uom']
        for order in self.filtered(lambda x: x.state == 'planned'):
            order.workorder_ids.write({'date_planned_start': False, 'date_planned_finished': False})

        # Schedule all work orders (new ones and those already created)
        all_mos = []
        production_obj = self.env['mrp.production']
        for order in self:
            if order in all_mos:
                continue
            def parse_mfg_childs(childs, parent, result={}, all_mos = [], parents= []):
                for child in childs:
                    all_mos.append(child)
                    if child.child_ids:
                        result.setdefault(child, []).append(child.child_ids)
                        parents.append(child)
                        parse_mfg_childs(child.child_ids, child, result, all_mos, parents)
            parents = []            
            result = {}
            parse_mfg_childs(order, False, result, all_mos, parents)
            new_result = {}
            for parent,childs in result.items():
                all_child = production_obj 
                for child in childs:
                    all_child+=child
                plan_orders = all_child+parent-order
                super(MrpProduction, plan_orders).button_plan()
                for o in plan_orders.filtered(lambda x: x.state == 'planned'):
                    o.workorder_ids.write({'date_planned_start': False, 'date_planned_finished': False})
                new_result[parent] = all_child
                
            parents.reverse()
            start_date_parent = order._get_start_date()
            already_processed_mo_ids = []
#             start_date = False
            total_parents = len(parents)
            for index,parent in enumerate(parents):
                child_mos = new_result.get(parent)
                if not child_mos:
                    start_date_parent = parent.process_order_planning(start_date_parent)
                    already_processed_mo_ids.append(parent.id)
                    continue
                #start_date = start_date_parent
                old_mo_start_date = start_date_parent
                for mo in child_mos:
                    if mo.id not in already_processed_mo_ids:
                        start_date = mo.process_order_planning(start_date_parent)
                        if old_mo_start_date < start_date:
                            old_mo_start_date = start_date
                        already_processed_mo_ids.append(mo.id)
#                 if not start_date:
#                     start_date = start_date_parent
                start_date_parent = old_mo_start_date
                if index+1 < total_parents:
                    if parent in new_result.get(parents[index+1]):
                        continue
                    else:
                        start_date_parent = parent.process_order_planning(start_date_parent)
                        already_processed_mo_ids.append(parent.id)
                else:
                    start_date_parent = parent.process_order_planning(start_date_parent)
                    already_processed_mo_ids.append(parent.id)
        return res
    
#     @api.multi
    def process_order_planning(self, start_date=False):
        self.ensure_one()
        WorkOrder = self.env['mrp.workorder']
        if not start_date:    
            start_date = self._get_start_date()
            
        from_date_set = False
        for workorder in self.workorder_ids:
            workcenter = workorder.workcenter_id
            wos = WorkOrder.search([('workcenter_id', '=', workcenter.id), ('date_planned_finished', '<>', False),
                                    ('state', 'in', ('ready', 'pending', 'progress')),
                                    ('date_planned_finished', '>=', start_date.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT))], order='date_planned_start')
            from_date = start_date
            intervals = workcenter.calendar_id.attendance_ids and workcenter.calendar_id.interval_get(from_date, workorder.duration_expected / 60.0)
            if intervals:
                to_date = intervals[-1][1]
                if not from_date_set:
                    from_date = intervals[0][0]
                    from_date_set = True
            else:
                to_date = from_date + relativedelta(minutes=workorder.duration_expected)
            # Check interval
            for wo in wos:
                if from_date < fields.Datetime.from_string(wo.date_planned_finished) and (to_date > fields.Datetime.from_string(wo.date_planned_start)):
                    from_date = fields.Datetime.from_string(wo.date_planned_finished)
                    intervals = workcenter.calendar_id.attendance_ids and workcenter.calendar_id.interval_get(from_date, workorder.duration_expected / 60.0)
                    if intervals:
                        to_date = intervals[-1][1]
                    else:
                        to_date = from_date + relativedelta(minutes=workorder.duration_expected)
            workorder.write({'date_planned_start': from_date, 'date_planned_finished': to_date})

            if (workorder.operation_id.batch == 'no') or (workorder.operation_id.batch_size >= workorder.qty_production):
                start_date = to_date
            else:
                qty = min(workorder.operation_id.batch_size, workorder.qty_production)
                cycle_number = math.ceil(qty / workorder.production_id.product_qty / workcenter.capacity)
                duration = workcenter.time_start + cycle_number * workorder.operation_id.time_cycle * 100.0 / workcenter.time_efficiency
                intervals = workcenter.calendar_id.attendance_ids and workcenter.calendar_id.interval_get(from_date, duration / 60.0)
                if intervals:
                    start_date = intervals[-1][1]
                else:
                    start_date = from_date + relativedelta(minutes=duration)
        
        return start_date
        
