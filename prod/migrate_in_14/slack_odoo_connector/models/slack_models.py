# -*- coding: utf-8 -*-

from odoo import models, fields, api
try:
    import slack
except ImportError:
    slack=None
    
try:
    from slackclient import SlackClient
except ImportError:
    SlackClient=None

from odoo.exceptions import ValidationError
from odoo.osv import osv

import re
#import time
#from email.utils import parsedate_tz, mktime_tz
import logging
_logger = logging.getLogger(__name__)

_image_dataurl = re.compile(r'(data:image/[a-z]+?);base64,([a-z0-9+/]{3,}=*)([\'"])', re.I)


class SlackCompanyAllUsers(models.Model):
    _name = 'slack.users'

    name = fields.Char(string="Name")
    email = fields.Char(string="Email")
    display_name = fields.Char(string="Display Name")
    user_id = fields.Char(string="User ID")
    user_ids = fields.Many2one('res.company')


class SlackCompanyAllGroups(models.Model):
    _name = 'slack.group'

    name = fields.Char(string="Name")
    group_ids = fields.Many2one('res.company')


class SlackAllUsers(models.Model):
    _name = 'slack.all.users'

    name = fields.Char(string="Name")
    email = fields.Char(string="Email")
    display_name = fields.Char(string="Display Name")
    user_id = fields.Char(string="User ID")
    user_ids = fields.Many2one('res.company')
    channel = fields.Char('Channel')
        
class MailChannelPartner(models.Model):

    _inherit = 'mail.channel.partner'

    member_id = fields.Char('Member_id')
    #is_slack = fields.Boolean(compute=' _is_slack_member ')


class MailChannelUser(models.Model):

    _inherit = 'res.users'

    member_id = fields.Char('Member_id')
    is_slack = fields.Boolean(compute='_is_slack_member')
    # is_invite = fields.Char(compute='send_invite')
    is_invite = fields.Char("Message")
    
#     @api.multi
    def _is_slack_member(self):
        for user in self:
            if user.member_id:
                user.is_slack = True
                user.is_invite = ("User also exist on Slack")
            else:
                user.is_slack = False


    def send_invitation(self):
        if self.env.user.company_id.slack_token:
            token = self.env.user.company_id.slack_token
            #token = self.env['res.company'].search([]).slack_token
            #sc = SlackClient(token)
            if slack:
                sc = slack.WebClient(token=token)
            else:
                sc = SlackClient(token)
            if sc:
                if slack:
                    channels = sc.channels_list(exclude_archived=1) #sc.api_call('channels.list')
                else:
                    channels = sc.api_call('channels.list')
                
                email = self.email
                if re.match("^.+@([?)[a-zA-Z0-9-.]+.([a-zA-Z]{2,3}|[0-9]{1,3})(]?)$)", email):
                    for channel in channels.get('channels',[]):
                        if channel.get('name','').upper() == 'GENERAL':
                            user = sc.api_call('users.admin.invite', email=email)
                            if 'error' in user:
                                raise osv.except_osv(" Invitation is already sent ")
                            else:
                                raise osv.except_osv(('Success'), ("Invitation is successfully sent"))
                        
                else:
                    raise osv.except_osv(("Sorry!"), ("Invalid Email Address"))
        else:
            _logger.info("Invalid Token, Sorry! Token is missing!.")
            #raise osv.except_osv(('Invalid Token'),('Sorry! Token is missing!'))


class MailMessage(models.Model):

    _inherit = 'mail.message'
    client_message_id = fields.Char('Client Message Id')
    member_id = fields.Char('Slack Member Id')
    message_id = fields.Char('Message Id')


#     @api.model
#     def invite(self,values):
#         print('')
#         print(values)
    
#     @api.model
#     def create(self, values):
#         return super(MailMessage, self).create(values)
#     
#         if values.get('body','')=='Contact created' or\
#          values.get('model','') not in ['mail.channel','res.partner'] or\
#           'client_message_id' in values or self._context.get('from_slack_webhook'):
#             return super(MailMessage, self).create(values)
#         slack_token = self.env.user.company_id.slack_token
#         if not slack_token or "subjects" in values:
#             return super(MailMessage, self).create(values)
# 
#         body = values.get('body')
#         token = self.env.user.company_id.slack_token
#         
#         body = body.strip('<>/p')
#         if values.get('model','') == 'mail.channel':
#             if values.get('message_type','') == 'comment':
#                 odoo_channel = self.env['mail.channel'].search([('id', '=', values.get('res_id'))])
#                 if odoo_channel and odoo_channel.channel_id:
#                     if slack:
#                         sc = slack.WebClient(token=token)
#                     else:
#                         sc = SlackClient(token)
#                     
#                     try:
#                         user = self.env.user
#                         slack_member = user.company_id.all_users_ids.filtered(lambda x:x.user_id==user.member_id)
#                         if slack_member:
#                             username = slack_member[0].name
#                             if slack:
#                                 sc.chat_postMessage(channel=odoo_channel.channel_id, text=body,username=username, icon_emoji='true')
#                             else:
#                                 sc.api_call('chat.postMessage',channel=odoo_channel.channel_id, text=body,username=username, icon_emoji='true')
#                         else:
#                             if slack:
#                                 sc.chat_postMessage(channel=odoo_channel.channel_id, text=body, icon_emoji='true')
#                             else:
#                                 sc.api_call('chat.postMessage',channel=odoo_channel.channel_id, text=body, icon_emoji='true')
#                             
#                     except Exception as e:
#                         _logger.info(str(e))
                        
#                     sc = slack.WebClient(token=token)
#                     slack_channels = sc.channels_list(exclude_archived=1)["channels"] #sc.api_call("channels.list", exclude_archived=1)["channels"]
#                     slack_user = sc.users_list() #sc.api_call("users.list")
#                     slack_user = slack_user.data
#         
#                     from_partner = self.env.user #self.env['res.users'].search([('email', '=', self.env.user.email)])
#                     to_channel = odoo_channel
#                     #from_partner = from_partner[0] if from_partner else from_partner
#                     found = False
#                     #if to_channel:
#                     real_name = None
#                     email = from_partner.email
#                     if email:
#                         head, sep, tail = email.partition('@')
#                         
#                     #if values.get('message_type','') == 'comment':
#                     users = slack_user #sc.api_call("users.list")
#                     i = 0
#                     check = 0
#                     if 'members' in users:
#                         for member in users.get('members',[]):
#                             if member.get('deleted'):
#                                 continue
#                             i = i + 1
#                     
#                     for channel in slack_channels:
#                         if channel.get('name') == odoo_channel.name:
#                             if 'members' in users:
#                                 for member in users.get('members',[]):
#                                     if member.get('deleted'):
#                                         continue
#                                     if member.get('name') == head:
#                                         real_name = member.get('real_name')
#                                         sc.chat_postMessage(channel=odoo_channel.channel_id, text=body, username=real_name, icon_emoji='true')
#                                         break
#                                     else:
#                                         check = check + 1
#                                         if check == i:
#                                             raise osv.except_osv(('Invalid User'), ("Please invite user to slack."))
#                                         continue
# 
#                             found = True
#                             break
# 
#                         else:
#                             continue
#                     if not found:
#                         partners = self.env['res.users'].search([])
#                         for part in partners:
#                             to_part_channel = self.env['mail.channel'].search([('id', '=', values.get('res_id'))], limit=1)
#                             if to_part_channel and part.name in list(to_part_channel['display_name'].split(',')):
#                                 if part.name == self.env.user.name:
#                                     continue
#                                 else:
#                                     channel_partner = part
#                                     from_partner = self.env['res.users'].search([('email', '=', self.env.user.email)])
#                                     to_channel = self.env['mail.channel'].search([(('id'), '=', values.get('res_id'))])
#                                     from_partner = from_partner[0] if from_partner else from_partner
#                                     if channel_partner:
#                                         partner_id = channel_partner.partner_id.id
#                                         partner_name = channel_partner.name
#                                     to_partner = self.env['mail.channel.partner'].search(
#                                         [('partner_id', '=', partner_id),
#                                          ('channel_id', '=', to_channel.id),
#                                          ('channel_id', 'not in', [1, 2])])
#                                     if not to_partner:
#                                         to_partner = self.env['mail.channel.partner'].create({
#                                             'partner_email': channel_partner.email,
#                                             'display_name': partner_name,
#                                             'partner_id': partner_id,
#                                             'channel_id': to_channel.id,
#                                             'is_pinned': True,
#                                         })
# 
#                                     if to_partner and to_partner.get('display_name') == partner_name:
#                                         if values.get('message_type') == 'comment':
# 
#                                             for user in slack_user.get('members',[]):
#                                                 if user.get('deleted'):
#                                                     continue
#                                                 # slack_name = [channel.get('name').upper() for channel in slack_channels]
#                                                 if to_partner.get('display_name','').upper() == \
#                                                         user.get('profile',{}).get('real_name').upper():
# #                                                                         self.env['mail.channel.partner'].write({
# #                                                                             'partner_email': user.get('profile',{}).get('email'),
# #                                                                             'display_name': user.get('profile',{}).get('real_name'),
# #                                                                             'partner_id': partner_id,
# #                                                                             'channel_id': to_channel.id,
# #                                                                             'is_pinned': True,
# #                                                                         })
# 
#                                                     userChannel = sc.im_open(user=user.get('id'))
#                                                     if userChannel:
#                                                         real_name = None
#                                                         email = from_partner.email
#                                                         if email:
#                                                             head, sep, tail = email.partition('@')
#                                                         users = slack_user #sc.api_call("users.list")
#                                                         i = 0
#                                                         check = 0
#                                                         if 'members' in users:
#                                                             for member in users.get('members'):
#                                                                 if member.get('deleted'):
#                                                                     continue
#                                                                 i = i + 1
#                                                         
#                                                         if 'members' in users:
#                                                             for member in users.get('members',[]):
#                                                                 if member.get('name','') == head:
#                                                                     real_name = member.get('real_name')
#                                                                     sc.chat_postMessage(channel=userChannel.get('channel').get('id'), text=body, username=real_name, icon_emoji='true')
#                                                                     break
#                                                                 else:
#                                                                     check = check + 1
#                                                                     if check == i:
#                                                                         raise osv.except_osv(
#                                                                             ('Invalid User'), (
#                                                                                 "Please invite user to slack."))
#                                                                     continue
#                                                         
#                                                     found = True
#                                                     break
#                                                 else:
#                                                     continue
#                                             if not found:
#                                                 raise ValueError('user does not found')
                            
                    
#                 else:
#                     partners = self.env['res.users'].search([])
#                     for part in partners:
#                         to_part_channel = self.env['mail.channel'].search([(('id'), '=', values.get('res_id'))], limit=1)
#                         if to_part_channel and part.name in list(to_part_channel['display_name'].split(',')):
#                             if part.name == self.env.user.name:
#                                 continue
#                             else:
#                                 channel_partner = part
#                                 from_partner = self.env['res.users'].search([('email', '=', self.env.user.email)])
#                                 to_channel = self.env['mail.channel'].search([(('id'), '=', values.get('res_id'))])
#                                 from_partner = from_partner[0] if from_partner else from_partner
#                                 # channel_partner = self.env['mail.channel'].search([('id', '=', values['res_id'])])
#                                 if channel_partner:
#                                     partner_id = channel_partner.partner_id.id
#                                     partner_name = channel_partner.name
#                                 to_partner = self.env['mail.channel.partner'].search(
#                                     [('partner_id', '=', partner_id),
#                                      ('channel_id', '=', to_channel.id),
#                                      ('channel_id', 'not in', [1, 2])])
#                                 if not to_partner:
#                                     to_partner = self.env['mail.channel.partner'].create({
#                                         'partner_email': channel_partner.email,
#                                         'display_name': partner_name,
#                                         'partner_id': partner_id,
#                                         'channel_id': to_channel.id,
#                                         'is_pinned': True,
#                                     })
# 
#                                 if to_partner and to_partner.get('display_name','') == partner_name:
#                                     if values.get('message_type','') == 'comment':
# 
#                                         for user in slack_user.get('members', []):
#                                             # slack_name = [channel.get('name').upper() for channel in slack_channels]
#                                             if to_partner.get('display_name','').upper() == user.get('profile',{}).get('real_name','').upper():
#                                                 self.env['mail.channel.partner'].write({
#                                                     'partner_email': user.get('profile',{}).get('email'),
#                                                     'display_name': user.get('profile',{}).get('real_name'),
#                                                     'partner_id': partner_id,
#                                                     'channel_id': to_channel.id,
#                                                     'is_pinned': True,
#                                                 })
#                                                 userChannel = sc.im_open(user=user.get('id'))
# 
#                                                 if userChannel:
#                                                     sc.chat_postMessage(channel=userChannel.get('channel',{}).get('id'), text=body, username=from_partner.name)
#                                                 found = True
#                                                 break
# 
#                                         if not found:
#                                             raise ValueError('user does not found')

#         res_id = super(MailMessage, self).create(values)
#         self.env.cr.commit()
#         return res_id

#         elif values.get('model','') == 'res.partner':
#             if slack:
#                 sc = slack.WebClient(token=token)
#             else:
#                 sc = SlackClient(token)
#             #subject = values.get('subject','') if values.get('subject') else values.get('body')
#             if slack:
#                 slack_channels = sc.channels_list(exclude_archived=1)["channels"] #sc.api_call("channels.list", exclude_archived=1)["channels"]
#             else:
#                 slack_channels = sc.api_call("channels.list", exclude_archived=1)["channels"]
#             
#             to_partner = None
#             from_partner = self.env['res.partner'].search([('id', '=', values.get('res_id'))], limit=1)
# 
#             channel_partner = self.env['mail.channel.partner'].search([('channel_id', '=', values.get('res_id')), ('partner_id', '!=', from_partner.id)])
#             if channel_partner:
#                 to_partner = channel_partner[0].partner_id if channel_partner else channel_partner
#             if slack:
#                 slack_member = sc.users_list(exclude_archived=1)['members'] #sc.api_call("users.list", exclude_archived=1)['members']
#             else:
#                 slack_member = sc.api_call("users.list", exclude_archived=1)['members']
#             if slack_member:
#                 #slack_name = [channel.get('name').upper() for channel in slack_member]
#                 found = False
#                 for slack_mem in slack_member:
#                     # slack_name = [channel.get('name').upper() for channel in slack_channels]
#                     if from_partner.email.upper() == slack_mem.get('profile',{}).get('email').upper():
#                         # for channel in slack_channels:
#                         # if slack_mem['id'] in channel.get('members'):
#                         #from_name = from_partner.name
#                         #from_email = from_partner.email
#                         if slack:
#                             sc.im_open(user=slack_mem.get('id'))
#                         else:
#                             sc.api_call('im.open',user=slack_mem.get('id'))
#                         
#                         if userChannel:
#                             if slack:
#                                 sc.chat_postMessage(channel=userChannel.get('channel',{}).get('id'), text=body, username=self.env.user.name)
#                             else:
#                                 sc.api_call('chat.postMessage',channel=userChannel.get('channel',{}).get('id'), text=body, username=self.env.user.name)
#                         found = True
#                         break
#                 
#                 res_id = super(MailMessage, self).create(values)
#                 self.env.cr.commit()
#                 return res_id
#         else:
#             return super(MailMessage, self).create(values)
