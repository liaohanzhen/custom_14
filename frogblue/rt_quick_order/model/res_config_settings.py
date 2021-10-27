from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    attribute_ids = fields.Many2one('product.attribute', string='Attributes')

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('rt_quick_order.attribute_ids', self.attribute_ids)
        super(ResConfigSettings, self).set_values()

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        attribute_str = self.env['ir.config_parameter'].sudo().get_param('rt_quick_order.attribute_ids')
        if attribute_str:
            res['attribute_ids'] = int(''.join(filter(lambda i: i.isdigit(), attribute_str)))
        else:
            res['attribute_ids'] = 1
        return res
