# -*- coding: utf-8 -*-

from odoo import models, api, fields, tools
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
    _inherit = 'mail.message'
    
#     @api.multi
    def _notify_compute_recipients(self, record, msg_vals):
        """ Compute recipients to notify based on subtype and followers. This
        method returns data structured as expected for ``_notify_recipients``. """
        msg_sudo = self.sudo()

        pids = [x[1] for x in msg_vals.get('partner_ids')] if 'partner_ids' in msg_vals else msg_sudo.partner_ids.ids
        cids = [x[1] for x in msg_vals.get('channel_ids')] if 'channel_ids' in msg_vals else msg_sudo.channel_ids.ids
        subtype_id = msg_vals.get('subtype_id') if 'subtype_id' in msg_vals else msg_sudo.subtype_id.id

        recipient_data = {
            'partners': [],
            'channels': [],
        }
        res = self.env['mail.followers']._get_recipient_data(record, subtype_id, pids, cids)
        author_id = msg_vals.get('author_id') or self.author_id.id if res else False
        for pid, cid, active, pshare, ctype, notif, groups in res:
            if pid and pid == author_id and not self.env.context.get('mail_notify_author'):  # do not notify the author of its own messages
                continue
            if pid:
                if active is False:
                    # avoid to notify inactive partner by email (odoobot)
                    continue
                pdata = {'id': pid, 'active': active, 'share': pshare, 'groups': groups}
                if notif == 'inbox':
                    recipient_data['partners'].append(dict(pdata, notif=notif, type='user'))
                elif notif == 'handle_slack':  
                    for user in self.env['res.users'].search([('partner_id','in',pid)]):
                        if user.member_id and user.notification_type=='handle_slack':
                            pass
                else:
                    if not pshare and notif:  # has an user and is not shared, is therefore user
                        recipient_data['partners'].append(dict(pdata, notif='email', type='user'))
                    elif pshare and notif:  # has an user but is shared, is therefore portal
                        recipient_data['partners'].append(dict(pdata, notif='email', type='portal'))
                    else:  # has no user, is therefore customer
                        recipient_data['partners'].append(dict(pdata, notif='email', type='customer'))
                
                                 
            elif cid:
                recipient_data['channels'].append({'id': cid, 'notif': notif, 'type': ctype})
        return recipient_data