#coding: utf-8

import logging

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class smart_warning(models.Model):
    """
    The model to keep alerts data
    """
    _name = "smart.warning"
    _description = "Smart Warning"

    @api.model
    def _return_model(self):
        """
        The method to return available models available for this user
        """
        model_ids =  self.env['ir.model'].sudo().search([
            ('access_ids.group_id.users', '=', self.env.uid),
            ('transient', '=', False),
        ], order="name")
        return model_ids.mapped(lambda rec: (rec.model, rec.name))

#     @api.multi
    @api.depends("user_group_ids", "user_group_ids.users")
    def _compute_access_user_ids(self):
        """
        Compute method for access_user_ids
        """
        for warn in self:
            users = warn.user_group_ids.mapped("users")
            warn.access_user_ids = [(6, 0, users.ids)]

#     @api.multi
    @api.onchange("model")
    def _onchange_model(self):
        """
        Onchange method for model to clean domain
        """
        for warning in self:
            warning.domain = "[]"

    name = fields.Char(
        "Alert Title",
        required=True,
        translate=True,
    )
    description = fields.Char(
        "Alert Text",
        required=True,
        translate=True,
    )
    css_class = fields.Selection(
        [
            ("danger", "Danger"),
            ("warning", "Warning"),
            ("info", "Info"),
            ("success", "Success"),
        ],
        string="Type",
        required=True,
        default="danger",
    )
    model = fields.Selection(
        _return_model,
        string='Document Type',
        required=True,
    )
    domain = fields.Text(
        string="Filters",
        default="[]",
        help="""
            Warning would be shown only in case a record satisfies those filters.
            Leave it empty to show this alert for all records of this document type.
        """,
    )
    user_group_ids = fields.Many2many(
        "res.groups",
        "res_groups_smart_warning_rel_table",
        "res_groups_id",
        "smart_warning_id",
        string="Show only for user groups",
        help="""
            If selected, this alert would be shown only for users which belong to those groups.
            If empty, it would be shown for everyone
        """,
    )
    access_user_ids = fields.Many2many(
        "res.users",
        "res_users_smart_warning_rel_table",
        "res_users_id",
        "smart_warning_id",
        string="Access Users",
        compute=_compute_access_user_ids,
        compute_sudo=True,
        store=True,
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    sequence = fields.Integer(
        string="Sequence",
        help="The lesser the closer to the top it is shown",
        default=0,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.user.company_id.id,
    )

    _order = "sequence, id"

    @api.model
    def return_warnings(self, res_model, res_id):
        """
        The method to find all warning related to this record and prepare them in js formats

        Args:
         * res_model - char - model name
         * res_id - int - id of a document

        Returns:
         * list of warning dicts:
          ** name
          ** description
          ** css_class
        """
        self = self.with_context(lang=self.env.user.lang)

        def prepare_js_dict(warn):
            return {
                "name": warn.name,
                "description": warn.description,
                "css_class": warn.css_class,
            }

        warnings = self.search([
            ("model", "=", res_model),
            "|",
                ("access_user_ids", "in", self.env.uid),
                ("access_user_ids", "=", False),
        ])
        res = []
        for warn in warnings:
            if warn.domain and warn.domain != "[]":
                try:
                    domain = [("id", "=", res_id)] + safe_eval(warn.domain)
                    model_cl = self.env[res_model]
                    if hasattr(model_cl, "active"):
                        domain += ["|", ("active", "=", True), ("active", "=", False)]
                    if self.env[res_model].search_count(domain):
                        res.append(prepare_js_dict(warn))
                except Exception as er:
                    _logger.warning("Domain {} for alert {} is not correctly set: {}".format(warn.domain, warn.id, er))
            else:
                res.append(prepare_js_dict(warn))
        return res
