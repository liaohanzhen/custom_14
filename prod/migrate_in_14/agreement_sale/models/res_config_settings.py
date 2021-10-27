from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_use_agreement_type = fields.Boolean(
        "Use agreement types", implied_group="agreement.group_use_agreement_type"
    )
    group_use_agreement_template = fields.Boolean(
        "Use agreement template", implied_group="agreement.group_use_agreement_template"
    )

    @api.model
    def get_values(self):
        ir_config = self.env['ir.config_parameter']
        group_use_agreement_type = True if ir_config.sudo().get_param('group_use_agreement_type') == "True" else False
        group_use_agreement_template = True if ir_config.sudo().get_param('group_use_agreement_template') == "True" else False

        return dict(
            group_use_agreement_type = group_use_agreement_type,
            group_use_agreement_template = group_use_agreement_template,
        )

    def set_values(self):
        self.ensure_one()
        ir_config = self.env['ir.config_parameter']
        ir_config.set_param("group_use_agreement_type", self.group_use_agreement_type or "False")
        ir_config.set_param("group_use_agreement_template", self.group_use_agreement_template or "False")
        return True