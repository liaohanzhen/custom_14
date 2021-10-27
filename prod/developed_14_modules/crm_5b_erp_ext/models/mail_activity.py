# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date #, datetime
#from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class MailActivity(models.Model):
    _inherit= 'mail.activity'
    
    @api.onchange('activity_type_id')
    def _onchange_activity_type_id(self):
        return