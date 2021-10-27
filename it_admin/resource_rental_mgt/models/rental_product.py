# -*- coding: utf-8 -*-
import datetime

from dateutil import relativedelta

from odoo import fields, models, api
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError


class RentalProduct(models.Model):
    _inherit = 'product.template'

    rent_ok = fields.Boolean(string='Can be Rented')
    rental = fields.Char(string='Rental', compute='abc', store=True)
    rental_pricing_ids = fields.One2many('rental.pricing', 'rental_product_id', string='Rental Pricings')
    qty_in_rent = fields.Float(string='Units', compute='action_view_rentals')
    extra_hourly = fields.Float('Extra Hour')
    extra_daily = fields.Float('Extra Day')
    price = fields.Char(compute='get_price')

    @api.depends('rent_ok')
    def abc(self):
        for rec in self:
            if rec.rent_ok:
                rec.rental = '(Rental)'
            else:
                rec.rental = ''

    def get_price(self):
        for rec in self:
            ls = rec.rental_pricing_ids.ids
            if len(ls) > 0:
                record = self.env['rental.pricing'].browse(ls[0])
                rec.price = str(record.price) + ' / ' + str(record.unit)
            else:
                rec.price = str(rec.lst_price)

    def action_view_rentals(self):
        for rec in self:
            sale_order_lines = self.env['sale.order.line'].search(
                [('product_id', 'in', rec.product_variant_ids.ids)])
            qty_delivered = 0.0
            qty_returned = 0.0
            for sale_order_line in sale_order_lines:
                qty_delivered = qty_delivered + sale_order_line.qty_delivered
                qty_returned = qty_returned + sale_order_line.qty_returned
            rec.qty_in_rent = qty_delivered - qty_returned


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def name_get(self):
        res = []
        for field in self:
            if field.rental == '(Rental)':
                res.append((field.id, '%s %s' % (field.name, field.rental)))
            else:
                res.append((field.id, '%s %s' % (field.name, '')))
        return res


class RentalPricing(models.Model):
    _name = 'rental.pricing'
    _order = 'price asc'

    duration = fields.Integer(string='Duration', default=1)
    unit = fields.Selection([('hour', 'Hours'), ('day', 'Days'), ('week', 'Weeks'), ('month', 'Months')], default='day',
                            string='Unit')
    rental_product_id = fields.Many2one('product.template')
    price = fields.Float(string='price', default=1.0)


class RentalOrder(models.Model):
    _inherit = 'sale.order'

    is_rental_order = fields.Boolean('Rental Order')
    has_pickable_lines = fields.Boolean()
    has_returnable_lines = fields.Boolean()
    has_late_lines = fields.Boolean()
    rental_status = fields.Selection(
        [('draft', 'Quotation'), ('sent', 'Quotation Sent'), ('pickup', 'Reserved'), ('return', 'Picked-up'),
         ('returned', 'Returned'), ('cancel', 'Cancelled')], default='draft')
    is_pick_date_today = fields.Boolean()
    is_return_date_today = fields.Boolean()
    time = fields.Datetime(compute='run_it')
    order_line_count_picked = fields.Integer()
    order_line_count_returned = fields.Integer()

    def run_it(self):
        for rec in self:
            rec.time = datetime.datetime.now()
            self.check_pick_date()
            self.check_return_date()

    def check_pick_date(self):
        for rec in self:
            today = datetime.datetime.now()
            for order_line_item in rec.order_line:
                if order_line_item.pickup_date:
                    if order_line_item.pickup_date.date() == today.date():
                        self._cr.execute(
                            """UPDATE sale_order SET is_pick_date_today=%r WHERE id='%d'""" % (True, rec.id))
                        break
                    else:
                        self._cr.execute(
                            """UPDATE sale_order SET is_pick_date_today=%r WHERE id='%d'""" % (False, rec.id))

    def check_return_date(self):
        for rec in self:
            today = datetime.datetime.now()
            for order_line_item in rec.order_line:
                if order_line_item.return_date:
                    if order_line_item.return_date.date() == today.date():
                        rec.is_return_date_today = True
                        self._cr.execute(
                            """UPDATE sale_order SET is_return_date_today=%r WHERE id='%d'""" % (True, rec.id))
                        break
                    else:
                        self._cr.execute(
                            """UPDATE sale_order SET is_return_date_today=%r WHERE id='%d'""" % (False, rec.id))

    def write(self, vals):
        if 'state' in vals:
            if vals['state'] == 'draft':
                vals['rental_status'] = 'draft'
            elif vals['state'] == 'sent':
                vals['rental_status'] = 'sent'
            elif vals['state'] == 'sale':
                vals['rental_status'] = 'pickup'
                vals['has_pickable_lines'] = True
            elif vals['state'] == 'cancel':
                vals['rental_status'] = 'cancel'
        result = super(RentalOrder, self).write(vals)
        return result

    def open_pickup(self):
        for rec in self:
            order_items = []
            for order_item in rec.order_line:
                order_items.append([0, 0, {'order_item_id': order_item.id,
                                           'product_id': order_item.product_id.id,
                                           'qty_reserved': order_item.qty_reserved,
                                           'qty_delivered': order_item.qty_reserved - order_item.qty_delivered,
                                           'qty_returned': order_item.qty_delivered - order_item.qty_returned
                                           }])
            res_id = (
                self.env['rental.order.wizard'].create({'rental_wizard_line_ids': order_items, 'status': 'pickup'})).id
            return {
                'name': 'Validate Pickup',
                'type': 'ir.actions.act_window',
                'res_model': 'rental.order.wizard',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': False,
                'res_id': res_id,
                'target': 'new',
            }

    def open_return(self):
        for rec in self:

            order_items = []
            for order_item in rec.order_line:
                difference = relativedelta.relativedelta(order_item.return_date, datetime.datetime.now())
                days = difference.days
                hours = difference.hours
                if hours < 0 or days < 0:
                    order_item.is_late = True
                    rec.has_late_lines = True
                order_items.append([0, 0, {'order_item_id': order_item.id,
                                           'product_id': order_item.product_id.id,
                                           'qty_reserved': order_item.qty_reserved,
                                           'qty_delivered': order_item.qty_delivered,
                                           'qty_returned': order_item.qty_delivered - order_item.qty_returned,
                                           'is_late': order_item.is_late,
                                           'pickup_date': order_item.pickup_date,
                                           'return_date': order_item.return_date
                                           }])
            res = self.env['rental.order.wizard'].create({'rental_wizard_line_ids': order_items, 'status': 'return'}).id
            return {
                'name': 'Validate Return',
                'type': 'ir.actions.act_window',
                'res_model': 'rental.order.wizard',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': False,
                'res_id': res,
                'target': 'new',
            }


class OderLines(models.Model):
    _inherit = 'sale.order.line'

    is_rental = fields.Boolean()
    is_product_rentable = fields.Boolean()
    pickup_date = fields.Datetime(string='Pickup date')
    return_date = fields.Datetime(string='Return date')
    rental_updateable = fields.Boolean()
    qty_reserved = fields.Float(string='Reserved')
    # qty_delivered = fields.Float()
    qty_delivered_left = fields.Float()
    qty_returned = fields.Float(string='Returned', digits=dp.get_precision('Product Unit of Measure'), readonly=True)
    qty_returned_left = fields.Float()
    name_tmp = fields.Char()
    is_late = fields.Boolean(default=False)
    rental_status_oder_line = fields.Selection(
        [('draft', 'Quotation'), ('sent', 'Quotation Sent'), ('pickup', 'Reserved'), ('return', 'Picked-up'),
         ('returned', 'Returned'), ('cancel', 'Cancelled')], default='draft')

    @api.onchange('product_id')
    def product_changed(self):
        for rec in self:
            if rec.product_id.rent_ok:
                rec.is_product_rentable = True

    def get_rent(self):
        for rec in self:
            name = rec.product_id.name
            if rec.product_id.description_sale:
                rec.name_tmp = rec.product_id.name + rec.product_id.description_sale
            else:
                rec.name_tmp = rec.product_id.name
            price_list = rec.product_id.rental_pricing_ids.ids
            if len(price_list) > 0:
                unit_price = rec.product_id.rental_pricing_ids[0].price
                if rec.pickup_date and rec.return_date:
                    pickup_date = rec.pickup_date
                    return_date = rec.return_date
                    min_duration = int(rec.product_id.rental_pricing_ids[0].duration)
                    unit = rec.product_id.rental_pricing_ids[0].unit
                    if unit == 'hour':
                        return_date = pickup_date + datetime.timedelta(hours=min_duration)
                    elif unit == 'day':
                        return_date = pickup_date + datetime.timedelta(days=min_duration)
                    elif unit == 'week':
                        return_date = pickup_date + datetime.timedelta(weeks=min_duration)
                    elif unit == 'month':
                        return_date = pickup_date + datetime.timedelta(days=min_duration * 30)
                else:
                    pickup_date = datetime.datetime.now()
                    return_date = datetime.datetime.now()
                    min_duration = int(rec.product_id.rental_pricing_ids[0].duration)
                    unit = rec.product_id.rental_pricing_ids[0].unit

                    if unit == 'hour':
                        return_date = pickup_date + datetime.timedelta(hours=min_duration)
                    elif unit == 'day':
                        return_date = pickup_date + datetime.timedelta(days=min_duration)
                    elif unit == 'week':
                        return_date = pickup_date + datetime.timedelta(weeks=min_duration)
                    elif unit == 'month':
                        return_date = pickup_date + datetime.timedelta(days=min_duration * 30)
                return {
                    'name': 'Rental',
                    'type': 'ir.actions.act_window',
                    'res_model': 'rent.wizard',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': False,
                    'res_id': False,
                    'target': 'new',
                    'context': {
                        'default_product_id': name,
                        'default_unit_price': unit_price,
                        'default_unit_price2': unit_price,
                        'default_pickup_date': pickup_date,
                        'default_quantity': 1,
                        'default_return_date': return_date,
                        'default_duration': min_duration,
                        'default_duration_unit': unit,
                    }
                }
            else:
                raise ValidationError('Update the product rental pricing!')
