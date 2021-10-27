# -*- coding: utf-8 -*-

from odoo import models
import uuid

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'
    
    def _generate_access_token(self):
        return str(uuid.uuid4())