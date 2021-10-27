# -*- coding: utf-8 -*-
import pytz
from dateutil import relativedelta
from odoo import fields, models, api


class UpdateRentProductOrder(models.TransientModel):
    _name = 'rent.wizard'

    product_id = fields.Char(strint='product', readonly=True)
    pickup_date = fields.Datetime(string='Date pickup')
    return_date = fields.Datetime(string='Date return')
    duration = fields.Integer(string='Duration', readonly=True)
    duration_unit = fields.Char(readonly=True)
    quantity = fields.Float(string='Quantity')
    unit_price = fields.Float(string='Unit Price')
    unit_price2 = fields.Float()
    pricing_explanation = fields.Html(string='Price Computation', readonly=True)
    temp_sale_order_id = fields.Many2one('sale.order')

    @api.onchange('pickup_date', 'return_date')
    def date_change(self):
        for rec in self:
            if rec.pickup_date and rec.return_date:
                date_1 = rec.pickup_date
                date_2 = rec.return_date
                unit = rec.duration_unit
                difference = relativedelta.relativedelta(date_2, date_1)
                years = difference.years
                months = difference.months
                weeks = difference.weeks
                days = difference.days
                hours = difference.hours
                minutes = difference.minutes

                active_id = rec._context.get('active_ids')
                order = rec.env['sale.order.line'].browse(active_id)
                available_rental_units = []
                available_rental_pricing = []
                for rental_pricing_id in order.product_id.rental_pricing_ids:
                    available_rental_pricing.append({'duration': rental_pricing_id.duration, 'unit': rental_pricing_id.unit, 'price': rental_pricing_id.price})
                    available_rental_units.append(rental_pricing_id.unit)
                if months > 0 and 'month' in available_rental_units:
                    unit = rec.duration_unit = 'month'
                elif weeks > 0 and 'week' in available_rental_units:
                    unit = rec.duration_unit = 'week'
                elif days > 0 and 'day' in available_rental_units:
                    unit = rec.duration_unit = 'day'
                elif hours > 0 and 'hour' in available_rental_units:
                    unit = rec.duration_unit = 'hour'

                for pricing in available_rental_pricing:
                    if pricing['unit'] == unit:
                        unit_price = rec.unit_price2 = rec.unit_price = pricing['price']
                        rec.duration = pricing['duration']

                if unit == 'hour':
                    rec.duration = round((8760 * years) + (730.001 * months) + (24 * days) + hours + (minutes / 60))
                    rec.unit_price = unit_price * rec.duration
                    rec.pricing_explanation = str(rec.duration) + ' * 1 ' + unit + ' (' + str(unit_price) + ')'
                elif unit == 'day':
                    rec.duration = (365 * years) + (30.4167 * months) + days + (hours / 24) + (minutes / 1440)
                    rec.unit_price = unit_price * rec.duration
                    rec.pricing_explanation = str(rec.duration) + ' * 1 ' + unit + ' (' + str(unit_price) + ')'

                elif unit == 'week':
                    rec.duration = (52.143 * years) + (4.345 * months) + (days / 7) + (hours / 168) + (minutes / 10080)
                    rec.unit_price = unit_price * rec.duration
                    rec.pricing_explanation = str(rec.duration) + ' * 1 ' + unit + ' (' + str(unit_price) + ')'

                elif unit == 'month':
                    rec.duration = (12 * years) + months + (days / 30.417) + (hours / 730) + (minutes / 43800)
                    rec.unit_price = unit_price * rec.duration
                    rec.pricing_explanation = str(rec.duration) + ' * 1 ' + unit + ' (' + str(unit_price) + ')'

    def update_order_line(self):
        for rec in self:
            ICPSudo = self.env['ir.config_parameter'].sudo()
            send_mail_qty_reserved = (ICPSudo.get_param('resource_rental_mgt.send_mail_qty_reserved'))
            active_id = rec._context.get('active_ids')
            order = rec.env['sale.order.line'].browse(active_id)
            order.price_unit = rec.unit_price
            order.pickup_date = rec.pickup_date
            order.return_date = rec.return_date
            order.product_uom_qty = order.qty_reserved = order.qty_delivered_left = rec.quantity

            rec.temp_sale_order_id = order.order_id
            user_time_zone = pytz.timezone(self.env.user.partner_id.tz)
            user_time_pickup = pytz.utc.localize(rec.pickup_date, is_dst=False)
            new_pickup_time = user_time_pickup.astimezone(user_time_zone)
            pickup_time = new_pickup_time.strftime('%d %b %Y, %I:%M:%S %p')

            user_time_return = pytz.utc.localize(rec.return_date, is_dst=False)
            new_return_time = user_time_return.astimezone(user_time_zone)
            return_time = new_return_time.strftime('%d %b %Y, %I:%M:%S %p')
            order.name = order.name_tmp + '\n' + str(pickup_time) + ' to ' + str(return_time)
            if send_mail_qty_reserved:
                template_id = self.env.ref('resource_rental_mgt.email_template_sale').id
                template = self.env['mail.template'].browse(template_id)
                template.browse(template_id).send_mail(rec.id, force_send=True)
