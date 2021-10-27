# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import models, api, fields, _
from odoo.tools.misc import formatLang, format_date, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from dateutil.relativedelta import relativedelta


class AccountFiscalPosition(models.Model):
    _inherit = 'account.fiscal.position'

    tax_exempt_text = fields.Char('Tax Exempt Text', help="i.e. Tax-exempt intra-Community supply", translate=True)


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    def invoice_print(self):
        self.ensure_one()
        self.sent = True
        return self.env.ref('frogblue_reports.report_frogblue_account_invoice').report_action(self)


class FrogblueAccountInvoiceReport(models.AbstractModel):
    _name = 'report.frogblue_reports.report_frogblue_accountinvoice'
    _description = 'Frogblue Account Invoice Report'

    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        counter = 0
        return {
            'doc_ids': docs.ids,
            'doc_model': 'account.move',
            'docs': docs,
            'time': time,
            'get_formated_date': self._get_formated_date,
            'get_formated_amount': self._get_formated_amount,
            'get_valid_date': self._get_valid_date,
            'get_delivery_date': self._get_delivery_date,
            'get_counter': self._get_counter,
            'set_zero': self._set_zero,
            'show_discount': self._show_discount,
            'get_salutation': self._get_salutation,
            'get_image': self._get_image,
            'get_subtotal': self._get_subtotal,
            'get_right_header': self._get_right_header,
            'get_customer_product_number': self._get_customer_product_number,
            'get_delivery_address': self._get_delivery_address,
            'get_related_sale_order': self._get_related_sale_order,
            'get_deliveries': self._get_deliveries,
            'get_related_cust_ref': self._get_related_cust_ref,
            'get_related_date_order': self._get_related_date_order,
            'get_related_sale_orders': self._get_related_sale_orders,
            'get_payment_term': self._get_payment_term,
            'get_weee_data': self._get_weee_data,
        }

    def _get_counter(self):
        self.counter += 1
        return self.counter

    def _get_formated_amount(self, env=False, amount=False, currency_obj=False, obj=False):
        lang = obj._context.get('lang', False)
        self = self.with_context(lang=lang)
        if not env:
            env = self.env
        if not amount:
            amount = 0.0
        ret_amount = formatLang(env, amount, currency_obj=currency_obj)
        return ret_amount

    def _get_formated_date(self, date=False, lang_code=False, date_format=False, now=False):
        if now:
            date = datetime.now()
        res = format_date(self.env, date, lang_code=lang_code, date_format=date_format)
        return res

    def _get_valid_date(self, obj):
        lang = obj._context.get('lang', False)
        valid_date = datetime.now() + relativedelta(days=14)
        if valid_date:
            valid_date = self._get_formated_date(date=valid_date, lang_code=lang)
        return valid_date

    def _get_delivery_date(self, line, sale_order):
        lang = sale_order._context.get('lang', False)
        delivery_date = False
        if sale_order.date_order:
            delivery_date = datetime.strptime(sale_order.date_order, DEFAULT_SERVER_DATETIME_FORMAT)
        if sale_order.effective_date:
            delivery_date = datetime.strptime(sale_order.effective_date, DEFAULT_SERVER_DATE_FORMAT)
        if sale_order.confirmation_date:
            delivery_date = datetime.strptime(sale_order.confirmation_date, DEFAULT_SERVER_DATETIME_FORMAT)
        if delivery_date:
            unit = 'days'
            interval = line.customer_lead
            kwargs = {
                unit: interval
            }
            delivery_date = delivery_date + relativedelta(**kwargs)
            delivery_date = self._get_formated_date(date=delivery_date, lang_code=lang)
        return delivery_date

    def _set_zero(self):
        self.counter = 0

    def _get_right_header(self, o):
        text = _('Your Contact')
        lang = o.partner_id.lang or o._context.get('lang', False)
        if not lang:
            return text
        if lang == 'en_US':
            return 'Your Contact'
        name = 'addons/frogblue_reports/report/purchase.py'
        translated_text = self._translate_text(lang=lang, name=name, src=text)
        return translated_text

    def _translate_text(self, lang=False, name=False, src=False):
        translation_dao = self.env['ir.translation']
        translation_id = translation_dao.search([(
            'lang', '=', lang), ('name', '=', name), ('src', '=', src)])
        if not translation_id:
            return src
        translation_obj = translation_id[0]
        return translation_obj.value

    def _show_discount(self, o):
        for line in o.invoice_line_ids:
            if line.discount:
                return True
        return False

    def _get_salutation(self, partner):
        if partner.title and 'Herr' in partner.title.name:
            return partner.title.name
        if partner.title and 'Frau' in partner.title.name:
            return partner.title.name
        return ''

    def _get_image(self, image):
        return ('data:image/png;base64,%s') % image if image else ''

    def _get_subtotal(self, lines):
        lang = lines._context.get('lang', False)
        self = self.with_context(lang=lang)
        sum = 0
        for line in lines:
            # if line.alternative_product == True:
            #     continue  # skip alternate product lines in claculating subtotal
            if line.invoice_line_tax_ids.price_include == False:
                sum += line.price_subtotal
            else:
                sum += line.price_total
        return sum

    def _get_customer_product_number(self, product, customer):
        if not product:
            return ''
        if not customer:
            return ''
        for customer_product_code_id in product.customer_product_code_ids:
            if customer_product_code_id.customer_id.id == customer.id:
                return customer_product_code_id.product_code or ''
        for customer_product_code_id in product.customer_product_code_ids:
            if customer_product_code_id.customer_id.id == customer.commercial_partner_id.id:
                return customer_product_code_id.product_code or ''
        return ''

    def _get_related_sale_order(self, obj):
        if obj.move_type in ['out_refund','in_refund'] and obj.env['account.move'].search([('name', '=', obj.invoice_origin),('name', '!=', False)]):
            return obj.env['account.move'].search([('name', '=', obj.invoice_origin),('name','!=', False)]).invoice_line_ids.mapped('sale_line_ids').mapped('order_id')
        else:
            return obj.invoice_line_ids.mapped('sale_line_ids').mapped('order_id')

    def _get_delivery_address(self, obj):
        orders = self._get_related_sale_order(obj)
        ret = []
        for order in orders:
            if order and order.partner_shipping_id and order.partner_shipping_id.id != obj.partner_id.id:
                ret.append(order.partner_shipping_id)
        return ret

    def _get_deliveries(self, sale_orders):
        ret = []
        for order in sale_orders:
            deliveries = order.picking_ids.filtered(lambda d: d.state== 'done')
            if deliveries:
                max_delivery = max(deliveries, key=lambda d: d.date_done)
                ret.append((max_delivery.name, max_delivery.date_done))
        ret1 = [i[0] for i in ret]
        ret2 = [datetime.strptime(str(i[1]),'%Y-%m-%d %H:%M:%S').strftime('%d.%m.%Y') for i in ret]
        return ret1, ret2

    def _get_related_cust_ref(self, sale_orders):
        ret = ''
        for order in sale_orders:
            if order.client_order_ref:
                ret += ('%s, ') % order.client_order_ref
        return ret[:-2]

    def _get_related_date_order(self, sale_orders, lang_code):
        ret = ''
        for order in sale_orders:
            if order.date_order:
                ret += ('%s, ') % (self._get_formated_date(date=order.date_order, lang_code=lang_code))
        return ret[:-2]

    def _get_related_sale_orders(self, sale_orders):
        ret = ''
        for order in sale_orders:
            ret += ('%s, ') % order.name
        return ret[:-2]

    def _get_payment_term(self, invoice):
        res = ''
        if not invoice:
            return res
        if not invoice.invoice_payment_term_id:
            return res
        if invoice.invoice_payment_term_id and invoice.invoice_payment_term_id.note:
            res = '%s%s ' % (res, invoice.invoice_payment_term_id.note)
        if invoice.invoice_payment_term_id and invoice.amount_total:
            res = '%s(%s) ' % (res, formatLang(invoice.env, invoice.amount_total, currency_obj=invoice.currency_id) or '')
        # if invoice.invoice_payment_term_id and invoice.date_due:
        #     date_due_formated = self._get_formated_date(date=invoice.date_due)
        #     due_text = _('due on')
        #     res = '%s%s %s ' % (res, due_text, date_due_formated)
        return res

    def _get_weee_data(self, invoice):
        weee_data = {
            'print': False,
            'country_name': False,
            'weee_number': False,
        }
        if not (invoice and invoice.company_id and invoice.company_id.id):
            return weee_data
        shipping_partner = invoice and invoice.partner_shipping_id or False
        if not (shipping_partner and shipping_partner.country_id and shipping_partner.country_id.id):
            return weee_data
        weee_number = invoice.company_id.get_weee_number(
            invoice.company_id, country_id=shipping_partner.country_id
        )
        if not weee_number:
            return weee_data
        weee_data['print'] = True
        weee_data['country_name'] = shipping_partner.country_id.name or ''
        weee_data['weee_number'] = weee_number
        return weee_data
