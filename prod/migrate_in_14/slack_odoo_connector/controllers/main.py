# -*- coding: utf-8 -*-

try:
    import slack
except ImportError:
    slack=None
try:
    from slackclient import SlackClient
except ImportError:
    SlackClient=None


from odoo import http
from odoo.http import request
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)


class SlackWebhooks(http.Controller):

    @http.route('/slack/event_api_payload_webhook/<int:company_id>', auth="public", type='json', methods=['POST'])
    def get_slack_event_apis_payload(self, company_id,**kw):
        
        json_data = request.jsonrequest
        _logger.info("json_data :"+str(json_data))
        if json_data.get('type','')=='url_verification':
            return "<Response>%s</Response>"%(json_data.get('challenge'))
        
        try:
            company = request.env['res.company'].sudo().search([('id','=',int(company_id))])
            if not company:
                return "<Response></Response>"
        except Exception as e:
            _logger.info("Json error :"+str(e))
        
        if company.slack_token:
            event_data = json_data.get('event',{})
            token = company.slack_token
            mail_channel_obj = request.env['mail.channel'].sudo()
            
            if slack:
                client = slack.WebClient(token=token)
            else:
                client = SlackClient(token)
                    
            #new message
            if event_data.get('type','')=='message':
                client_msg_id = event_data.get('client_msg_id')
                if not client_msg_id:
                    return "<Response></Response>"
                mail_message = request.env['mail.message'].sudo().search([('client_message_id', '=', client_msg_id)])
                if mail_message:
                    return "<Response></Response>"
                
                slack_channel_id = event_data.get('channel')
                slack_user_id = event_data.get('user','')
                
                ts = float(event_data.get('ts',0.0))
                date_time = datetime.fromtimestamp(ts)
                chat = event_data.get('text','').strip("<@" + slack_user_id + ">")
                
                odoo_slack_member = company.all_users_ids.filtered(lambda x:x.user_id==slack_user_id)
                from_partner = None
                user_obj = request.env['res.users'].sudo()
                company_obj = request.env['res.company'].sudo()
                
                channel_ids = []
                recipient_partners = []
                
                member_email=None
                if not odoo_slack_member:
                    if slack:
                        slack_member = client.users_info(user=event_data.get('user'))
                        slack_member = slack_member.data
                    else:
                        slack_member = client.api_call('users.info',user=event_data.get('user'))
                        
                    slack_member = slack_member.get('user')
                    from_partner = company_obj.get_from_partner(slack_member)
                    if not from_partner:
                        return "<Response></Response>"
                    
                    member_email = slack_member.get('profile',{}).get('email')
                    
                    odoo_slack_member = request.env['slack.users'].sudo().create({
                                "name": slack_member.get('profile',{}).get('real_name'),
                                "email": member_email,
                                "user_id": slack_member.get('id'),
                                "user_ids": company.id,
                            })
                else:
                    odoo_slack_member = odoo_slack_member[0]
                    
                if not from_partner:
                    from_partner = user_obj.with_context(active_test=False).search([('member_id', "=", odoo_slack_member.user_id)], order='active desc', limit=1)
                    if not from_partner:
                        if slack:
                            slack_member = client.users_info(user=event_data.get('user'))
                            slack_member = slack_member.data
                        else:
                            slack_member = client.api_call('users.info',user=event_data.get('user'))
                            
                        slack_member = slack_member.get('user')
                        from_partner = company_obj.get_from_partner(slack_member)
                        if not from_partner:
                            return "<Response></Response>"
                        
                recipient_partners.append(from_partner.partner_id.id)
                
                odoo_channel = mail_channel_obj.create_update_slack_channel(client,slack_channel_id)
                channel_ids.append(odoo_channel.id)
                
                message_vals = {
                    'message_type': "comment",
                    "subtype_id": request.env.ref("mail.mt_comment").id,
                    'subject': chat,
                    'date': date_time,
                    'body': chat,
                    'needaction_partner_ids': [(4, from_partner.partner_id.id)],
                    'client_message_id': client_msg_id,
                    'email_from': member_email or from_partner.email,
                    'channel_ids': [[6, 0, channel_ids]],
                    'partner_ids': [[6, 0, recipient_partners]],
                    'member_id': odoo_slack_member.user_id,
                    'model': 'mail.channel',
                    'res_id': odoo_channel.id,
                    'author_id': from_partner.partner_id.id,
                    
                }    
                if 'files' in event_data:
                    attachment_ids = company_obj.getAttachments(event_data, token)            
                    message_vals.update({'attachment_ids': [[6, 0, attachment_ids]],})
                    
                odoo_message = request.env['mail.message'].sudo().with_context(from_slack_webhook=True).create(message_vals)
                if odoo_message:
                    notifications = []
                    message_values = odoo_message.message_format()[0]
                    for partner in odoo_channel.channel_partner_ids:
                        notifications.append([
                            (request.db, 'res.partner', partner.id),
                            {'type': 'author', 'message': dict(message_values)}
                        ])
                        request.env['bus.bus'].sendmany(notifications)
            elif event_data.get('type','')=='channel_created':
                channel_data = event_data.get('channel')
                mail_channel_obj.create_slack_channel(channel_data)
            elif event_data.get('type','')=='member_joined_channel':
                mail_channel_obj.slack_member_joined_channel(client,event_data)
            elif event_data.get('type','')=='member_left_channel':
                mail_channel_obj.slack_member_left_channel(event_data)    
                                    
        return "<Response></Response>"
    