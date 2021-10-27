# Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class KnowledgeConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    module_attachment_indexation = fields.Boolean(
        "Attachments List and Document Indexation",
        help="Document indexation, full text search of attachements.\n"
        "- This installs the module attachment_indexation.",
    )

    group_ir_attachment_user = fields.Boolean(
        string="Central access to Documents",
        help="When you set this field all users will be able to manage "
        "attachments centrally, from the Knowledge/Documents menu.",
        implied_group="knowledge.group_ir_attachment_user",
    )

    module_document_page = fields.Boolean(
        "Manage document pages (Wiki)",
        help="Provide document page and category as a wiki.\n"
        "- This installs the module document_page.",
    )

    module_document_page_approval = fields.Boolean(
        "Manage documents approval",
        help="Add workflow on documents per category.\n"
        "- This installs the module document_page_approval.",
    )

    module_cmis_read = fields.Boolean(
        "Attach files from an external DMS into Odoo",
        help="Connect Odoo with a CMIS compatible server to attach files\n"
        "to an Odoo record.\n"
        "- This installs the module cmis_read.",
    )

    module_cmis_write = fields.Boolean(
        "Store attachments in an external DMS instead of the Odoo Filestore",
        help="Connect Odoo with a CMIS compatible server to store files.\n"
        "- This installs the module cmis_write.",
    )

    @api.model
    def get_values(self):
        ir_config = self.env['ir.config_parameter']
        module_attachment_indexation = True if ir_config.sudo().get_param('module_attachment_indexation') == "True" else False
        group_ir_attachment_user = True if ir_config.sudo().get_param('group_ir_attachment_user') == "True" else False
        module_document_page = True if ir_config.sudo().get_param('module_document_page') == "True" else False
        module_document_page_approval = True if ir_config.sudo().get_param('module_document_page_approval') == "True" else False
        module_cmis_read = True if ir_config.sudo().get_param('module_cmis_read') == "True" else False
        module_cmis_write = True if ir_config.sudo().get_param('module_cmis_write') == "True" else False

        return dict(
            module_attachment_indexation = module_attachment_indexation,
            group_ir_attachment_user = group_ir_attachment_user,
            module_document_page = module_document_page,
            module_document_page_approval = module_document_page_approval,
            module_cmis_read = module_cmis_read,
            module_cmis_write = module_cmis_write,
        )

    def set_values(self):
        self.ensure_one()
        ir_config = self.env['ir.config_parameter']
        ir_config.set_param("module_attachment_indexation", self.module_attachment_indexation or "False")
        ir_config.set_param("group_ir_attachment_user", self.group_ir_attachment_user or "False")
        ir_config.set_param("module_document_page", self.module_document_page or "False")
        ir_config.set_param("module_document_page_approval", self.module_document_page_approval or "False")
        ir_config.set_param("module_cmis_read", self.module_cmis_read or "False")
        ir_config.set_param("module_cmis_write", self.module_cmis_write or "False")
        return True
