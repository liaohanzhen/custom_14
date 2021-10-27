# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
import base64
import logging
from datetime import datetime, timedelta
_logger = logging.getLogger(__name__)
    
class Employee(models.Model):
    _inherit = "hr.employee"
    x_show_in_website = fields.Boolean(string='Show in website?')
    x_department_name = fields.Char(related='department_id.name', string='Department Name')
    x_display_order = fields.Integer(string='Website Order', help='Website display order e.g. 1=> Chris, 2=>Eden')

class website_content_5b(models.Model):
    _name = 'website.content.5b'
    _description='5B Website Contents'

    link_url = fields.Char(string='URL', help='End part of the url, title-of-the-page')
    publish_date = fields.Datetime('Publish Date')
    active = fields.Boolean(string='Active', default=True)
    is_publish = fields.Boolean(string='Is Published')
    name = fields.Char(string='Page Name', help='About 5B, Solutions etc')
    seo_tags = fields.Char(string='SEO Keywords', help='About 5B, Solutions etc.')
    seo_desc = fields.Char(string='SEO Desc.', help='Page description about 60 characters')
    title = fields.Char(string='Title', help='Title of page display in breadcumb')
    short_intro = fields.Html('Short Intro', help='Around 100 characters')
    description = fields.Html('Details')
    video_url = fields.Char(string='Video URL')
    video_caption = fields.Char(string='Video Caption')
    document_url = fields.Char(string='Document URL')
    banner_image = fields.Many2one('ir.attachment',  string='Banner Image', help='1968 x 800px')
    caption_image = fields.Many2one('ir.attachment',  string='Caption Image', help='800 x 600px')
    caption_title = fields.Char(string='Caption title')

class website_faqs_5b(models.Model):
    _name = 'website.faqs.5b'
    _description='5B Website FAQs'

    publish_date = fields.Datetime('Publish Date')
    active = fields.Boolean(string='Active', default=True)
    is_publish = fields.Boolean(string='Is Published')
    name = fields.Char(string='FAQ', help='FAQs', default="FAQs")
    question = fields.Char(string='Question', help='Question')
    answer = fields.Html('Answer', help='Short and brief answer')
    display_order = fields.Integer(string='Display order', default=1)
    
class website_project_5b(models.Model):
    _name = 'website.project.5b'
    _description='5B Website Projects'

    publish_date = fields.Datetime('Publish Date')
    active = fields.Boolean(string='Active', default=True)
    is_publish = fields.Boolean(string='Is Published')
    name = fields.Char(string='Project Name')
    project_capacity = fields.Char(string='Capacity(kWp)')
    project_panel = fields.Char(string='No. of MAVs')
    short_intro = fields.Html('Project Intro', help='Project Intro')
    description = fields.Html('Details')
    document_url = fields.Char(string='Document URL')
    display_order = fields.Integer(string='Display order', default=1)
    project_portfolio = fields.Many2one('ir.attachment',  string='Project Portfolio')
    banner_image = fields.Many2one('ir.attachment',  string='Banner Image', help='1968 x 800px')
    caption_image = fields.Many2one('ir.attachment',  string='Project Image', help='800 x 600px')
    caption_image_thumb = fields.Binary(string='Caption Thumb', compute='_compute_images')
    
    project_address = fields.Char(string='Project Address', help='Complete project address (incl. Country)')
    p_lat = fields.Char(string='Geo Lat.', help='Lattitude of the project locaiton')
    p_lon = fields.Char(string='Geo Lon.', help='Longitude of the project locaiton')
    project_crm_id = fields.Many2one('crm.lead', string='Linked CRM project', help='Completed project in CRM project')
    
    @api.depends('caption_image.datas')
    def _compute_images(self):
        _thumb = None
        _rec_update = {}
        for rec in self:
            if rec.caption_image:
                base64_source = rec.caption_image.datas
                missing_padding = len(base64_source) % 4
                if missing_padding:
                    base64_source += '='* (4 - missing_padding)
                _base64_source = bytes(base64_source)
                _thumb = tools.image_process(_base64_source, size=(800, 450))
                _rec_update['caption_image_thumb'] = _thumb
            else:
                _rec_update['caption_image_thumb'] = None
            rec.update(_rec_update)

class website_media_5b(models.Model):
    _name = 'website.media.5b'
    _description='5B Website Media'
    
    publish_date = fields.Datetime('Publish Date')
    active = fields.Boolean(string='Active', default=True)
    is_publish = fields.Boolean(string='Is Published')
    name = fields.Char(string='Media Name')
    
    media_image = fields.Many2one('ir.attachment',  string='Media Image', help='Size anything above 800 x 450px aspect ratio')
    media_image_thumb = fields.Binary(string='Media Thumb', compute='_compute_images')
    
    video_source = fields.Selection([('youtube', 'YouTube'), ('vimeo', 'Vimeo')], 'Video source')
    video_link = fields.Char(string='Video Link')
    
    media_caption = fields.Char(string='Media caption')
    display_order = fields.Integer(string='Display order', default=1)
    short_intro = fields.Html('Short desc', help='Description about media')
    document_url = fields.Char(string='Document URL (if any)')
    
    @api.depends('media_image.datas')
    def _compute_images(self):
        _thumb = None
        _rec_update = {}
        for rec in self:
            if rec.media_image:
                base64_source = rec.media_image.datas
                missing_padding = len(base64_source) % 4
                if missing_padding:
                    base64_source += '='* (4 - missing_padding)
                _base64_source = bytes(base64_source)
                _thumb = tools.image_process(_base64_source, size=(800, 450))
                _rec_update['media_image_thumb'] = _thumb
            else:
                _rec_update['media_image_thumb'] = None
            rec.update(_rec_update)

class website_resources_5b(models.Model):
    _name = 'website.resources.5b'
    _description='5B Website Resources'
    
    publish_date = fields.Datetime('Publish Date')
    active = fields.Boolean(string='Active', default=True)
    is_publish = fields.Boolean(string='Is Published')
    
    name = fields.Char(string='Document Name')
    document_src = fields.Many2one('ir.attachment',  string='Resource Doc.', help='Upload resource docs')
    document_link = fields.Char(string='Document Link', help='Resource doc link if any')
    document_caption = fields.Char(string='Document caption')
    display_order = fields.Integer(string='Display order', default=1)
   
class website_news_5b(models.Model):
    _name = 'website.news.5b'
    _description='5B Website News'

    link_url = fields.Char(string='URL', help='End part of the url, title-of-the-page')
    publish_date = fields.Datetime('Publish Date')
    active = fields.Boolean(string='Active', default=True)
    is_publish = fields.Boolean(string='Is Published')
    name = fields.Char(string='Name', help='News', default="News")
    title = fields.Char(string='Title', help='News title')
    
    seo_tags = fields.Char(string='SEO Keywords', help='News tags')
    seo_desc = fields.Char(string='SEO Desc.', help='News description about 60 characters')
    external_source = fields.Char(string='Source', help='Short name of source of news e.g. Yahoo Finance, Renew Economy etc.')
    external_source_logo = fields.Many2one('ir.attachment',  string='Source Logo', help='Height of 20px')
    external_source_url = fields.Char(string='Source URL', help='Full URL of news')
    
    display_order = fields.Integer(string='Display order', default=1)
    
    short_intro = fields.Html('Short Intro', help='Around 100 characters')
    description = fields.Html('Details')
    video_url = fields.Char(string='Video URL')
    video_caption = fields.Char(string='Video Caption')
    document_url = fields.Char(string='Document URL')
    banner_image = fields.Many2one('ir.attachment',  string='Banner Image', help='1968 x 800px')
    caption_image = fields.Many2one('ir.attachment',  string='Caption Image', help='800 x 600px')
    caption_title = fields.Char(string='Caption title')
    
    @api.onchange('title')
    def onchange_title(self):
        if not self.title:
            return
        _link_url = self.title.replace(" ","-").lower()
        self.link_url = _link_url