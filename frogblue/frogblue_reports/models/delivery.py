# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time

from odoo import models, api, fields, _
from odoo.tools.misc import formatLang, format_date, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
from dateutil.relativedelta import relativedelta


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def do_print_picking(self):
        self.write({'printed': True})
        return self.env.ref('frogblue_reports.report_frogblue_delivery_note').report_action(self)


class FrogblueDeliveryNoteReport(models.AbstractModel):
    _name = 'report.frogblue_reports.report_frogblue_deliverynote'
    _description = 'Frogblue Delivery Note Report'

    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)
        counter = 0
        return {
            'doc_ids': docs.ids,
            'doc_model': 'stock.picking',
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
            'get_line_quantities': self._get_line_quantities,
            'get_packages': self._get_packages,
            'get_weee_data': self._get_weee_data,
            'get_serial_numbers_data': self._get_serial_numbers_data,
            'get_user_name': self._get_user_name,
            'get_user_phone': self._get_user_phone,
            'get_salesperson': self._get_salesperson,
            'get_non_eu_country': self._get_non_eu_country,
        }

    def _get_counter(self):
        if self.counter:
            self.counter += 1

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

    def _get_line_quantities(self, line):
        lang = line._context.get('lang', False)
        self = self.with_context(lang=lang)
        amount_ordered = 0.0
        amount_supplied = 0.0

        if line and line.sale_line_id and line.sale_line_id.product_uom_qty:
            amount_ordered = line.sale_line_id.product_uom_qty
        if line and line.product_uom_qty:
            amount_supplied = line.quantity_done
        outstanding_amount = amount_ordered - amount_supplied

        line_quantities = {
            'amount_ordered': amount_ordered,
            'amount_supplied': amount_supplied,
            'outstanding_amount': outstanding_amount,
        }
        return line_quantities

    def _get_packages(self, delivery):
        lang = delivery._context.get('lang', False)
        self = self.with_context(lang=lang)
        packages_dict = {}
        for line in delivery.move_lines:
            for move_line in line.move_line_ids:
                if not move_line.result_package_id:
                    continue
                if not (move_line.qty_done and move_line.qty_done > 0.0):
                    continue
                if packages_dict.get(move_line.result_package_id.name, False):
                    continue
                package_weight = move_line.result_package_id.weight or 0.0
                pack_type_weight = move_line.result_package_id.packaging_id and \
                    move_line.result_package_id.packaging_id.max_weight or 0.0
                package_weight += pack_type_weight
                package_type = move_line.result_package_id.packaging_id or False
                packages_dict[move_line.result_package_id.name] = {
                    'package_type_name': package_type and package_type.name or '',
                    'package_type_length': package_type and package_type.length or 0,
                    'package_type_height': package_type and package_type.height or 0,
                    'package_type_width': package_type and package_type.width or 0,
                    'weight': package_weight,
                    'net_weight': move_line.result_package_id.net_weight or 0.0,
                    'shipping_weight': move_line.result_package_id.shipping_weight or 0.0,
                }
        packages_data = {
            'num_of_packages': len(packages_dict),
            'packages': packages_dict
        }
        return packages_data

    def _get_weee_data(self, delivery):
        weee_data = {
            'print': False,
            'country_name': False,
            'weee_number': False,
        }
        if not (delivery and delivery.company_id and delivery.company_id.id):
            return weee_data
        shipping_partner = delivery and delivery.partner_id or False
        if not (shipping_partner and shipping_partner.country_id and shipping_partner.country_id.id):
            return weee_data
        weee_number = delivery.company_id.get_weee_number(
            delivery.company_id, country_id=shipping_partner.country_id
        )
        if not weee_number:
            return weee_data
        weee_data['print'] = True
        weee_data['country_name'] = shipping_partner.country_id.name or ''
        weee_data['weee_number'] = weee_number
        return weee_data

    def _get_serial_numbers_data(self, delivery):
        lang = delivery._context.get('lang', False)
        self = self.with_context(lang=lang)
        serial_numbers_data = {}
        article_number = 0
        for line in delivery.move_lines:
            serial_numbers_dict = {}
            row = 1
            column = 1
            article_number += 1
            for move_line in line.move_line_ids:
                if not move_line.lot_id:
                    continue
                if not (move_line.qty_done and move_line.qty_done > 0.0):
                    continue
                serial_number = move_line.lot_id and move_line.lot_id.name or False
                if not serial_numbers_dict.get(row, False):
                    serial_numbers_dict[row] = {
                        1: False,
                        2: False,
                        3: False,
                        4: False,
                    }
                serial_numbers_dict[row][column] = serial_number
                if column % 4 == 0:
                    column = 0
                    row += 1
                column += 1
            serial_numbers_data[article_number] = {
                'article_number': article_number,
                'article_code': line.product_id and line.product_id.default_code or '',
                'article_name': line.product_id and line.product_id.name or '',
                'article_qty': line.quantity_done or 0.0,
                'article_uom': line.product_uom and line.product_uom.name or '',
                'serial_numbers': serial_numbers_dict
            }
        return serial_numbers_data

    def _get_user_name(self, delivery):
        user_name = self.env and self.env.user and self.env.user.name or ''
        if delivery.sale_id and delivery.sale_id.user_id:
            user_name = delivery.sale_id.user_id.name or ''
        return user_name

    def _get_user_phone(self, delivery):
        user_phone = self.env and self.env.user and self.env.user.phone or ''
        if delivery.sale_id and delivery.sale_id.user_id:
            user_phone = delivery.sale_id.user_id.phone or ''
        return user_phone

    def _get_salesperson(self, delivery):
        salesperson = self.env and self.env.user
        if delivery.sale_id and delivery.sale_id.user_id:
            salesperson = delivery.sale_id.user_id
        return salesperson

    def _get_non_eu_country(self, country_id):
        europe = self.env.ref('base.europe')
        if country_id not in europe.country_ids.ids:
            return True
        else:
            return False


class FrogbluePickListReport(models.AbstractModel):
    _name = 'report.frogblue_reports.report_frogblue_picklist'
    _description = 'Frogblue Pick List Report'

    def get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)
        self.counter = 0
        return {
            'doc_ids': docs.ids,
            'doc_model': 'stock.picking',
            'docs': docs,
            'time': time,
            'get_formated_date': self._get_formated_date,
            'get_formated_amount': self._get_formated_amount,
            'get_valid_date': self._get_valid_date,
            'get_delivery_date': self._get_delivery_date,
            'get_counter': self._get_counter,
            'set_zero': self._set_zero,
            'get_customer_product_number': self._get_customer_product_number,
            'get_line_quantities': self._get_line_quantities,
            'get_total_data': self._get_total_data,
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

    def _translate_text(self, lang=False, name=False, src=False):
        translation_dao = self.env['ir.translation']
        translation_id = translation_dao.search([(
            'lang', '=', lang), ('name', '=', name), ('src', '=', src)])
        if not translation_id:
            return src
        translation_obj = translation_id[0]
        return translation_obj.value

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

    def _get_line_quantities(self, move_line, line):
        lang = move_line._context.get('lang', False)
        self = self.with_context(lang=lang)
        qty_done = 0.0
        qty_done_weight = 0.0

        if line and line.qty_done:
            qty_done = line.qty_done
        if move_line and move_line.product_id and move_line.product_id.weight:
            qty_done_weight = line.qty_done * move_line.product_id.weight

        line_quantities = {
            'qty_done': qty_done,
            'qty_done_weight': qty_done_weight,
        }
        return line_quantities

    def _get_total_data(self, delivery):
        lang = delivery._context.get('lang', False)
        self = self.with_context(lang=lang)
        total_weight = 0.0
        total_pieces = 0.0

        for move_line in delivery.move_lines:
            for line in move_line.move_line_ids:
                line_weight = line.qty_done * move_line.product_id.weight
                total_weight += line_weight
                total_pieces += line.qty_done

        total_data = {
            'total_weight': total_weight,
            'total_pieces': total_pieces,
        }
        return total_data
