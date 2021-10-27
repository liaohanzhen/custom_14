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
    
class SlackCompanyToken(models.Model):
    """
    This Class will store members and channels of slack
    """

    _inherit = 'res.users'

    notification_type = fields.Selection(selection_add=[('handle_slack', 'Handled in Slack')],ondelete={'handle_slack': 'set default'})