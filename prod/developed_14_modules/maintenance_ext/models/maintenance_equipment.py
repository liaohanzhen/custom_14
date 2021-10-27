# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'
    
    iframe_url = fields.Char("iFrame URL")
    tool_number = fields.Char("Tool Number")
    
    @api.model
    def create(self, vals):
        vals['tool_number'] = self.env['ir.sequence'].next_by_code('maintenance.equipment.tool.number')
        record = super(MaintenanceEquipment, self).create(vals)
        return record