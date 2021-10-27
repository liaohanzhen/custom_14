# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    product_tmp_id = fields.Many2one('product.template',string="Producto flete e instalacion")
    product_tmp_id2 = fields.Many2one('product.template',string="Producto plan de proteccion")
    product_tmp_id3 = fields.Many2one('product.template',string="Producto depósito en garantía")
    descuento_maximo = fields.Float(string='Descuento Maximo')

    #New field dias de gracia
    dias_gracia = fields.Integer(string="Días de gracia", store=True)
    
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(product_tmp_id=int(params.get_param("structurall_module.product_tmp_id", default=False)) or False,
                   product_tmp_id2=int(params.get_param("structurall_module.product_tmp_id2", default=False)) or False,
                   product_tmp_id3=int(params.get_param("structurall_module.product_tmp_id3", default=False)) or False,
                   descuento_maximo=float(params.get_param('structurall_module.descuento_maximo', 0.0)),
                   dias_gracia=float(params.get_param('structurall_module.dias_gracia', 0.0)),
                   )
        return res

    
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ir_param = self.env['ir.config_parameter']
        ir_param.sudo().set_param("structurall_module.product_tmp_id", self.product_tmp_id.id)
        ir_param.sudo().set_param("structurall_module.product_tmp_id2", self.product_tmp_id2.id)
        ir_param.sudo().set_param("structurall_module.product_tmp_id3", self.product_tmp_id3.id)
        ir_param.sudo().set_param('structurall_module.descuento_maximo', self.descuento_maximo)
        ir_param.sudo().set_param('structurall_module.dias_gracia', self.dias_gracia)
        
    