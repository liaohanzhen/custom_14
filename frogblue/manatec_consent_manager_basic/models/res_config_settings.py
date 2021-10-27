# -*- coding: utf-8 -*-
"""
    Author: Konrad Sawade (konrad.sawade@manatec.de)
    Copyright: 2020, manaTec GmbH
    Date created: 21.08.2020
"""
import logging

from odoo import fields, models

logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    privacy_policy_url = fields.Char('URL', related='website_id.privacy_policy_url', required=True, readonly=False)
    cookie_domain = fields.Char('Cookie Domain', related='website_id.cookie_domain', required=True, readonly=False)
