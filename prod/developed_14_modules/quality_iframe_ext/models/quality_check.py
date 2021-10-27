# -*- coding: utf-8 -*-
from odoo import models,fields, api

class QualityCheck(models.Model):
    _inherit = 'quality.check'
    
    iframe_url = fields.Char("iFrame URL",related="point_id.iframe_url",store=True)

class QualityAlert(models.Model):
    _inherit = 'quality.alert'
    
    color = fields.Integer('Color', compute="change_colore_on_kanban", store=True)
    
    @api.depends('priority')
    def change_colore_on_kanban(self):
        """    this method is used to change color index base on priority status
        :return: index of color for kanban view    """    
        for record in self:
            color = 0
            if not record.priority or record.priority=='0':
                color=0
            elif record.priority == '1':
                color = 12
            elif record.priority == '2':
                color = 11
            elif record.priority == '3':
                color = 14
            record.color = color
    