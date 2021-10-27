# -*- coding: utf-8 -*-
#############################################################################
# Author      : Webkul Software Pvt. Ltd. (<https://webkul.com/>)
# Copyright(c): 2015-Present Webkul Software Pvt. Ltd.
# License URL : https://store.webkul.com/license.html/
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
# If not, see <https://store.webkul.com/license.html/>
#############################################################################

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date, datetime, timedelta
from odoo.addons import decimal_precision as dp
from dateutil.relativedelta import relativedelta

class CustomerQuote(models.Model):
    _name = 'quote.quote'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _rec_name = 'product_id'
    _order = 'id desc'
    _description = 'Customer Quotation'

    name = fields.Char(
        string="Quotation No.",
        readonly=True,
        help="Unique Number for Quotation.",
        track_visibility='onchange',
        default=lambda self: _('New'),
        copy=False,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        default=lambda self: self.env.user.partner_id,
    )
    product_id = fields.Many2one(comodel_name='product.product', string='Product', required=True)
    currency_id = fields.Many2one(string="currency", related="product_id.currency_id")
    website_currency_id = fields.Many2one(
        "res.currency",
        string="Website Currency",
        default=lambda self: self.env.user.company_id.currency_id,
        help="The currency in which the quote has been requested.",
    )
    prod_actual_price = fields.Float(string="Actual Price", related="product_id.list_price", readonly=True)
    prod_min_qty = fields.Float(string="Minimum Quantity", related="product_id.min_qty", readonly=True)
    prod_valid_days = fields.Integer(string="Valid Upto", related="product_id.valid_days", readonly=True)
    qty = fields.Float(string='Quantity', required=True)
    price = fields.Float(string='Price(per item)', required=True)
    description = fields.Text(string='Description')
    status = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
        ('incart', 'In Cart'),
        ('inprocess', 'In Process'),
        ('sold', 'Sold')],
        string="Status",
        default="pending",
        track_visibility='onchange',
        copy=False,
    )
    sale_order_id = fields.Many2one(comodel_name='sale.order', string="Sale Order", copy=False,)
    sale_order_line_id = fields.Many2one(comodel_name='sale.order.line', string="Sale Order Line", copy=False,)
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        default=lambda self: self.env.user.partner_id,
    )
    total_amount = fields.Float('Total', compute="compute_total_amount")
    approved_date = fields.Date('Approved Date', copy=False,)
    expired_date = fields.Date('Expired Date', copy=False,)
    company_id = fields.Many2one(
        'res.company',
        default=lambda self: self.env.user.company_id,
        string='Company',
        readonly=True,
    )
    notify_admin_on_new_quote = fields.Boolean(
        'Notify Admin on New Quote',
        default=lambda self: self.env['ir.default'].get("customer.quote.settings", 'notify_admin_on_new_quote'),
    )
    notify_customer_on_new_quote = fields.Boolean(
        'Notify Customer on New Quote',
        default=lambda self: self.env['ir.default'].get("customer.quote.settings", 'notify_customer_on_new_quote'),
    )

    notify_salesman_on_new_quote = fields.Boolean(
        'Notify Salesman on New Quote',
        default=lambda self: self.env['ir.default'].get("customer.quote.settings", 'notify_salesman_on_new_quote'),
     )
    notify_customer_on_quote_state_change = fields.Boolean(
        'Notify Customer on Quote State Update',
        default=lambda self: self.env['ir.default'].get("customer.quote.settings", 'notify_customer_on_quote_state_change'),
    )
    salesman_id = fields.Many2one(
        comodel_name="res.users",
        string="Salesman",
        default=lambda self: self.env['ir.default'].get("customer.quote.settings", 'salesman_id')
    )
    website_quote_price = fields.Float(
        'Website Quote Unit price',
        compute='_compute_website_quote_price',
        digits='Quote Price'
    )
    website_quote_total_amount = fields.Float(
        'Website Quote Total Amount',
        compute='_compute_website_quote_price',
        digits='Quote Total Amount'
    )

    @api.depends('price', 'total_amount')
    def _compute_website_quote_price(self):
        current_pl = self.env['website'].get_current_website().pricelist_id
        for quote in self:
            from_currency = quote.website_currency_id
            to_currency = current_pl.currency_id
            quote.website_quote_price = from_currency.compute(quote.price, to_currency)
            quote.website_quote_total_amount = from_currency.compute(quote.qty * quote.price, to_currency)

    def but_approve_quote(self):
        self.write({'status': 'approved'})
        for rec in self:
            if rec.status == 'approved':
                rec.approved_date = date.today()
                valid_days = rec.product_id.valid_days
                app_date = datetime.strptime(str(rec.approved_date), '%Y-%m-%d').date()
                exp_date = app_date + timedelta(days=valid_days)
                rec.expired_date = datetime.strptime(str(exp_date), '%Y-%m-%d').date()
        self.send_quote_status_update_mail()

    def send_quote_status_update_mail(self):

        for rec in self:
            template_obj = self.env['mail.template']
            quote_config_obj = self.env['customer.quote.settings'].sudo().get_values()
            if quote_config_obj.get("notify_customer_on_quote_state_change")==True and quote_config_obj.get("notify_customer_on_quote_state_change_m_tmpl_id"):
                temp_id = quote_config_obj["notify_customer_on_quote_state_change_m_tmpl_id"]
                if not temp_id:
                    temp_id = self.env.sudo().ref("website_quote_system.quote_status_update_email_template_to_customer")
                if temp_id:
                    template_obj.sudo().browse(temp_id).send_mail(rec.id, force_send=True)

    def send_quote_creation_mail(self):
        for rec in self:
            template_obj = self.env['mail.template']
            quote_config_obj = self.env['customer.quote.settings'].sudo().get_values()

            if quote_config_obj.get("notify_admin_on_new_quote")==True and quote_config_obj.get("notify_admin_on_new_quote_m_tmpl_id"):
                temp_id = quote_config_obj["notify_admin_on_new_quote_m_tmpl_id"]
                if not temp_id:
                    temp_id = self.env.sudo().ref("website_quote_system.quote_create_email_template_to_admin")
                if temp_id:
                    template_obj.browse(temp_id).sudo().send_mail(rec.id, force_send=True)

            if quote_config_obj.get("notify_customer_on_new_quote")==True and quote_config_obj.get("notify_customer_on_new_quote_m_tmpl_id"):
                temp_id = quote_config_obj["notify_customer_on_new_quote_m_tmpl_id"]
                if not temp_id:
                    temp_id = self.env.sudo().ref("website_quote_system.quote_create_email_template_to_customer")
                if temp_id:
                    template_obj.browse(temp_id).sudo().send_mail(rec.id, force_send=True)

            if quote_config_obj.get("notify_salesman_on_new_quote")==True and quote_config_obj.get("notify_salesman_on_new_quote_m_tmpl_id"):
                temp_id = quote_config_obj["notify_salesman_on_new_quote_m_tmpl_id"]
                if not temp_id:
                    temp_id = self.env.sudo().ref("website_quote_system.quote_create_email_template_to_salesman")
                if temp_id:
                    template_obj.sudo().browse(temp_id).sudo().send_mail(rec.id, force_send=True)

    @api.model
    def create(self, vals):
        qty = vals.get('qty')
        if qty <= 0:
            raise UserError(_("Quantity must be greater than zero."))
        price = vals.get('price')
        if price <= 0:
            raise UserError(_("Price must be a greater than zero."))
        vals['name'] = self.env['ir.sequence'].next_by_code("quote.quote")
        res = super(CustomerQuote, self).create(vals)
        if vals.get("customer_id"):
            res.message_subscribe([vals.get("customer_id")])
        res.send_quote_creation_mail()
        return res

    def write(self, vals):
        if vals.get('qty') or vals.get('qty') == 0:
            qty = vals.get('qty')
            if qty == 0 or qty < 0:
                raise UserError(_("Quantity must be greater than zero."))
        if vals.get('price') or vals.get('price') == 0:
            price = vals.get('price')
            if price == 0 or price < 0:
                raise UserError(_("Price must be a greater than zero."))
        res = super(CustomerQuote, self).write(vals)
        return res

    def unlink(self):
        for rec in self:
            if rec.sale_order_id.state not in ['draft']:
                raise UserError(_('You cannot delete a Quote Request if the corresponding Sale Order is in Quotation Sent/Confirmed state.!'))
            rec.sale_order_line_id.unlink()
        res = super(CustomerQuote, self).unlink()
        return res

    @api.depends('qty', 'price')
    def compute_total_amount(self):
        self.total_amount = self.qty * self.price
        return True

    def but_reject_quote(self):
        self.write({'status': 'rejected'})
        self.send_quote_status_update_mail()
        return True

    @api.model
    def quote_status_update_scheduler_queue(self):
        obj = self.search([])
        for rec in obj:
            sale_order_line_obj = self.env['sale.order.line'].search([
                ('id', '=', rec.sale_order_line_id.id)
            ])
            sale_order_obj = self.env['sale.order'].search([('id', '=', rec.sale_order_id.id)])
            d2 = date.today()
            dt = rec.expired_date
            if dt:
                d1 = datetime.strptime(str(dt), "%Y-%m-%d").date()
                rd = relativedelta(d2, d1)
            if rec.status == 'approved':
                if rd.days >= 0 and rd.months >= 0 and rd.years >= 0:
                    rec.status = 'expired'
                    self.send_quote_status_update_mail()
            elif rec.status == 'incart':
                if sale_order_line_obj.invoice_status == 'invoiced':
                    rec.status = 'sold'
                    self.send_quote_status_update_mail()
                elif sale_order_line_obj.state == 'sale':
                    rec.status = 'inprocess'
                    self.send_quote_status_update_mail()
                else:
                    if rd.days >= 0 and rd.months >= 0 and rd.years >= 0:
                        rec.status = 'expired'
                        self.send_quote_status_update_mail()
            elif rec.status == 'inprocess':
                if sale_order_line_obj.invoice_status == 'invoiced':
                    rec.status = 'sold'
                    self.send_quote_status_update_mail()
                elif sale_order_line_obj.state == 'sale' and sale_order_obj.transaction_ids:
                    rec.status = 'inprocess'
                    self.send_quote_status_update_mail()
            else:
                pass

    def _compute_access_url(self):
        super(CustomerQuote, self)._compute_access_url()
        for q in self:
            q.access_url = '/my/quote/%s' % (q.id)
