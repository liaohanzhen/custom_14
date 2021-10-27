# -*- coding: utf-8 -*-
from odoo import models,fields,api

class TrainingPackage(models.Model):
    _name = 'training.package'
    
    name = fields.Char("Name",required=1)
    training_template_ids = fields.Many2many("training.template",'training_package_template_rel','package_id','template_id',"Templates")
    
