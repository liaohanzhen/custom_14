from odoo import api, fields, models


class HospitalSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    name = fields.Char(string='Note')
    product_id = fields.Many2many('product.product', string='Medicine')

    def set_values(self):
        res = super().set_values()
        self.env['ir.config_parameter'].set_param('hospital.name', self.name)
        # self.env['ir.config_parameter'].set_param('hospital.product_id', self.product_id.ids)
        return res

    @api.model
    def get_values(self):
        res = super().get_values()
        IrDefault = self.env['ir.config_parameter'].sudo()
        res.update(name=IrDefault.get_param('hospital.name'))
        # res.update(product_id=literal_eval(IrDefault.get_param('hospital.product_id')))
        return res
