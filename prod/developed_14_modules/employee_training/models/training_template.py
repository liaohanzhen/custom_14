# -*- coding: utf-8 -*-
from odoo import models,fields,api
from datetime import datetime
class TrainingTemplate(models.Model):
    _name = 'training.template'
    
    name = fields.Char("Name", required=1)
    equipment_id = fields.Many2one("maintenance.equipment", "Equipment")
    department_id = fields.Many2one("hr.department","Department")
    is_recurring = fields.Boolean("Is recurring")
    frequency_days = fields.Integer("Frequency (days)")
    training_content = fields.Html("Training content")
    history_ids = fields.One2many('training.template.history','template_id','History')
    validity_duration = fields.Integer("Validity duration(nb of days)")
    iframe_url = fields.Char("iFrame URL")
    deadline_days = fields.Integer("Deadline Days")
    
    @api.model
    def create(self, vals):
        res = super(TrainingTemplate, self).create(vals)
        self.env['training.template.history'].create({'template_id':res.id, 'date':datetime.now(),'user_id':self._uid})
        return res
#     @api.multi
    def write(self, vals):
        res = super(TrainingTemplate, self).write(vals)
        for template in self:
            self.env['training.template.history'].create({'template_id':template.id, 'date':datetime.now(),'user_id':self._uid})
        return res
    
class TrainingTemplateHistory(models.Model):
    _name = 'training.template.history'
    _order = 'date desc'
    
    template_id = fields.Many2one("training.template",'Training Template')
    date = fields.Datetime("Date")
    user_id = fields.Many2one("res.users","User")
    