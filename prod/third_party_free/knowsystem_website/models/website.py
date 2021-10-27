#coding: utf-8

import logging

from odoo import _, api, fields, models
from odoo.tools.safe_eval import safe_eval
from odoo.tools.translate import html_translate

_logger = logging.getLogger(__name__)


class website(models.Model):
    """
    Overwrite to keep configuration for particular website
    """
    _inherit = "website"

    @api.model
    def _default_knowsystem_website_portal(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        return safe_eval(ICPSudo.get_param('knowsystem_website_portal', default='False'))

    @api.model
    def _default_knowsystem_website_public(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        return safe_eval(ICPSudo.get_param('knowsystem_website_public', default='False'))

    @api.model
    def _default_knowsystem_portal_print(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        return safe_eval(ICPSudo.get_param('knowsystem_portal_print', default='False'))

    @api.model
    def _default_knowsystem_portal_likes(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        return safe_eval(ICPSudo.get_param('knowsystem_portal_likes', default='False'))

    @api.model
    def _default_knowsystem_portal_social_share(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        return safe_eval(ICPSudo.get_param('knowsystem_portal_social_share', default='False'))

    @api.model
    def _default_knowsystem_portal_tooltip(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        return safe_eval(ICPSudo.get_param('knowsystem_portal_tooltip', default='False'))

    @api.model
    def _default_knowsystem_portal_filters_ids(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        custom_filters = safe_eval(ICPSudo.get_param('knowsystem_portal_filters_ids', default='[]'))
        custom_filters_ids = self.env["ir.filters"].sudo().search([("id", "in", custom_filters)])    
        return custom_filters_ids    

    @api.model
    def _default_knowsystem_custom_search_ids(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        custom_searchs = safe_eval(ICPSudo.get_param('knowsystem_custom_search_ids', default='[]'))
        custom_search_ids = self.env["ir.filters"].sudo().search([("id", "in", custom_searchs)]) 
        return custom_search_ids

    def _inverse_knowsystem_website_portal(self):
        """
        Inverse method for knowsystem_website_portal
        """
        for record in self:
            if not record.knowsystem_website_portal:
                record.knowsystem_website_public = False
                record.knowsystem_portal_print = False
                record.knowsystem_portal_filters_ids = False
                record.knowsystem_custom_search_ids = False
                record.knowsystem_portal_likes = False
                record.knowsystem_portal_social_share = False

    knowsystem_website_portal = fields.Boolean(
        string="Portal KnowSystem",
        default=_default_knowsystem_website_portal,
        inverse=_inverse_knowsystem_website_portal,
    )
    knowsystem_website_public = fields.Boolean(
        string="Public KnowSystem",
        default=_default_knowsystem_website_public,
    )
    knowsystem_portal_print = fields.Boolean(
        string="Print in Portal",
        default=_default_knowsystem_portal_print,
    )
    knowsystem_portal_likes = fields.Boolean(
        string="Portal Likes",
        default=_default_knowsystem_portal_likes,
    )
    knowsystem_portal_social_share = fields.Boolean(
        string="Social Sharing",
        default=_default_knowsystem_portal_social_share,
    )
    knowsystem_portal_tooltip = fields.Boolean(
        string="Sections and Tags Tooltips",
        default=_default_knowsystem_portal_tooltip,
    )
    knowsystem_portal_filters_ids = fields.Many2many(
        "ir.filters",
        "ir_filters_know_website_rel_table",
        "ir_filters_id",
        "res_config_setting_id",
        string="Custom Portal Filters",
        default=_default_knowsystem_portal_filters_ids,
    )
    knowsystem_custom_search_ids = fields.Many2many(
        "knowsystem.custom.search",
        "knowsystem_custom_know_website_rel_table",
        "knowsystem_custom_search_id",
        "res_config_settings_id",
        string="Custom Portal Search",
        default=_default_knowsystem_custom_search_ids,
    )
    left_navigation_hints_header = fields.Char(
        string="Left Navigation Hints Header",
        translate=True,
        default="About KnowSystem",
    )
    left_navigation_hints = fields.Html(
        string="Left Navigation Hints",
        translate=html_translate,
        sanitize_attributes=False,
    )
    center_knowsystem_introduction = fields.Html(
        string="KnowSystem Introduction",
        translate=html_translate,
        sanitize_attributes=False,
    )
    pager_knowsystem = fields.Integer(
        string="Articles Per Page",
        default=10,
    )
    _sql_constraints = [
        ('pager_knowsystem_value_check', 'check (pager_knowsystem>0)', _('Articles number should be positive!')),
    ]

    @api.model
    def create(self, values):
        """
        Overwrite to manage KnowSystem menu
        """
        if values.get("knowsystem_website_public") is not None:
            record._generate_knowsystem_menu(values.get("knowsystem_website_public"), False)            
        return super(website, self).create(values)        

    def write(self, values):
        """
        Re-write to change menus
        """
        if values.get("knowsystem_website_public") is not None:
            for record in self:
                record._generate_knowsystem_menu(
                    values.get("knowsystem_website_public"),
                    record.knowsystem_website_public,
                )
        return super(website, self).write(values)

    def _generate_knowsystem_menu(self, shouldbemenu, previouslyexist):
        """
        The method to add KnowSystem menu or ublink it

        Args:
         * shouldbemenu - bool - whether the menu should present
         * previouslyexist - whether the menu should have already exist (not to recover manually removed menu)
        
        Extra info:
         * Expected singleton
        """
        self.ensure_one()
        exist_ids = self.env["website.menu"].search([
            ("url", "=", "/knowsystem"), 
            ('website_id', 'in', [False, self.id]),
        ])
        if shouldbemenu:
            if not previouslyexist and not exist_ids:
                try:
                    values = {
                        "name": _("KnowSystem"),
                        "url": "/knowsystem",
                        "parent_id": self.menu_id.id,
                        "website_id": self.id,
                        "sequence": 60,
                    }
                    new_menu_id = self.env["website.menu"].create(values)
                except Exception as e:
                    _logger.warning(e)            
        elif exist_ids:
            exist_ids.unlink()
