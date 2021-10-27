# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    equipment_count = fields.Integer(compute='_compute_equipment_count', string='# of Equipments')
    
    def _compute_equipment_count(self):
        for employee in self:
            if employee.user_id:
                employee.equipment_count = self.env['maintenance.equipment'].search_count([('technician_user_id','=',employee.user_id.id)])
            else:
                employee.equipment_count=0
    
    def employee_assigned_equipments(self):
        self.ensure_one()
        action = self.env.ref('maintenance.hr_equipment_action',False)
        result = action and action.read()[0] or {}
        ctx = dict() #self._context.copy()
        ctx.update({'default_technician_user_id':self.user_id.id})
        result['context'] = ctx
        result['domain'] = [('technician_user_id', '=', self.user_id.id)]
        return result