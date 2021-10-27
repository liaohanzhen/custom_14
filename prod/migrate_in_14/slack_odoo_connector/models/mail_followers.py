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
    _inherit = 'mail.followers'
    
    
    def _get_recipient_data(self, records, message_type, subtype_id, pids=None, cids=None):
        """ Private method allowing to fetch recipients data based on a subtype.
        Purpose of this method is to fetch all data necessary to notify recipients
        in a single query. It fetches data from

         * followers (partners and channels) of records that follow the given
           subtype if records and subtype are set;
         * partners if pids is given;
         * channels if cids is given;

        :param records: fetch data from followers of records that follow subtype_id;
        :param subtype_id: mail.message.subtype to check against followers;
        :param pids: additional set of partner IDs from which to fetch recipient data;
        :param cids: additional set of channel IDs from which to fetch recipient data;

        :return: list of recipient data which is a tuple containing
          partner ID (void if channel ID),
          channel ID (void if partner ID),
          active value (always True for channels),
          share status of partner (void as irrelevant if channel ID),
          notification status of partner or channel (email or inbox),
          user groups of partner (void as irrelevant if channel ID),
        """
        if records and subtype_id:
            query = """
WITH sub_followers AS (
    SELECT fol.id, fol.partner_id, fol.channel_id, subtype.internal
    FROM mail_followers fol
        RIGHT JOIN mail_followers_mail_message_subtype_rel subrel
        ON subrel.mail_followers_id = fol.id
        RIGHT JOIN mail_message_subtype subtype
        ON subtype.id = subrel.mail_message_subtype_id
    WHERE subrel.mail_message_subtype_id = %%s AND fol.res_model = %%s AND fol.res_id IN %%s
)
SELECT partner.id as pid, NULL AS cid,
        partner.active as active, partner.partner_share as pshare, NULL as ctype,
        users.notification_type AS notif, array_agg(groups.id) AS groups
    FROM res_partner partner
    LEFT JOIN res_users users ON users.partner_id = partner.id AND users.active
    LEFT JOIN res_groups_users_rel groups_rel ON groups_rel.uid = users.id
    LEFT JOIN res_groups groups ON groups.id = groups_rel.gid
    WHERE EXISTS (
        SELECT partner_id FROM sub_followers
        WHERE sub_followers.channel_id IS NULL
            AND sub_followers.partner_id = partner.id
            AND (coalesce(sub_followers.internal, false) <> TRUE OR coalesce(partner.partner_share, false) <> TRUE)
    ) %s
    GROUP BY partner.id, users.notification_type
UNION
SELECT NULL AS pid, channel.id AS cid,
        TRUE as active, NULL AS pshare, channel.channel_type AS ctype,
        CASE WHEN channel.email_send = TRUE THEN 'email' ELSE 'inbox' END AS notif, NULL AS groups
    FROM mail_channel channel
    WHERE EXISTS (
        SELECT channel_id FROM sub_followers WHERE partner_id IS NULL AND sub_followers.channel_id = channel.id
    ) %s
""" % ('OR partner.id IN %s' if pids else '', 'OR channel.id IN %s' if cids else '')
            params = [subtype_id, records._name, tuple(records.ids)]
            if pids:
                params.append(tuple(pids))
            if cids:
                params.append(tuple(cids))
            self.env.cr.execute(query, tuple(params))
            res = self.env.cr.fetchall()
        elif pids or cids:
            params, query_pid, query_cid = [], '', ''
            if pids:
                query_pid = """
SELECT partner.id as pid, NULL AS cid,
    partner.active as active, partner.partner_share as pshare, NULL as ctype,
    users.notification_type AS notif, NULL AS groups
FROM res_partner partner
LEFT JOIN res_users users ON users.partner_id = partner.id AND users.active
WHERE partner.id IN %s"""
                params.append(tuple(pids))
            if cids:
                query_cid = """
SELECT NULL AS pid, channel.id AS cid,
    TRUE as active, NULL AS pshare, channel.channel_type AS ctype,
    CASE when channel.email_send = TRUE then 'email' else 'inbox' end AS notif, NULL AS groups
FROM mail_channel channel WHERE channel.id IN %s """
                params.append(tuple(cids))
            query = ' UNION'.join(x for x in [query_pid, query_cid] if x)
            self.env.cr.execute(query, tuple(params))
            res = self.env.cr.fetchall()
#             if pids:
#                 for user in self.env['res.users'].search([('partner_id','in',pids)]):
#                     if user.member_id and user.notification_type=='handle_slack':
#                         pass
        else:
            res = []
        return res
    
    
