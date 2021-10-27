# -*- coding: utf-8 -*-

from odoo import fields, models


class BaseConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    urgent_helpdesk_ticket_keyword = fields.Char(
        'Urgent Helpdesk Ticket Keyword',
        help='Default keyword to set ticket as urgent when creating ticket based on incoming mail.')

    urgent_quality_alert_keyword = fields.Char(
        'Urgent Quality Alert Keyword',
        help='Default keyword to set quality alert as urgent when creating Quality alert based on incoming mail.')

    #     @api.multi
    def set_urgent_helpdesk_ticket_keyword(self):
        return self.env['ir.values'].sudo().set_default(
            'res.config.settings', 'urgent_helpdesk_ticket_keyword', self.urgent_helpdesk_ticket_keyword)

    #     @api.multi
    def set_urgent_quality_alert_keyword(self):
        return self.env['ir.values'].sudo().set_default(
            'res.config.settings', 'urgent_quality_alert_keyword', self.urgent_quality_alert_keyword)
