# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'
    
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        message = super(MailThread, self).message_post(**kwargs)
        if not kwargs:
            kwargs = {}
        if kwargs.get('rating_feedback'):
            message.mail_ids.write({'email_to':'sales@frogblue.com'})
        return message
        