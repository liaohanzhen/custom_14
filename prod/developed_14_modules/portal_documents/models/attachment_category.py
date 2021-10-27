# -*- coding: utf-8 -*-

from odoo import fields, models

class AttachmentCategory(models.Model):
    _name = 'attachment.category'
    _description = "Attachment Categories"
    _order = "sequence, name"

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(help="Gives the sequence order when displaying a list of attachment categories.")
