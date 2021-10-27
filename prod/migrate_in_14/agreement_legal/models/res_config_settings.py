# Copyright (C) 2018 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_agreement_maintenance = fields.Boolean(
        string="Manage maintenance agreements and contracts."
    )
    module_agreement_mrp = fields.Boolean(
        string="Link your manufacturing orders to an agreement."
    )
    module_agreement_project = fields.Boolean(
        string="Link your projects and tasks to an agreement."
    )
    module_agreement_repair = fields.Boolean(
        string="Link your repair orders to an agreement."
    )
    module_agreement_rma = fields.Boolean(
        string="Link your RMAs to an agreement.")
    module_agreement_sale = fields.Boolean(
        string="Create an agreement when the sale order is confirmed."
    )
    module_agreement_sale_subscription = fields.Boolean(
        string="Link your subscriptions to an agreement."
    )
    module_agreement_stock = fields.Boolean(
        string="Link your pickings to an agreement."
    )
    module_fieldservice_agreement = fields.Boolean(
        string="Link your Field Service orders and equipments to an agreement."
    )
    module_agreement_helpdesk = fields.Boolean(
        string="Link your Helpdesk tickets to an agreement."
    )
    
    @api.model
    def get_values(self):
        ir_config = self.env['ir.config_parameter']
        module_agreement_maintenance = True if ir_config.sudo().get_param('module_agreement_maintenance') == "True" else False
        module_agreement_mrp = True if ir_config.sudo().get_param('module_agreement_mrp') == "True" else False
        module_agreement_project = True if ir_config.sudo().get_param('module_agreement_project') == "True" else False
        module_agreement_repair = True if ir_config.sudo().get_param('module_agreement_repair') == "True" else False
        module_agreement_rma = True if ir_config.sudo().get_param('module_agreement_rma') == "True" else False
        module_agreement_sale = True if ir_config.sudo().get_param('module_agreement_sale') == "True" else False
        module_agreement_sale_subscription = True if ir_config.sudo().get_param('module_agreement_sale_subscription') == "True" else False
        module_agreement_stock = True if ir_config.sudo().get_param('module_agreement_stock') == "True" else False
        module_fieldservice_agreement = True if ir_config.sudo().get_param('module_fieldservice_agreement') == "True" else False
        module_agreement_helpdesk = True if ir_config.sudo().get_param('module_agreement_helpdesk') == "True" else False

        return dict(
            module_agreement_maintenance = module_agreement_maintenance,
            module_agreement_mrp = module_agreement_mrp,
            module_agreement_project = module_agreement_project,
            module_agreement_repair = module_agreement_repair,
            module_agreement_rma = module_agreement_rma,
            module_agreement_sale = module_agreement_sale,
            module_agreement_sale_subscription = module_agreement_sale_subscription,
            module_agreement_stock = module_agreement_stock,
            module_fieldservice_agreement = module_fieldservice_agreement,
            module_agreement_helpdesk = module_agreement_helpdesk
        )

    def set_values(self):
        self.ensure_one()
        ir_config = self.env['ir.config_parameter']
        ir_config.set_param("module_agreement_maintenance", self.module_agreement_maintenance or "False")
        ir_config.set_param("module_agreement_mrp", self.module_agreement_mrp or "False")
        ir_config.set_param("module_agreement_project", self.module_agreement_project or "False")
        ir_config.set_param("module_agreement_repair", self.module_agreement_repair or "False")
        ir_config.set_param("module_agreement_rma", self.module_agreement_rma or "False")
        ir_config.set_param("module_agreement_sale", self.module_agreement_sale or "False")
        ir_config.set_param("module_agreement_sale_subscription", self.module_agreement_sale_subscription or "False")
        ir_config.set_param("module_agreement_stock", self.module_agreement_stock or "False")
        ir_config.set_param("module_fieldservice_agreement", self.module_fieldservice_agreement or "False")
        ir_config.set_param("module_agreement_helpdesk", self.module_agreement_helpdesk or "False")
        return True
