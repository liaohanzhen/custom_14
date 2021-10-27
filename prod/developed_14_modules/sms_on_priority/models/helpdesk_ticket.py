# -*- coding: utf-8 -*-

from odoo import models, api, fields, tools


class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'

    urgent_keyword = fields.Char("Automatically set as urgent if email contains the keyword : ", default='urgent')
    send_sms_if_urgent = fields.Boolean("Send SMS if ticket is urgent (3 stars)?")


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    sms_sent = fields.Boolean("SMS Sent ?", default=False, copy=False)

    @api.model
    def create(self, vals):
        res = super(HelpdeskTicket, self).create(vals)
        if vals.get('priority', '') == '3' and res.team_id.send_sms_if_urgent and not res.sms_sent and res.team_id:
            members = res.sudo().team_id.member_ids
            if members:
                partners = members.mapped('partner_id').filtered(lambda x: x.mobile)
                template = self.env.ref("sms_on_priority.sms_template_helpdesk_ticket", False)
                partners.send_sms_to_partner(res, template)
                if partners:
                    res.write({'sms_sent': True})
        #             partners = res.message_follower_ids.mapped('partner_id')
        #             #partners = partners - self.env.user.partner_id
        #             partners = partners.filtered(lambda x:x.mobile)
        #             template = self.env.ref("sms_on_priority.sms_template_helpdesk_ticket",False)
        #             partners.send_sms_to_partner(res,template)
        #             if partners:
        #                 res.write({'sms_sent':True})
        return res

    #     @api.multi
    def write(self, vals):
        res = super(HelpdeskTicket, self).write(vals)
        if vals.get('priority', '') == '3':
            for ticket in self:
                if ticket.sms_sent or not ticket.team_id.member_ids or not ticket.team_id.send_sms_if_urgent:
                    continue
                members = ticket.sudo().team_id.member_ids
                partners = members.mapped('partner_id').filtered(lambda x: x.mobile)
                # partners = partners - self.env.user.partner_id
                template = self.env.ref("sms_on_priority.sms_template_helpdesk_ticket", False)
                partners.send_sms_to_partner(ticket, template)
                if partners:
                    super(HelpdeskTicket, ticket).write({'sms_sent': True})

        #                 partners = ticket.message_follower_ids.mapped('partner_id')
        #                 partners = partners - self.env.user.partner_id
        #                 partners = partners.filtered(lambda x:x.mobile)
        #                 template = self.env.ref("sms_on_priority.sms_template_helpdesk_ticket",False)
        #                 partners.send_sms_to_partner(ticket,template)
        #                 if partners:
        #                     super(HelpdeskTicket,ticket).write({'sms_sent':True})
        return res

    @api.model
    def message_new(self, msg, custom_values=None):
        body = msg.get('body', '')
        values = dict(custom_values or {}, description_html=body)

        if custom_values and custom_values.get('team_id'):
            team = self.env['helpdesk.team'].sudo().search([('id', '=', custom_values.get('team_id'))], limit=1)
            default_keyword = team.urgent_keyword
            if default_keyword and (
                    default_keyword.lower() in body.lower() or default_keyword.lower() in msg.get('subject',
                                                                                                  '').lower()):
                values['priority'] = '3'
        if msg.get('cc'):
            message_follower_ids = values.get('message_follower_ids') or []  # webclient can send None or False
            for cc_email in msg.get('cc').split(","):
                cc_email = cc_email.strip()
                if cc_email:
                    cc_email = tools.email_split(cc_email)
                    if not cc_email:
                        continue
                    cc_email = cc_email[0]
                    partner_exist = self.env['res.partner'].sudo().search([('email', '=', cc_email)], limit=1)
                    if not partner_exist:
                        try:
                            partner_exist = self.env['res.partner'].sudo().create(
                                {'email': cc_email, 'name': cc_email, 'customer': 1})
                        except Exception:
                            pass
                    if partner_exist:
                        message_follower_ids += [(0, 0, fol_vals) for fol_vals in
                                                 self.env['mail.followers']._add_default_followers(self._name, [],
                                                                                                   [partner_exist.id],
                                                                                                   customer_ids=[])[0][
                                                     0]]
            if message_follower_ids:
                values['message_follower_ids'] = message_follower_ids
        return super(HelpdeskTicket, self).message_new(msg, custom_values=values)

#     @api.multi
#     def send_sms_to_partner(self, record, template=None):
#         template = self.env.ref("sms_template_helpdesk_ticket",False)
#         if not template:
#             return
#         default_mobile = template.from_mobile_verified_id 
#         if not default_mobile:
#             default_mobile = self.env['sms.number'].search([('mobile_number','!=', False),('account_id','!=',False)],limit=1)
#         if not default_mobile:
#             return
#         sms_subtype = self.env['ir.model.data'].get_object('sms_frame', 'sms_subtype')
#         template_obj = self.env['sms.frame.template']
#         message_obj = self.env['sms.message']
#         for partner in self:
#             if not partner.mobile:
#                 continue
#             sms_rendered_content = template_obj.render_template(template.template_body, template.model_id.model, record.id)
#             my_sms = default_mobile.account_id.send_message(default_mobile.mobile_number, partner.mobile, sms_rendered_content.encode('utf-8'), template.model_id.model, record.id, template.media_id, media_filename=template.media_filename)
#             attachments = []
#             if template.media_id:
#                 attachments.append((template.media_filename, base64.b64decode(template.media_id)) )
#             message_obj.create({'record_id': record.id,
#                                 'model_id':template.model_id.id,
#                                 'account_id':default_mobile.account_id.id,
#                                 'from_mobile':default_mobile.mobile_number,
#                                 'to_mobile':partner.mobile,
#                                 'sms_content':sms_rendered_content,
#                                 'status_string':my_sms.response_string, 
#                                 'direction':'O',
#                                 'message_date':datetime.utcnow(), 
#                                 'status_code':my_sms.delivary_state, 
#                                 'sms_gateway_message_id':my_sms.message_id, 
#                                 'by_partner_id':self.env.user.partner_id.id})
#                 
#             record.message_post(body=sms_rendered_content, subject="SMS Sent", message_type="comment", subtype_id=sms_subtype.id, attachments=attachments)
