# -*- coding: utf-8 -*-

from odoo import models, fields

class ProjectProjectType(models.Model):
    _name = 'project.project.type'
    
    name = fields.Char("Name")
    image = fields.Binary("Image", attachment=True)
    sequence_id = fields.Many2one('ir.sequence', 'Reference Sequence')
    active = fields.Boolean('Active', default=True)
