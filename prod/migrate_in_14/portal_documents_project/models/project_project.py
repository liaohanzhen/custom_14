# -*- coding: utf-8 -*-

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    portal_attachment_ids = fields.One2many('portal.user.attachment', 'res_id', domain=lambda self:[('res_model', '=', self._name)], string='Portal Attachments')
    
