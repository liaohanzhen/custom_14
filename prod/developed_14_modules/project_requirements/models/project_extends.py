from odoo import models,fields,api
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


class ProjectExtends(models.Model):
    _inherit = 'project.project'

    @api.model
    def create(self, vals):
        res = super(ProjectExtends,self).create(vals)
        if res.project_code:
            project_exist = self.search([('project_code','=',res.project_code),('id', '!=', res.id)])
            if not project_exist:
                channel_obj=self.env['mail.channel']
                channel_data={}
                channel_name = "proj-"+res.name.replace(" ",'-')+"-"+res.project_code.replace(" ",'-')
                channel_data.update({'name':channel_name.lower()})
                if self.message_partner_ids:
                    partner_ids=[]
                    for partner_id in res.message_partner_ids:
                        partner_ids.append((0,0,{'partner_id':partner_id.id}))
                    channel_data.update({'channel_last_seen_partner_ids':partner_ids})
                channel_data=channel_obj.create(channel_data)
                if channel_data:
                    mail_invite = self.env['mail.wizard.invite'].with_context({
                                            'default_res_model': 'project.project',
                                            'default_res_id': res.id}).create({'channel_ids': [(4, channel_data.id)],})
                    mail_invite.add_followers()
                        
        return res        
                
    def message_unsubscribe(self, partner_ids=None, channel_ids=None):
        res = super(ProjectExtends, self).message_unsubscribe(partner_ids=partner_ids, channel_ids=channel_ids)                 
        token = self.env.user.company_id.slack_token
        if token:
            if slack:
                sc = slack.WebClient(token=token)
            else:
                sc = SlackClient(token) 
        if partner_ids:
            for record in self:
                if record.message_channel_ids:
                    for channel_id in record.message_channel_ids:
                        channel_obj = self.env['mail.channel'].search([('id','=',channel_id.id),('channel_id','!=',False)])
                        if channel_obj:
                            if slack:
                                slack_channel_info = sc.conversations_members(channel=channel_obj.channel_id)
                            else:
                                slack_channel_info = sc.api_call('conversations.members',channel=channel_obj.channel_id)
                            if slack_channel_info:
                                member_list = slack_channel_info.get('members')
                                for partner in partner_ids:
                                    user_data = self.env['res.users'].search([('partner_id','=',partner)])
                                    if user_data.member_id:
                                        if user_data.member_id in member_list:
                                            for slack_member in member_list:
                                                if user_data.member_id == slack_member:
                                                    params={'channel':channel_obj.channel_id,'user':user_data.member_id}
                                                    if slack:
                                                        slack_member_kick_off = sc.conversations_kick(**params)
                                                    else:
                                                        slack_member_kick_off = sc.api_call('conversations.kick',params)
                                                        
        if channel_ids:
            for record in self:
                for message_channel_id in record.message_channel_ids:
                    message_channel_obj = self.env['mail.channel'].search([('id','=',message_channel_id.id),('channel_id','!=',False)])
                    if message_channel_obj:
                        for channel_id in channel_ids:
                            channel_obj = self.env['mail.channel'].search([('id','=',channel_id),('channel_id','!=',False)])
                            if channel_obj:
                                if slack:
                                    slack_channel_info = sc.conversations_members(channel=message_channel_obj.channel_id)
                                else:
                                    slack_channel_info = sc.api_call('conversations.members',channel=message_channel_obj.channel_id)
                                if slack_channel_info:
                                    member_list =slack_channel_info.get('members')
                                    for partner in channel_obj.channel_last_seen_partner_ids:
                                        user_data = self.env['res.users'].search([('partner_id','=',partner.partner_id.id)])
                                        if user_data.member_id:
                                            if user_data.member_id in member_list:
                                                for slack_member in member_list:
                                                    if user_data.member_id == slack_member:
                                                        params={'channel':message_channel_obj.channel_id,'user':user_data.member_id}
                                                        if slack:
                                                            try: 
                                                                slack_member_kick_off = sc.conversations_kick(**params)
                                                            except Exception as e:
                                                                _logger.exception("OAuth2: %s" % str(e))
                                                        else:
                                                            try:
                                                                slack_member_kick_off = sc.api_call('conversations.kick',params)
                                                            except Exception as e:
                                                                _logger.exception("OAuth2: %s" % str(e))        
                                
     
        return res