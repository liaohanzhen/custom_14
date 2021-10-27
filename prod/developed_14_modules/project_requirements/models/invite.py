# -*- coding: utf-8 -*-

from odoo import _, api, models
import logging
_logger = logging.getLogger(__name__)
try:
    import slack
except ImportError:
    slack=None
    
try:
    from slackclient import SlackClient
except ImportError:
    SlackClient=None    

class Invite(models.TransientModel):
    _inherit = 'mail.wizard.invite'
   
   
    def add_followers(self):
        new_partners_dict = {}
        new_channels_dict = {}
        document_dict = {}
        for wizard in self:
            if wizard.res_model=='project.project':
                Model = self.env[wizard.res_model]
                document = Model.browse(wizard.res_id)
                document_dict.update({wizard.id : document})
                
                new_partners = wizard.partner_ids - document.message_partner_ids
                new_partners_dict.update({wizard.id : new_partners})
                
                new_channels = wizard.channel_ids - document.message_channel_ids
                new_channels_dict.update({wizard.id : new_channels})
                
        res = super(Invite, self).add_followers()
        if new_partners_dict or new_channels_dict:
            for wizard in self:
                if wizard.res_model=='project.project':
                    wizard.add_member_in_slack(new_partners_dict.get(wizard.id),document_dict.get(wizard.id),new_channels_dict.get(wizard.id))
                
        return res
        
    def add_member_in_slack(self,new_partner_ids,document,new_channels):
        token = self.env.user.company_id.slack_token
        if not token:
            return
        if new_partner_ids:
            new_partner_id_list=[]
            for partner in new_partner_ids:
                new_partner_id_list.append(partner.id)
            if slack:
                sc = slack.WebClient(token=token)
            else:
                sc = SlackClient(token)     
            for channel in document.message_channel_ids:
                if not channel.channel_id:
                    continue
                
                for user in self.env['res.users'].search([('partner_id','in',new_partner_id_list)]):
                    if user.member_id:
                        member_id = user.member_id
                    else:
                        user_email = user.email or user.login
                        if user_email:
                            continue
                        if slack:
                            try:
                                slack_member = sc.users_lookupByEmail(email=user_email)
                                slack_member = slack_member.data
                            except Exception as e:
                                _logger.exception("OAuth2: %s" % str(e))
                                continue
                        else:
                            slack_member = sc.api_call('users.lookupByEmail',email=user_email)
                        user_data_slack = slack_member.get('user')
                        member_id = user_data_slack and user_data_slack.get('id')
                        if not member_id:
                            continue
                        
                        user.write({'member_id':member_id})
                                    
                    params = {'channel':channel.channel_id,
                              'users':member_id}
                    if slack:
                        try:
                            slack_member = sc.conversations_invite(**params)
                            slack_member = slack_member.data
                        except Exception as e:
                            _logger.exception("OAuth2: %s" % str(e))
                    else:
                        slack_member = sc.api_call('conversations.invite',**params)
        else:
            if slack:
                sc = slack.WebClient(token=token)
            else:
                sc = SlackClient(token)     
            
            for channel in new_channels:
                if not channel.channel_id:
                    continue
                partner_list=[]
                for partner in channel.channel_last_seen_partner_ids:
                    partner_list.append(partner.partner_id.id)
                for user in self.env['res.users'].search([('partner_id','in',partner_list)]):
                    if user.member_id:
                        member_id = user.member_id
                    else:
                        user_email = user.email or user.login
                        if not user_email:
                            continue
                        if slack:
                            try:
                                slack_member = sc.users_lookupByEmail(email=user_email)
                                slack_member = slack_member.data
                            except Exception as e:
                                _logger.exception("OAuth2: %s" % str(e))
                        else:
                            slack_member = sc.api_call('users.lookupByEmail',email=user_email)
                        user_data_slack = slack_member.get('user')
                        member_id = user_data_slack and user_data_slack.get('id')
                        if not member_id:
                            continue
                        user.write({'member_id':member_id})
                    
                    params = {'channel':channel.channel_id,
                              'users':member_id}
                    if slack:
                        try:
                            slack_member = sc.conversations_invite(**params)
                            slack_member = slack_member.data
                        except Exception as e:
                            _logger.exception("OAuth2: %s" % str(e))
                    else:
                        slack_member = sc.api_call('conversations.invite',params)
