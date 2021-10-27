# -*- coding: utf-8 -*-

from odoo import models, api, fields


class QualityAlertTeam(models.Model):
    _inherit = 'quality.alert.team'

    member_ids = fields.Many2many('res.users', string='Team Members', domain=lambda self: [
        ('groups_id', 'in', self.env.ref('quality.group_quality_user').id)])
    urgent_keyword = fields.Char("Automatically set as urgent if email contains the keyword : ", default='urgent')
    send_sms_if_urgent = fields.Boolean("Send SMS if Quality alert is urgent (3 stars)?")


class QualityAlert(models.Model):
    _inherit = 'quality.alert'

    sms_sent = fields.Boolean("SMS Sent ?", default=False, copy=False)

    @api.model
    def message_new(self, msg, custom_values=None):
        body = msg.get('body', '')
        if custom_values and custom_values.get('team_id'):
            team = self.env['quality.alert.team'].sudo().search([('id', '=', custom_values.get('team_id'))], limit=1)
            default_keyword = team.urgent_keyword
            if default_keyword and (
                    default_keyword.lower() in body.lower() or default_keyword.lower() in msg.get('subject',
                                                                                                  '').lower()):
                values = dict(custom_values or {}, priority='3')

        return super(QualityAlert, self).message_new(msg, custom_values=values)

    @api.model
    def create(self, vals):
        res = super(QualityAlert, self).create(vals)
        if vals.get('priority',
                    '') == '3' and res.team_id.send_sms_if_urgent and not res.sms_sent and res.team_id.member_ids:
            members = res.sudo().team_id.member_ids
            if members:
                partners = members.mapped('partner_id').filtered(lambda x: x.mobile)
                template = self.env.ref("sms_on_priority.sms_template_quality_alert", False)
                partners.send_sms_to_partner(res, template)
                if partners:
                    res.write({'sms_sent': True})

        #             partners = res.message_follower_ids.mapped('partner_id')
        #             partners = partners - self.env.user.partner_id
        #             partners = partners.filtered(lambda x:x.mobile)
        #             template = self.env.ref("sms_on_priority.sms_template_quality_alert",False)
        #             partners.send_sms_to_partner(res,template)
        #             if partners:
        #                 res.write({'sms_sent':True})
        return res

    #     @api.multi
    def write(self, vals):
        res = super(QualityAlert, self).write(vals)
        if vals.get('priority', '') == '3':
            for alert in self:
                if alert.sms_sent or not alert.team_id.member_ids or not res.team_id.send_sms_if_urgent:
                    continue

                members = alert.sudo().team_id.member_ids
                partners = members.mapped('partner_id').filtered(lambda x: x.mobile)
                # partners = partners - self.env.user.partner_id
                template = self.env.ref("sms_on_priority.sms_template_quality_alert", False)
                partners.send_sms_to_partner(alert, template)
                if partners:
                    super(QualityAlert, alert).write({'sms_sent': True})

        #                 partners = ticket.message_follower_ids.mapped('partner_id')
        #                 partners = partners - self.env.user.partner_id
        #                 partners = partners.filtered(lambda x:x.mobile)
        #                 template = self.env.ref("sms_on_priority.sms_template_quality_alert",False)
        #                 partners.send_sms_to_partner(ticket,template)
        #                 if partners:
        #                     super(QualityAlert,ticket).write({'sms_sent':True})
        return res
