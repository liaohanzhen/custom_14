# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, Warning
from datetime import datetime
import requests
import base64

try:
    import slack
except ImportError:
    slack=None
    
try:
    from slackclient import SlackClient
except ImportError:
    SlackClient=None
from slack.errors import SlackApiError
    
class SlackCompanyToken(models.Model):
    """
    This Class will store members and channels of slack
    """

    _inherit = 'res.company'

    slack_token = fields.Char()
    all_users_ids = fields.One2many('slack.users', 'user_ids', string="All Users")
    all_group_ids = fields.One2many('slack.group', 'group_ids', string="Channels")
    slack_team_id = fields.Char('Slack Team')
    
    @api.model
    def get_from_partner(self, slack_member):
        member_email = slack_member.get('profile',{}).get('email')
        if not member_email:
            return None
        
        user_obj = self.env['res.users']
        
        from_partner = user_obj.with_context(active_test=False).sudo().search([('member_id', "=", slack_member.get('id'))], order='active desc', limit=1)
        if not from_partner:     
            from_partner = user_obj.with_context(active_test=False).sudo().search([('login', "=", member_email)], order='active desc', limit=1)
        
#        if not from_partner:
#            from_partner = user_obj.sudo().create({
#                'member_id': slack_member.get('id'),
#                'email': member_email,
#                'login': member_email,
#                'name': slack_member.get('profile',{}).get('real_name'),
#            })
        
        if from_partner and not from_partner.member_id:
            from_partner.sudo().write({'member_id':slack_member.get('id')})
        
        return from_partner
    
#     @api.multi
    def import_slack_channels_and_users(self):
        if self.slack_token:
            token = self.slack_token
            mail_channel_obj = self.env['mail.channel']
            channel_partner_obj  = self.env['mail.channel.partner']
            
            if slack:
                sc = slack.WebClient(token=token)
            else:
                sc = SlackClient(token)
                
            if slack:
                slack_channels = sc.conversations_list(exclude_archived=1,types='public_channel, private_channel, mpim, im',limit=500)
                slack_member = sc.users_list() #sc.api_call('users.list', channel=channel.get('id'))
                slack_member = slack_member.data
                
            else:
                slack_channels = sc.api_call('conversations.list',exclude_archived=1,types='public_channel, private_channel, mpim, im',limit=500)
                slack_member = sc.api_call('users.list')
            
            slack_odoo_member_dict = {}
            for member in slack_member.get('members',[]):
                if member.get('deleted') or member.get('is_bot'):
                    continue
                #member_email = member.get('profile',{}).get('email')
                from_partner = self.get_from_partner(member)
                if not from_partner:
                    continue
                slack_odoo_member_dict.update({member.get('id'):from_partner})
                    
            slack_channels = slack_channels.get("channels")
            odoo_user_id = self.env.user.id    
            for channel in slack_channels:
                if channel.get('is_archived'):
                    continue
                try:
                    if slack:
                        conversion_members = sc.conversations_members(channel=channel.get('id'))
                        conversion_members = conversion_members.data.get('members')
                    else:
                        conversion_members = sc.api_call('conversations.members',channel=channel.get('id'))
                        conversion_members = conversion_members.get('members')
                except Exception as e:
                    continue
                if not conversion_members:
                    continue
                
                channel_name = channel.get("name")
                if not channel_name:
                    member_names = []
                    for cm_id in conversion_members:
                        odoo_user = slack_odoo_member_dict.get(cm_id)
                        if odoo_user:
                            member_names.append(odoo_user.name)
                    channel_name = ','.join(member_names)
                        
                channel_members = [member for member in slack_member.get('members',[]) if member.get('id') in conversion_members]
                alias_user = slack_odoo_member_dict.get(channel.get('creator'))
                channel_vals = {
                                'name': channel_name,
                                'alias_user_id': alias_user and alias_user.id or odoo_user_id,
                                'is_subscribed': True,
                                'is_sl_channel': channel.get('is_channel'),
                                'is_sl_group': channel.get('is_group'),
                                'is_sl_im': channel.get('is_im'),
                                'is_sl_mpim':channel.get('is_mpim'),
                                }
                
                if channel.get('is_im') or channel.get('is_group'):
                    channel_vals.update({'public': 'private',})
                if channel.get('is_im'):
                    channel_vals.update({'channel_type': 'chat',})
                            
                odoo_channel = mail_channel_obj.search([('channel_id', '=', channel.get('id'))],limit=1)
                if not odoo_channel:
                    odoo_channel = mail_channel_obj.search([('name', '=', channel_name)],limit=1)
                    channel_vals.update({'channel_id': channel.get('id'),})
                if not odoo_channel:
                    odoo_channel = mail_channel_obj.create(channel_vals)
                else:
                    odoo_channel.write(channel_vals)
                
                for member in channel_members:
                    if member.get('deleted') or member.get('is_bot'):
                        continue
                    from_partner = slack_odoo_member_dict.get(member.get('id'))
                            
                    if not from_partner:
                        from_partner = self.get_from_partner(member)
                    if not from_partner:
                        continue
                    
                    channel_partner = channel_partner_obj.search([('partner_id', '=', from_partner.partner_id.id), ('channel_id', '=', odoo_channel.id)], limit=1)
                    if not channel_partner:
                        member_email = member.get('profile',{}).get('email')
                        channel_partner = channel_partner_obj.create({
                                'member_id': member.get('id'),
                                'partner_email': member_email,
                                'display_name': member.get('profile',{}).get('real_name'),
                                'partner_id': from_partner.partner_id.id,
                                'channel_id': odoo_channel.id,
                                'is_pinned': True,
                            })
                    elif not channel_partner.member_id or not channel_partner.is_pinned:
                        channel_partner.write({'member_id':member.get('id'), 'is_pinned':True})    
        return True
                                    
#     @api.multi
    def slack_token_verify(self):
        """
        This method will verify slack token and create records of members and channels from slack to Odoo
        :return:
        """
        if self.slack_token:
            token = self.slack_token
            if slack:
                sc = slack.WebClient(token=token)
            else:
                sc = SlackClient(token)
            
            attachment_ids = []
            #slack_channels = sc.channels_list(exclude_archived=1) #sc.api_call("channels.list", exclude_archived=1)
            if slack:
                slack_channels = sc.conversations_list(exclude_archived=1,types='public_channel, private_channel, mpim, im',limit=500)
                slack_member = sc.users_list() #sc.api_call('users.list', channel=channel.get('id'))
                slack_member = slack_member.data
            else:
                slack_channels = sc.api_call('conversations.list',exclude_archived=1,types='public_channel, private_channel, mpim, im',limit=500)
                slack_member = sc.api_call('users.list')
                
            slack_channels = slack_channels.get("channels")
            
            slack_odoo_member_dict = {}
            for member in slack_member.get('members',[]):
                if member.get('deleted') or member.get('is_bot'):
                    continue
                member_email = member.get('profile',{}).get('email')
                from_partner = self.get_from_partner(member)
                if not from_partner:
                    continue
                slack_odoo_member_dict.update({member.get('id'):from_partner})
                
            if slack_channels:
                mail_channel_obj = self.env['mail.channel']
                channel_partner_obj  = self.env['mail.channel.partner']
                message_obj = self.env['mail.message']
                odoo_user_id = self.env.user.id
                self.all_group_ids.unlink()
                for channel in slack_channels:
                    if channel.get('is_archived'):
                        continue
                    try:
                        if slack:
                            conversion_members = sc.conversations_members(channel=channel.get('id'))
                            conversion_members = conversion_members.data.get('members')
                        else:
                            conversion_members = sc.api_call('conversations.members',channel=channel.get('id'))
                            conversion_members = conversion_members.get('members')
                    except Exception as e:
                        continue
                    if not conversion_members:
                        continue
                    channel_members = [member for member in slack_member.get('members',[]) if member.get('id') in conversion_members]
                    
                    channel_name = channel.get("name")
                    if not channel_name:
                        member_names = []
                        for cm_id in conversion_members:
                            odoo_user = slack_odoo_member_dict.get(cm_id)
                            if odoo_user:
                                member_names.append(odoo_user.name)
                        channel_name = ','.join(member_names)
                        
                    
                    channel_ids = []
                    
                    alias_user = slack_odoo_member_dict.get(channel.get('creator'))
                    channel_vals = {
                                    'name': channel_name,
                                    'alias_user_id': alias_user and alias_user.id or odoo_user_id,
                                    'is_subscribed': True,
                                    'is_sl_channel': channel.get('is_channel'),
                                    'is_sl_group': channel.get('is_group'),
                                    'is_sl_im': channel.get('is_im'),
                                    'is_sl_mpim':channel.get('is_mpim'),
                                    }
                    
                    if channel.get('is_im') or channel.get('is_group'):
                        channel_vals.update({'public': 'private',})
                    if channel.get('is_im'):
                        channel_vals.update({'channel_type': 'chat',})
                                
                    odoo_channel = mail_channel_obj.search([('channel_id', '=', channel.get('id'))],limit=1)
                    if not odoo_channel:
                        odoo_channel = mail_channel_obj.search([('name', '=', channel_name)],limit=1)
                        channel_vals.update({'channel_id': channel.get('id'),})
                    if not odoo_channel:
                        odoo_channel = mail_channel_obj.create(channel_vals)
                    else:
                        odoo_channel.write(channel_vals)
                    channel_ids.append(odoo_channel.id)
                        
                    if channel_members:
                        if slack:
                            history = sc.conversations_history(channel=channel.get('id'),limit=500)
                            history = history.data
                        else:
                            history = sc.api_call('conversations.history',channel=channel.get('id'),limit=500)
                        
                        history_messages = history.get('messages',[])
                        while history.get('has_more') and history.get('response_metadata',{}).get('next_cursor'):
                            if slack:
                                history = sc.conversations_history(channel=channel.get('id'),limit=500,cursor=history.get('response_metadata',{}).get('next_cursor'))
                                history = history.data
                            else:
                                history = sc.api_call('conversations.history',channel=channel.get('id'),limit=500,cursor=history.get('response_metadata',{}).get('next_cursor'))
                            history_messages += history.get('messages',[])
                        
                        for member in channel_members:
                            if member.get('deleted') or member.get('is_bot'):
                                continue
                            
                            recipient_partners = []
                            member_email = member.get('profile',{}).get('email')
                            from_partner = slack_odoo_member_dict.get(member.get('id'))
                            
                            if not from_partner:
                                from_partner = self.get_from_partner(member)
                            if not from_partner:
                                continue
                            
                            recipient_partners.append(from_partner.partner_id.id)
                            
                            channel_partner = channel_partner_obj.search([('partner_id', '=', from_partner.partner_id.id), ('channel_id', '=', odoo_channel.id)], limit=1)
                            if not channel_partner:
                                channel_partner = channel_partner_obj.create({
                                        'member_id': member.get('id'),
                                        'partner_email': member_email,
                                        'display_name': member.get('profile',{}).get('real_name'),
                                        'partner_id': from_partner.partner_id.id,
                                        'channel_id': odoo_channel.id,
                                        'is_pinned': True,
                                    })
                            elif not channel_partner.member_id or not channel_partner.is_pinned:
                                channel_partner.write({'member_id':member.get('id'), 'is_pinned':True})
                                
                            member_messages = [x for x in history_messages if x.get('client_msg_id') and x.get('user')==member.get('id')]
                            
                            for message in member_messages: #history.get('messages',[]):
                                #if 'client_msg_id' in message:
                                ts = float(message.get('ts',0.0))
                                date_time = datetime.fromtimestamp(ts)
                                c_msg_id = message.get('client_msg_id')

                                if 'files' in message:
                                    attachment_ids = self.getAttachments(message, token)

                                chat = message.get('text','').strip("<@" + member.get('id','') + ">")
                                
                                mail_message = message_obj.search([('client_message_id', '=', c_msg_id)])
                                if mail_message:
                                    continue                                    
                                else:
                                    message_obj.with_context(from_slack_webhook=True).create({
                                        'subject': chat,
                                        'date': date_time,
                                        'body': chat,
                                        'client_message_id': c_msg_id,
                                        'email_from': member_email,
                                        'channel_ids': [[6, 0, channel_ids]],
                                        'partner_ids': [[6, 0, recipient_partners]],
                                        'attachment_ids': [[6, 0, attachment_ids]],
                                        'member_id': message.get('user'),
                                        'model': 'res.partner',
                                        'res_id': from_partner.partner_id.id,
                                        'author_id': from_partner.partner_id.id
                                    })

                                # message_list.append(odoo_message.id)
                                self.env.cr.commit()
                    if channel_name:
                        group = self.env['slack.group'].create({"name": channel_name,})
                        self.all_group_ids = [group.id]
                
                if len(self.all_group_ids) == 0:
                    raise UserError('No Group Found from this Token')
            else:
                raise UserError("No Group Found")
            
            members = slack_member.get('members')
            if members:
                self.all_users_ids.unlink()
                for member in members:
                    if member.get('deleted'):
                        continue
                    profile = member.get('profile')
                    if profile.get("email"):
                        user = self.env['slack.users'].create({
                            "name": profile.get('real_name'),
                            # "display_name": profile['display_name'] if profile['display_name'] else profile['real_name'],
                            "email": profile.get('email'),
                            "user_id": member.get('id'),
                            "user_ids": self.id,
                        })
                        #self.all_users_ids = [user.id]
                
                if len(self.all_users_ids) == 0:
                    raise UserError('No User Found from this Token')
        else:
            raise Warning("Token missing, Please Enter the Slack Token")



    def getAttachments(self, slack_attachments, token):
        sl_attachments = slack_attachments.get('files',[])
        attachment_ids = []
        request_header = {"Authorization": "Bearer {}".format(token)}
        
        for sl_attachment in sl_attachments:
            name = sl_attachment.get('name')
            url = sl_attachment.get('url_private','')
            if 'name' not in sl_attachment or not url:
                continue
            
            res = requests.get(url,headers=request_header)
            if res.status_code!=200:
                continue
            content = base64.b64encode(res.content)
            content= content.decode()
            
            odoo_attachment = self.env['ir.attachment'].create({
                'datas': sl_attachment.get('contentBytes'),
                'name': sl_attachment.get("name"),
                'datas_fname': sl_attachment.get("name")})
            
            attachment_ids.append(odoo_attachment.id)
        return attachment_ids
