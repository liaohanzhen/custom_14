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
import logging
_logger = logging.getLogger(__name__)

class CustomerQuote(models.Model):
    _name = 'wk.quote.dashboard'
    _description = 'Quote Dashboard'

    name = fields.Char(string="Name", translate=True)
    color = fields.Integer(string='Color Index')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
        ('incart', 'In Cart'),
        ('inprocess', 'In Process'),
        ('sold', 'Sold')]
    )
    sequence = fields.Integer(string='Sequence', help="Gives the sequence order when displaying a list of Quotes")
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env.company)

    def _compute_total_quotes(self):
        company_ids = self._context.get('allowed_company_ids', self.env.user.company_ids)
        domain = ['|',('company_id','in',company_ids),('company_id', '=', False)]
        len_quote_data = len(self.env['quote.quote'].search(domain))
        self.count_total_quotes = len_quote_data

    def _count_pending_quotes(self):
        company_ids = self._context.get('allowed_company_ids', self.env.user.company_ids)
        domain = [('status','=','pending'),'|',('company_id','in',company_ids),('company_id', '=', False)]
        obj = self.env['quote.quote'].search(domain)
        self.count_pending_quotes = len(obj)

    def _count_approved_quotes(self):
        company_ids = self._context.get('allowed_company_ids', self.env.user.company_ids)
        domain = [('status','=','approved'),'|',('company_id','in',company_ids),('company_id', '=', False)]
        obj = self.env['quote.quote'].search(domain)
        self.count_approved_quotes = len(obj)

    def _count_rejected_quotes(self):
        company_ids = self._context.get('allowed_company_ids', self.env.user.company_ids)
        domain = [('status','=','rejected'),'|',('company_id','in',company_ids),('company_id', '=', False)]
        obj = self.env['quote.quote'].search(domain)
        self.count_rejected_quotes = len(obj)

    def _count_expired_quotes(self):
        company_ids = self._context.get('allowed_company_ids', self.env.user.company_ids)
        domain = [('status','=','expired'),'|',('company_id','in',company_ids),('company_id', '=', False)]
        obj = self.env['quote.quote'].search(domain)
        self.count_expired_quotes = len(obj)

    def _count_incart_quotes(self):
        company_ids = self._context.get('allowed_company_ids', self.env.user.company_ids)
        domain = [('status','=','incart'),'|',('company_id','in',company_ids),('company_id', '=', False)]
        obj = self.env['quote.quote'].search(domain)
        self.count_incart_quotes = len(obj)

    def _count_inprocess_quotes(self):
        company_ids = self._context.get('allowed_company_ids', self.env.user.company_ids)
        domain = [('status','=','inprocess'),'|',('company_id','in',company_ids),('company_id', '=', False)]
        obj = self.env['quote.quote'].search(domain)
        self.count_inprocess_quotes = len(obj)

    def _count_sold_quotes(self):
        company_ids = self._context.get('allowed_company_ids', self.env.user.company_ids)
        domain = [('status','=','sold'),'|',('company_id','in',company_ids),('company_id', '=', False)]
        obj = self.env['quote.quote'].search(domain)
        self.count_sold_quotes = len(obj)

    count_total_quotes = fields.Integer(string="Total Quotes", compute="_compute_total_quotes")
    count_pending_quotes = fields.Integer(string="Pending Quotes", compute="_count_pending_quotes")
    count_approved_quotes = fields.Integer(string="Approved Quotes", compute="_count_approved_quotes")
    count_rejected_quotes = fields.Integer(string="Rejected Quotes", compute="_count_rejected_quotes")
    count_expired_quotes = fields.Integer(string="Expired Quotes", compute="_count_expired_quotes")
    count_incart_quotes = fields.Integer(string="In Cart Quotes", compute="_count_incart_quotes")
    count_inprocess_quotes = fields.Integer(string="In Process Quotes", compute="_count_inprocess_quotes")
    count_sold_quotes = fields.Integer(string="Sold Quotes", compute="_count_sold_quotes")

    def action_create_new(self):
        return {
            'name': _('Create Quote'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': "quote.quote",
            'view_id': self.env.ref('website_quote_system.quote_system_customer_quote_form_view').id,
            'context': {},
        }
