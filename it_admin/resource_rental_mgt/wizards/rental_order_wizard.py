# -*- coding: utf-8 -*-
import datetime

import pytz
from dateutil import relativedelta

from odoo import fields, models, api
from odoo.exceptions import ValidationError


class ValidateRentalOrder(models.TransientModel):
    _name = 'rental.order.wizard'

    status = fields.Selection(
        [('draft', 'Quotation'), ('sent', 'Quotation Sent'), ('pickup', 'Reserved'), ('return', 'Picked-up'),
         ('returned', 'Returned'), ('cancel', 'Cancelled')])
    rental_wizard_line_ids = fields.One2many('rental.order.wizard.line', 'rental_order_wizard_id')
    temp_sale_order_id = fields.Many2one('sale.order')
    reserved = fields.Float()
    picked = fields.Float()
    returned = fields.Float()
    has_late_lines = fields.Boolean()

    def apply(self):
        for rec in self:
            ICPSudo = self.env['ir.config_parameter'].sudo()
            send_mail_qty_delivered = (ICPSudo.get_param('resource_rental_mgt.send_mail_qty_delivered'))
            send_mail_qty_returned = (ICPSudo.get_param('resource_rental_mgt.send_mail_qty_returned'))
            active_id = rec._context.get('active_ids')
            order = rec.env['sale.order'].browse(active_id)
            rec.temp_sale_order_id = order
            ls = order.order_line.ids
            order_line_count_all = len(ls)

            for rental_wizard_line_id in rec.rental_wizard_line_ids:
                if rec.status == 'pickup':
                    picked = float(rental_wizard_line_id.qty_delivered)
                    rec.reserved = float(rental_wizard_line_id.order_item_id.qty_reserved)
                    picked_left = float(rental_wizard_line_id.order_item_id.qty_delivered_left)
                    if picked_left - picked < 0:
                        raise ValidationError('Can not pick more than reserved!')
                    elif picked < picked_left:
                        rental_wizard_line_id.order_item_id.qty_delivered_left = picked_left - picked
                        order.has_late_lines = True
                        order.has_pickable_lines = True
                        rec.picked = rental_wizard_line_id.order_item_id.qty_delivered = rental_wizard_line_id.order_item_id.qty_delivered + picked
                        rental_wizard_line_id.order_item_id.qty_returned_left = rental_wizard_line_id.order_item_id.qty_returned_left + picked
                        if picked > 0:
                            order.has_returnable_lines = True
                    else:
                        rec.picked = rental_wizard_line_id.order_item_id.qty_delivered = rental_wizard_line_id.order_item_id.qty_delivered + picked
                        rental_wizard_line_id.order_item_id.qty_returned_left = rental_wizard_line_id.order_item_id.qty_returned_left + picked
                        rental_wizard_line_id.order_item_id.rental_status_oder_line = 'return'
                        rental_wizard_line_id.order_item_id.qty_delivered_left = 0.0
                        if picked > 0:
                            order.has_returnable_lines = True

                    if send_mail_qty_delivered:
                        template_id = self.env.ref('resource_rental_mgt.email_template_rental_sale').id
                        template = self.env['mail.template'].browse(template_id)
                        template.browse(template_id).send_mail(rec.id, force_send=True)

                elif rec.status == 'return':
                    returned_left = rental_wizard_line_id.order_item_id.qty_returned_left
                    returned = rental_wizard_line_id.qty_returned

                    if returned_left - returned < 0:
                        raise ValidationError('Can not return more than picked!')
                    elif returned < returned_left:
                        rental_wizard_line_id.order_item_id.qty_returned_left = returned_left - returned
                        order.has_late_lines = True
                        order.has_returnable_lines = True
                        rental_wizard_line_id.order_item_id.qty_returned = rental_wizard_line_id.order_item_id.qty_returned + returned
                    else:
                        rental_wizard_line_id.order_item_id.qty_returned = rental_wizard_line_id.order_item_id.qty_returned + returned
                        rental_wizard_line_id.order_item_id.rental_status_oder_line = 'returned'
                        rental_wizard_line_id.order_item_id.qty_returned_left = 0.0

                    if send_mail_qty_returned:
                        template_id = self.env.ref('resource_rental_mgt.email_template_rental_sale').id
                        template = self.env['mail.template'].browse(template_id)
                        template.browse(template_id).send_mail(rec.id, force_send=True)

                    if rental_wizard_line_id.order_item_id.is_late:
                        product_id = int(ICPSudo.get_param('resource_rental_mgt.product_id'))
                        min_extra_hour = int(ICPSudo.get_param('resource_rental_mgt.min_extra_hour'))
                        difference = relativedelta.relativedelta(datetime.datetime.now(),
                                                                 rental_wizard_line_id.return_date)
                        days = difference.days
                        hours = difference.hours

                        if product_id:
                            if (days * 24 + hours) >= min_extra_hour:
                                extra_hourly = rental_wizard_line_id.order_item_id.product_id.extra_hourly
                                extra_daily = rental_wizard_line_id.order_item_id.product_id.extra_daily

                                user_time_zone = pytz.timezone(self.env.user.partner_id.tz)
                                user_time_pickup = pytz.utc.localize(rental_wizard_line_id.pickup_date, is_dst=False)
                                new_pickup_time = user_time_pickup.astimezone(user_time_zone)
                                pickup_time = new_pickup_time.strftime('%d %b %Y, %I:%M:%S %p')

                                user_time_pickup = pytz.utc.localize(rental_wizard_line_id.return_date, is_dst=False)
                                new_pickup_time = user_time_pickup.astimezone(user_time_zone)
                                return_time = new_pickup_time.strftime('%d %b %Y, %I:%M:%S %p')

                                if (extra_hourly or extra_daily) > 0.0:
                                    price_unit = (extra_hourly * hours) + (extra_daily * days)
                                    description = str(
                                        rental_wizard_line_id.order_item_id.product_id.name) + '\nExpected on: ' + str(
                                        pickup_time) + '\nReturned on: ' + str(return_time)
                                    order.order_line = [
                                        (0, 0,
                                         {'product_id': product_id, 'product_uom_qty': 1, 'price_unit': price_unit,
                                          'name': description})]
                                else:
                                    extra_hour = float(ICPSudo.get_param('resource_rental_mgt.extra_hour'))
                                    extra_day = float(ICPSudo.get_param('resource_rental_mgt.extra_day'))
                                    if (extra_hour or extra_day) > 0.0:
                                        price_unit = (extra_hour * hours) + (extra_day * days)
                                        description = 'Expected on: ' + str(pickup_time) + '\nReturned on: ' + str(
                                            return_time)
                                        order.order_line = [
                                            (0, 0,
                                             {'product_id': product_id, 'product_uom_qty': 1, 'price_unit': price_unit,
                                              'name': description})]
                if rental_wizard_line_id.order_item_id.qty_reserved == rental_wizard_line_id.order_item_id.qty_delivered:
                    order.order_line_count_picked += 1

                if rental_wizard_line_id.order_item_id.qty_returned == rental_wizard_line_id.order_item_id.qty_delivered and rental_wizard_line_id.order_item_id.qty_delivered == rental_wizard_line_id.order_item_id.qty_reserved and rental_wizard_line_id.order_item_id.qty_delivered > 0:
                    order.order_line_count_returned += 1

            if order_line_count_all == order.order_line_count_picked:
                order.has_pickable_lines = False
                order.has_late_lines = False
                order.rental_status = 'return'
            if order_line_count_all == order.order_line_count_returned:
                order.rental_status = 'returned'
                order.has_late_lines = False
                order.has_returnable_lines = False


class RentalOrderLine(models.TransientModel):
    _name = 'rental.order.wizard.line'

    rental_order_wizard_id = fields.Many2one('rental.order.wizard')
    product_id = fields.Many2one('product.product', string='Product')
    qty_reserved = fields.Float(string='Reserved')
    qty_delivered = fields.Float(string='Picked-up')
    qty_delivered_left = fields.Float()
    qty_returned = fields.Float(string='Returned')
    qty_returned_left = fields.Float()
    order_item_id = fields.Many2one('sale.order.line')
    is_late = fields.Boolean()
    pickup_date = fields.Datetime()
    return_date = fields.Datetime()
