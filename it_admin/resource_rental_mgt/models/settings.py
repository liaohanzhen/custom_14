# -*- coding: utf-8 -*-

from odoo import fields, models, tools, api, _


class RentalSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    send_mail_qty_reserved = fields.Boolean(string='Auto mail send on quantity reserved')
    send_mail_qty_delivered = fields.Boolean(string='Auto mail send on quantity delivered')
    send_mail_qty_returned = fields.Boolean(string='Auto mail send on quantity returned')
    product_id = fields.Many2one('product.product', string='Product')
    extra_hour = fields.Float('Per Hour')
    extra_day = fields.Float('Per Day')
    min_extra_hour = fields.Integer('Apply after')

    def set_values(self):
        res = super(RentalSettings, self).set_values()

        self.env['ir.config_parameter'].set_param('resource_rental_mgt.send_mail_qty_reserved', self.send_mail_qty_reserved)
        self.env['ir.config_parameter'].set_param('resource_rental_mgt.send_mail_qty_delivered', self.send_mail_qty_delivered)
        self.env['ir.config_parameter'].set_param('resource_rental_mgt.send_mail_qty_returned', self.send_mail_qty_returned)
        self.env['ir.config_parameter'].set_param('resource_rental_mgt.product_id', self.product_id.id)
        self.env['ir.config_parameter'].set_param('resource_rental_mgt.extra_hour', self.extra_hour)
        self.env['ir.config_parameter'].set_param('resource_rental_mgt.extra_day', self.extra_day)
        self.env['ir.config_parameter'].set_param('resource_rental_mgt.min_extra_hour', self.min_extra_hour)
        return res

    @api.model
    def get_values(self):
        res = super(RentalSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        send_mail_qty_reserved = ICPSudo.get_param('resource_rental_mgt.send_mail_qty_reserved')
        send_mail_qty_delivered = ICPSudo.get_param('resource_rental_mgt.send_mail_qty_delivered')
        send_mail_qty_returned = ICPSudo.get_param('resource_rental_mgt.send_mail_qty_returned')

        product_id = ICPSudo.get_param('resource_rental_mgt.product_id')
        extra_hour = ICPSudo.get_param('resource_rental_mgt.extra_hour') or 0.0
        extra_day = ICPSudo.get_param('resource_rental_mgt.extra_day') or 0.0
        min_extra_hour = ICPSudo.get_param('resource_rental_mgt.min_extra_hour') or 2
        res.update(
            send_mail_qty_reserved=send_mail_qty_reserved,
            send_mail_qty_delivered=send_mail_qty_delivered,
            send_mail_qty_returned=send_mail_qty_returned,
            product_id=int(product_id),
            extra_hour=float(extra_hour),
            extra_day=float(extra_day),
            min_extra_hour=int(min_extra_hour),
        )
        return res
