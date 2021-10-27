# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
import base64
import logging
from datetime import datetime, timedelta
from werkzeug import urls, utils
_logger = logging.getLogger(__name__)

class LinkTrackerExtendWebsite(models.Model):
    _inherit = ['link.tracker']
    short_url = fields.Char(string='Tracked URL', compute='_compute_short_url2')
    short_url_host = fields.Char(string='Host of the short URL', compute='_compute_short_url_host2')
            
    @api.depends('code')
    def _compute_short_url2(self):
        for tracker in self:
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.5b.website.url')
            tracker.short_url = urls.url_join(base_url, '/r/%(code)s' % {'code': tracker.code})

    def _compute_short_url_host2(self):
        for tracker in self:
            tracker.short_url_host = self.env['ir.config_parameter'].sudo().get_param('web.5b.website.url') + '/r/'