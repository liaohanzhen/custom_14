# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models,fields

class project_project(models.Model):
    _inherit = "project.project"
    
    category_id = fields.Many2one("portfolio.category",string="Project Category",required = True)
    proj_desc = fields.Html(string="Description", required=True)
    thumb_img = fields.Binary(string = "Thumbnail", required = True)
    is_publish = fields.Boolean(string="Publish On Website")
    image_lines = fields.One2many("image.gallary","project_id", string = "Slider Details")
    related_projects = fields.Many2many("project.project", 'project_project_relation', 'project_id',
                                        'related_project_id', string="Related Projects")
    
class image_gallary(models.Model):
    _name = "image.gallary"
    
    name = fields.Char(string="Slide Title",required = True)
    slide_desc = fields.Html(string="Slide Description")
    slide_img = fields.Binary(string = "Slide Image")
    project_id = fields.Many2one("project.project", string = "Project")
    