
from odoo import models, api, tools
try:
    import slack
except ImportError:
    slack=None
    
try:
    from slackclient import SlackClient
except ImportError:
    SlackClient=None
import random
import string
from werkzeug.urls import url_encode
import logging
_logger = logging.getLogger(__name__)
    
class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'
    
    def _get_uniq_string(self):
        size = 15
        chars = string.ascii_uppercase
        return ''.join(random.choice(chars) for _ in range(size))
    
    def get_base_url_slack(self):
        """Get the base URL for the current model.

        Defined here to be overriden by website specific models.
        The method has to be public because it is called from mail templates.
        """
        return self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    
    def _get_share_url_slack(self, record, redirect=True, signup_partner=False, pid=None):
        """
        Build the url of the record  that will be sent by mail and adds additional parameters such as
        access_token to bypass the recipient's rights,
        signup_partner to allows the user to create easily an account,
        hash token to allow the user to be authenticated in the chatter of the record portal view, if applicable
        :param redirect : Send the redirect url instead of the direct portal share url
        :param signup_partner: allows the user to create an account with pre-filled fields.
        :param pid: = partner_id - when given, a hash is generated to allow the user to be authenticated
            in the portal chatter, if any in the target page,
            if the user is redirected to the portal instead of the backend.
        :return: the url of the record with access parameters, if any.
        """
        
        params = {
            'model': record._name,
            'res_id': record.id,
        }
        if hasattr(record, 'access_token'):
            params['access_token'] = record._portal_ensure_token()
        if pid:
            params['pid'] = pid
            params['hash'] = record._sign_token(pid)
        if signup_partner and hasattr(record, 'partner_id') and record.partner_id:
            params.update(record.partner_id.signup_get_auth_param()[record.partner_id.id])

        return '/mail/view?%s' % (url_encode(params))
    
#     @api.multi
    @api.returns('mail.message', lambda value: value.id)
#     def message_post(self, body='', subject=None,
#                      message_type='notification', subtype=None,
#                      parent_id=False, attachments=None,
#                      notif_layout=False, add_sign=True, model_description=False,
#                      mail_auto_delete=True, **kwargs):
    
    def message_post(self, *,
                     body='', subject=None, message_type='notification',
                     email_from=None, author_id=None, parent_id=False,
                     subtype_xmlid=None, subtype_id=False, partner_ids=None, channel_ids=None,
                     attachments=None, attachment_ids=None,
                     add_sign=True, record_name=False,
                     **kwargs):
        
#         new_message = super(MailThread, self).message_post(body=body, subject=subject,
#                                                            message_type=message_type, subtype=subtype,
#                                                            parent_id=parent_id, attachments=attachments,
#                                                            notif_layout=notif_layout, add_sign=add_sign, model_description=model_description,
#                                                            mail_auto_delete=mail_auto_delete, **kwargs)
        new_message = super(MailThread, self).message_post(body=body, subject=subject,
                                                           message_type=message_type, 
                                                           email_from=email_from, author_id=author_id, 
                                                           parent_id=parent_id, subtype_xmlid=subtype_xmlid, 
                                                           subtype_id=subtype_id, partner_ids=partner_ids, 
                                                           channel_ids=channel_ids, attachments=attachments, 
                                                           attachment_ids=attachment_ids, add_sign=add_sign, record_name=record_name, **kwargs)
        
        if self._context.get('is_message_from_js') and self.message_channel_ids:
            slack_channels = self.message_channel_ids.filtered(lambda x:x.channel_id)
            token = self.env.user.company_id.slack_token
            if not token or not slack_channels:
                return new_message
            
            body = new_message.body
            #body = body.strip('<>/p')
            body = tools.html2plaintext(body).strip()
            attachments = []
            if hasattr(self, '_get_share_url') and hasattr(self, 'get_base_url'):
                url = self.get_base_url() + self._get_share_url(redirect=True)
                
            else:
                url = self.get_base_url_slack() + self._get_share_url_slack(self, redirect=True)
            
            attachments = [
                           {
                            "fallback": "View %s %s %s"%(self._description, self.display_name, url),
                            "actions": [
                                    {
                                        "type": "button",
                                        "name": "file_request_"+self._get_uniq_string(),
                                        "text": "View %s %s"%(self._description, self.display_name),
                                        "url": url,
                                        "style": "primary"
                                    }
                                ]
                            }
                        ]    
            if slack:
                sc = slack.WebClient(token=token)
            else:
                sc = SlackClient(token)
            for odoo_channel in slack_channels: 
                try:
                    user = self.env.user
                    slack_member = user.company_id.all_users_ids.filtered(lambda x:x.user_id==user.member_id)
                    if slack_member:
                        username = slack_member[0].name
                        if slack:
                            sc.chat_postMessage(channel=odoo_channel.channel_id, text=body,username=username,attachments=attachments, icon_emoji='true')
                        else:
                            sc.api_call('chat.postMessage',channel=odoo_channel.channel_id, text=body,attachments=attachments,username=username, icon_emoji='true')
                    else:
                        if slack:
                            sc.chat_postMessage(channel=odoo_channel.channel_id, text=body,attachments=attachments, icon_emoji='true')
                        else:
                            sc.api_call('chat.postMessage',channel=odoo_channel.channel_id, text=body,attachments=attachments, icon_emoji='true')
                except Exception as e:
                    _logger.info(str(e))
                
            
        return new_message
        