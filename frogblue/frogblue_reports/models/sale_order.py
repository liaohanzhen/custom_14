# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import models, api, fields, _
from odoo.tools.misc import formatLang, format_date, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from dateutil.relativedelta import relativedelta


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def print_quotation(self):
        super(SaleOrder, self).print_quotation()
        return self.env.ref('frogblue_reports.report_frogblue_sale_order').report_action(self)


class FrogblueSaleOrderReport(models.AbstractModel):
    _name = 'report.frogblue_reports.report_frogblue_saleorder'
    _description = 'Frogblue Sale Order Report'

    def _get_report_values(self, docids, data=None):
        docs = self.env['sale.order'].browse(docids)
        counter = 0
        return {
            'doc_ids': docs.ids,
            'doc_model': 'sale.order',
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
            'get_tax': self._get_tax,
            'get_subtotal': self._get_subtotal,
            'get_right_header': self._get_right_header,
            'get_customer_product_number': self._get_customer_product_number,
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
        valid_date = obj.validity_date
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
        for line in o.order_line:
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

    def _get_tax(self, obj):
        lang = obj._context.get('lang', False)
        self = self.with_context(lang=lang)
        ret = []
        taxes = []
        for line in obj.order_line:
            # if line.alternative_product == True:
            #     continue
            for account_tax in line.tax_id:
                if not account_tax in taxes:
                    taxes.append(account_tax)
        for account_tax in taxes:
            tax = []
            ret_amount = 0
            lines_amount = 0
            for line in obj.order_line:
                # if line.alternative_product == True:
                #     continue
                if account_tax in line.tax_id:
                    lines_amount += line.price_subtotal
                    amount = line.price_tax
                    if amount:
                        ret_amount += amount
            tax.append(account_tax.description)
            tax.append("%.2f" % ret_amount)
            ret.append(tax)
        return ret

    def _get_subtotal(self, lines):
        lang = lines._context.get('lang', False)
        self = self.with_context(lang=lang)
        sum = 0
        for line in lines:
            # if line.alternative_product == True:
            #     continue  # skip alternate product lines in claculating subtotal
            if line.tax_id.price_include == False:
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

    def _get_weee_data(self, sale_order):
        weee_data = {
            'print': False,
            'country_name': False,
            'weee_number': False,
        }
        if not (sale_order and sale_order.company_id and sale_order.company_id.id):
            return weee_data
        shipping_partner = sale_order and sale_order.partner_shipping_id or False
        if not (shipping_partner and shipping_partner.country_id and shipping_partner.country_id.id):
            return weee_data
        weee_number = sale_order.company_id.get_weee_number(
            sale_order.company_id, country_id=shipping_partner.country_id
        )
        if not weee_number:
            return weee_data
        weee_data['print'] = True
        weee_data['country_name'] = shipping_partner.country_id.name or ''
        weee_data['weee_number'] = weee_number
        return weee_data


class FrogblueSaleOrderReportProforma(models.AbstractModel):
    _name = 'report.frogblue_reports.report_frogblue_saleorder_proforma'
    _description = 'Frogblue Sale Order Report Proforma'

    def _get_report_values(self, docids, data=None):
        docs = self.env['sale.order'].browse(docids)
        counter = 0
        return {
            'doc_ids': docs.ids,
            'doc_model': 'sale.order',
            'docs': docs,
            'time': time,
            'get_formated_date': self._get_formated_date,
            'get_formated_amount': self._get_formated_amount,
            'get_counter': self._get_counter,
            'set_zero': self._set_zero,
            'show_discount': self._show_discount,
            'get_salutation': self._get_salutation,
            'get_image': self._get_image,
            'get_tax': self._get_tax,
            'get_subtotal': self._get_subtotal,
            'get_right_header': self._get_right_header,
            'get_customer_product_number': self._get_customer_product_number,
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
        for line in o.order_line:
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

    def _get_tax(self, obj):
        lang = obj._context.get('lang', False)
        self = self.with_context(lang=lang)
        ret = []
        taxes = []
        for line in obj.order_line:
            # if line.alternative_product == True:
            #     continue
            for account_tax in line.tax_id:
                if not account_tax in taxes:
                    taxes.append(account_tax)
        for account_tax in taxes:
            tax = []
            ret_amount = 0
            lines_amount = 0
            for line in obj.order_line:
                # if line.alternative_product == True:
                #     continue
                if account_tax in line.tax_id:
                    lines_amount += line.price_subtotal
                    amount = line.price_tax
                    if amount:
                        ret_amount += amount
            tax.append(account_tax.description)
            tax.append("%.2f" % ret_amount)
            ret.append(tax)
        return ret

    def _get_subtotal(self, lines):
        lang = lines._context.get('lang', False)
        self = self.with_context(lang=lang)
        sum = 0
        for line in lines:
            # if line.alternative_product == True:
            #     continue  # skip alternate product lines in claculating subtotal
            if line.tax_id.price_include == False:
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
        return ''

    def _get_weee_data(self, sale_order):
        weee_data = {
            'print': False,
            'country_name': False,
            'weee_number': False,
        }
        if not (sale_order and sale_order.company_id and sale_order.company_id.id):
            return weee_data
        shipping_partner = sale_order and sale_order.partner_shipping_id or False
        if not (shipping_partner and shipping_partner.country_id and shipping_partner.country_id.id):
            return weee_data
        weee_number = sale_order.company_id.get_weee_number(
            sale_order.company_id, country_id=shipping_partner.country_id
        )
        if not weee_number:
            return weee_data
        weee_data['print'] = True
        weee_data['country_name'] = shipping_partner.country_id.name or ''
        weee_data['weee_number'] = weee_number
        return weee_data
