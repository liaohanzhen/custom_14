# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
import base64
import logging
from datetime import datetime, timedelta
_logger = logging.getLogger(__name__)

class mvp_pylon_projects_5b(models.Model):
    _name = 'mvp.pylon.projects.5b'
    _description='MVP Pylon Projects'
    
    publish_date = fields.Datetime('Publish Date')
    active = fields.Boolean(string='Active', default=True)
    is_publish = fields.Boolean(string='Is Published')
    project_id = fields.Char(string='Project ID')
    name = fields.Char(string='Project Name')
    project_data = fields.Char(string='Project Data')
    design_data = fields.Char(string='Design Data')