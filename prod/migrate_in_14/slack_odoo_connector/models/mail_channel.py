# -*- coding: utf-8 -*-

from odoo import models, api, fields, tools,_
try:
    import slack
except ImportError:
    slack=None
    
try:
    from slackclient import SlackClient
except ImportError:
    SlackClient=None
import logging
_logger = logging.getLogger(__name__)
    
class Channel(models.Model):
    _inherit = 'mail.channel'
    
    channel_id = fields.Char('Channel Id')
    is_sl_channel = fields.Boolean('Is Slack Channel?', copy=False)
    is_sl_group = fields.Boolean('Is Slack Group?', copy=False)
    is_sl_im = fields.Boolean('Is Slack IM?', copy=False)
    is_sl_mpim = fields.Boolean('Is Slack Mpin?', copy=False)
    
    sl_channel_type = fields.Char('Slack Channel Type')
    
    
    @api.model
    def create(self, vals):
        res = super(Channel, self).create(vals)
        _logger.info('channel vals : '+ str(vals))
        if not res.channel_id and res.channel_type not in ['chat', 'livechat']:
            token = self.env.user.company_id.slack_token
            if not token:
                return res
            
            if slack:
                sc = slack.WebClient(token=token)
            else:
                sc = SlackClient(token)
            params = {'name': res.name.replace(' ','-'), }
            if res.public == 'private':
                params.update({'is_private' : True})
            
            channel_partners = res.channel_last_seen_partner_ids.mapped('partner_id')
            users = self.env['res.users'].with_context(active_test=False).sudo().search([('partner_id', "in", channel_partners.ids)], order='active desc')
            slack_member_ids = []
            for user in users:
                if user.member_id:
                    slack_member_ids.append(user.member_id)
                    continue
                user_email = user.email or user.login
                
                if slack:
                    slack_member = sc.users_lookupByEmail(email=user_email)
                    slack_member = slack_member.data
                else:
                    slack_member = sc.api_call('users.lookupByEmail',email=user_email)
                user_data = slack_member.get('user')
                if user_data:
                    odoo_user = self.env['res.company'].get_from_partner(user_data)
                    if odoo_user:
                        slack_member_ids.append(odoo_user.member_id)
                    
            if slack_member_ids:
                params.update({'user_ids': ','.join(slack_member_ids)})
                
            if slack:
                conversation_info = sc.conversations_create(**params)
                conversation_info = conversation_info.data
            else:
                conversation_info = sc.api_call('conversations.create',**params)
            
            channel_info = conversation_info.get('channel')
            res.write({'channel_id' : channel_info.get('id')})
                
        return res
    
    @api.model
    def slack_member_joined_channel(self,sc,member_data):
        slack_member_id = member_data.get('user')
        slack_channel_id = member_data.get('channel')
        
        odoo_channel = self.search([('channel_id','=', slack_channel_id)], limit=1)
        if not odoo_channel:
            odoo_channel = self.create_update_slack_channel(sc, slack_channel_id)
        
        odoo_user = self.env['res.users'].with_context(active_test=False).sudo().search([('member_id', "=", slack_member_id)], order='active desc', limit=1)
        if not odoo_user:
            if slack:
                slack_member = sc.users_info(user=slack_member_id)
                slack_member = slack_member.data
            else:
                slack_member = sc.api_call('users.info',user=slack_member_id)
                
            slack_member = slack_member.get('user')
            odoo_user = self.env['res.company'].get_from_partner(slack_member)
        if not odoo_user:
            return odoo_user
        
        channel_partner_obj  = self.env['mail.channel.partner'].sudo()
        channel_partner = channel_partner_obj.search([('partner_id', '=', odoo_user.partner_id.id), ('channel_id', '=', odoo_channel.id)], limit=1)
        if not channel_partner:
            channel_partner = channel_partner_obj.create({
                    'member_id': odoo_user.member_id,
                    'partner_email': odoo_user.email or odoo_user.login,
                    'display_name': odoo_user.name,
                    'partner_id': odoo_user.partner_id.id,
                    'channel_id': odoo_channel.id,
                    'is_pinned': True,
                })
        elif not channel_partner.member_id or not channel_partner.is_pinned:
            channel_partner.write({'member_id':odoo_user.member_id, 'is_pinned':True})    
        return odoo_user
    
    @api.model
    def slack_member_left_channel(self,channel_data):
        slack_member_id = channel_data.get('user')
        slack_channel_id = channel_data.get('channel')
        
        odoo_user = self.env['res.users'].with_context(active_test=False).sudo().search([('member_id', "=", slack_member_id)], order='active desc', limit=1)
        if not odoo_user:
            return True
        odoo_channel = self.search([('channel_id','=', slack_channel_id)], limit=1)
        if not odoo_channel:
            return True
        channel_partner = self.env['mail.channel.partner'].sudo().search([('partner_id', '=', odoo_user.partner_id.id), ('channel_id', '=', odoo_channel.id)], limit=1)
        if channel_partner:
            channel_partner.unlink()
        return True
        
    @api.model
    def create_slack_channel(self,channel_data):
        slack_channel_id = channel_data.get('id')
        channel_exist = self.search([('channel_id','=', slack_channel_id)], limit=1)
        if channel_exist:
            return channel_exist
        
        channel_name = channel_data.get('name')
        if not channel_name:
            return self
        
        alias_user = self.env['res.users'].with_context(active_test=False).sudo().search([('member_id','=',channel_data.get('creator'))], order='active desc', limit=1)
        channel_vals = {
                        'channel_id': channel_data.get('id'),
                        'name': channel_name,
                        'alias_user_id': alias_user and alias_user.id,
                        'is_subscribed': True,
                        'is_sl_channel': channel_data.get('is_channel'),
                        'is_sl_group': channel_data.get('is_group'),
                        'is_sl_im': channel_data.get('is_im'),
                        'is_sl_mpim':channel_data.get('is_mpim'),
                        }
        
        if channel_data.get('is_im') or channel_data.get('is_group'):
            channel_vals.update({'public': 'private',})
        if channel_data.get('is_im'):
            channel_vals.update({'channel_type': 'chat',})
        
        odoo_channel = self.search([('name', '=', channel_name)],limit=1) #,('channel_id','=',False)
        if not odoo_channel:
            odoo_channel = self.create(channel_vals)
        else:
            odoo_channel.write(channel_vals)
        return odoo_channel
    
    @api.model
    def create_update_slack_channel(self,sc,slack_channel_id, odoo_channel=None):
        self = self.sudo()
        channel_exist = self.search([('channel_id','=', slack_channel_id)], limit=1)
        if channel_exist:
            return channel_exist
        if slack:
            sl_channel = sc.conversations_info(channel=slack_channel_id)
            sl_channel = sl_channel.data
        else:
            sl_channel = sc.api_call('conversations.info',channel=slack_channel_id)
        channel_info = sl_channel.get('channel')
        if channel_info:
            try:
                if slack:
                    conversion_members = sc.conversations_members(channel=slack_channel_id)
                    conversion_members = conversion_members.data.get('members')
                else:
                    conversion_members = sc.api_call('conversations.members',channel=slack_channel_id)
                    conversion_members = conversion_members.get('members')
            except Exception as e:
                return
            
            users = self.env['res.users'].with_context(active_test=False).sudo().search([('member_id', 'in', conversion_members)])
            missing_user_ids = set(conversion_members) - set(users.mapped('member_id'))
            missing_user_ids = list(missing_user_ids)
            for member_id in missing_user_ids:
                if slack:
                    slack_member = sc.users_info(user=member_id)
                    slack_member = slack_member.data
                else:
                    slack_member = sc.api_call('users.info',user=member_id)
                    
                slack_member = slack_member.get('user')
                from_partner = self.env['res.company'].get_from_partner(slack_member)
                if from_partner:
                    users += from_partner
            
            channel_name = channel_info.get('name')
            member_names = []
            
            if not channel_name:
                for odoo_user in users:
                    member_names.append(odoo_user.name)
                channel_name = ','.join(member_names)
                
            odoo_user_id = self.env.user.id
            alias_user = self.env['res.users'].with_context(active_test=False).search([('member_id','=',channel_info.get('creator'))], order='active desc', limit=1)
            channel_vals = {
                            'channel_id': channel_info.get('id'),
                            'name': channel_name,
                            'alias_user_id': alias_user and alias_user.id or odoo_user_id,
                            'is_subscribed': True,
                            'is_sl_channel': channel_info.get('is_channel'),
                            'is_sl_group': channel_info.get('is_group'),
                            'is_sl_im': channel_info.get('is_im'),
                            'is_sl_mpim':channel_info.get('is_mpim'),
                            }
            
            if channel_info.get('is_im') or channel_info.get('is_group'):
                channel_vals.update({'public': 'private',})
            if channel_info.get('is_im'):
                channel_vals.update({'channel_type': 'chat',})
            if odoo_channel:
                odoo_channel.write(channel_vals)
            else:
                odoo_channel = self.search([('name', '=', channel_name)],limit=1) #, ('channel_id','=',False)
                if not odoo_channel:
                    odoo_channel = self.create(channel_vals)
                else:
                    odoo_channel.write(channel_vals)
            
            channel_partner_obj  = self.env['mail.channel.partner'].sudo()
            
            for odoo_user in users:
                channel_partner = channel_partner_obj.search([('partner_id', '=', odoo_user.partner_id.id), ('channel_id', '=', odoo_channel.id)], limit=1)
                if not channel_partner:
                    channel_partner = channel_partner_obj.create({
                            'member_id': odoo_user.member_id,
                            'partner_email': odoo_user.email or odoo_user.login,
                            'display_name': odoo_user.name,
                            'partner_id': odoo_user.partner_id.id,
                            'channel_id': odoo_channel.id,
                            'is_pinned': True,
                        })
                elif not channel_partner.member_id or not channel_partner.is_pinned:
                    channel_partner.write({'member_id':odoo_user.member_id, 'is_pinned':True})
            
        return odoo_channel
        
#     @api.multi
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, message_type='notification', **kwargs):
        message = super(Channel, self).message_post(message_type=message_type, **kwargs)
        token = self.env.user.company_id.slack_token
        if message and token and message_type=='comment':
            body = message.body
            if _("Odoo's chat helps employees collaborate efficiently") in body:
                return message
            #body = body.strip('<>/p')
            body = tools.html2plaintext(body).strip()
            
            if slack:
                sc = slack.WebClient(token=token)
            else:
                sc = SlackClient(token)
            for odoo_channel in self: 
                if odoo_channel.channel_id:
                    try:
                        user = self.env.user
                        slack_member = user.company_id.all_users_ids.filtered(lambda x:x.user_id==user.member_id)
                        if slack_member:
                            username = slack_member[0].name
                            if slack:
                                sc.chat_postMessage(channel=odoo_channel.channel_id, text=body,username=username, icon_emoji='true')
                            else:
                                sc.api_call('chat.postMessage',channel=odoo_channel.channel_id, text=body,username=username, icon_emoji='true')
                        else:
                            if slack:
                                sc.chat_postMessage(channel=odoo_channel.channel_id, text=body, icon_emoji='true')
                            else:
                                sc.api_call('chat.postMessage',channel=odoo_channel.channel_id, text=body, icon_emoji='true')
                    except Exception as e:
                        _logger.info(str(e))
                else:
                    user = self.env.user
                    channel_partners = odoo_channel.channel_partner_ids
                    users = self.env['res.users'].sudo().search([('member_id','!=', False), ('partner_id', 'in', channel_partners.ids)]) 
                    if users:
                        receiving_users = users.filtered(lambda x: x.partner_id.id!=message.author_id.id)
                        sending_user = users - receiving_users
                        sl_user_ids = ','.join(receiving_users.mapped('member_id'))
                        try:
                            if slack:
                                slack_channel = sc.conversations_open(users=sl_user_ids)
                            else:
                                slack_channel = sc.api_call('conversations.open',users=sl_user_ids)
                        except Exception as e:
                            _logger.info('conversations.open error: '+str(e))
                            return message
                        slack_channel_id = slack_channel.get('channel',{}).get('id')
                                
                        if not sending_user:
                            sending_user = user
                        else:
                            sending_user = sending_user[0]
                            
                        slack_member = user.company_id.all_users_ids.filtered(lambda x:x.user_id==sending_user.member_id)
                        try:
                            if slack_member:
                                username = slack_member[0].name
                                if slack:
                                    sc.chat_postMessage(channel=slack_channel_id, text=body,username=username, icon_emoji='true')
                                else:
                                    sc.api_call('chat.postMessage',channel=slack_channel_id, text=body,username=username, icon_emoji='true')
                            else:
                                if slack:
                                    sc.chat_postMessage(channel=slack_channel_id, text=body, icon_emoji='true')
                                else:
                                    sc.api_call('chat.postMessage',channel=slack_channel_id, text=body, icon_emoji='true')
                            
                            self.create_update_slack_channel(sc,slack_channel_id, odoo_channel)
                        except Exception as e:
                            _logger.info('chat.postMessage error: '+str(e))
                            
        return message
