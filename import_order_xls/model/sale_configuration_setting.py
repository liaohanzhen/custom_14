from odoo import fields, models, api


class sale_config_settings(models.TransientModel):
    _inherit = 'res.config.settings'

    @api.model
    def self_default_qty_defaults(self):
        default_qty = 1
        try:
            key_id = self.env.ref('import_order_xls.default_qty_confi_parameter')
            default_qty = key_id and key_id.value or 1
        except:
            pass
        return default_qty

    group_visible_import_order = fields.Boolean('Import sale order line from excel file ?',
                                                implied_group='import_order_xls.group_sale_order_line_import',
                                                help='You can allow user to import sale order line from excel file.')
    default_product_uom_qty = fields.Integer("Set Default Quantity",
                                             help="This quantity will be taken when excel file has no value for quantity in line.",
                                             default=self_default_qty_defaults, default_model='sale.order.line')

    def set_all_companydefaults(self):
        self.company_id.write({'group_visible_import_order': self.group_visible_import_order})

    def execute(self):
        res = super(sale_config_settings, self).execute()
        if self.default_product_uom_qty:
            try:
                key_id = self.env.ref('import_order_xls.default_qty_confi_parameter')
            except:
                self.env['ir.config_parameter'].create(
                    {'key': 'import_order_xls.default_qty_confi_parameter', 'value': self.default_product_uom_qty})
            if key_id:
                value = self.env['ir.config_parameter'].search([('id', '=', key_id.id)])
                value and value.write({'value': self.default_product_uom_qty})
        return res
