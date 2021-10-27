# -*- coding: utf-8 -*-
from odoo import models, fields


class MailMessage(models.Model):
    _inherit = 'mail.message'

    sms_number_id = fields.Many2one('sms.number', "SMS Stored Number")
    sms_mobile_number = fields.Char("SMS From Mobile Number", related="sms_number_id.mobile_number", store=True)
    to_mobile = fields.Char("SMS To Mobile Number")

    def _get_message_format_fields(self):
        res = super(MailMessage, self)._get_message_format_fields()
        return res + ['sms_number_id', 'sms_mobile_number', 'to_mobile']
