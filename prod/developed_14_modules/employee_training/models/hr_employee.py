# -*- coding: utf-8 -*-
from odoo import models,fields,api
from odoo.exceptions import Warning

class HREmployee(models.Model):
    _inherit = 'hr.employee'
    
    training_ids = fields.One2many("training.training",'employee_id',"Employee Trainings")