# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models, modules, SUPERUSER_ID, tools
from odoo.exceptions import UserError, AccessError
class Message(models.Model):
    """ Messages model: system notification (replacing res.log notifications),
        comments (OpenChatter discussion) and incoming emails. """
    _inherit = 'mail.message'

    @api.model
    def create(self, values):
        if 'model' in values or 'res_id' in values:
            if values.get('model', False) == 'helpdesk.ticket' and not values.get('message_type', False) == 'notification':
                if values.get('res_id', False):
                    ticket = self.env['helpdesk.ticket'].search([('id', '=', values.get('res_id',False)),'|',('active','=',False),('stage_id.is_close','=',True)])
                    if ticket:
                        ticket.write({'active':True})
                        stage= self.env['helpdesk.stage'].search([('team_ids','in',ticket.team_id.id)],order='sequence')
                        if stage:
                            ticket.write({'stage_id': stage[0].id})

        return super(Message, self).create(values)