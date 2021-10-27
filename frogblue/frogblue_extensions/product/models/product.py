# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    version_number = fields.Char('Version Number')
    vde = fields.Boolean('VDE')
    emv = fields.Boolean('EMV')
    funk = fields.Boolean('Funk')
    etim = fields.Text('ETIM')
    ext_show_price = fields.Boolean('Show Prices', compute='show_product_price', default=False)
    ext_show_price_kanban_tree = fields.Boolean('Show Price', compute='show_product_price_kanban_tree', default=False)

    def show_product_price(self):
        if self.env.user.has_group('frogblue_extensions.group_ext_user_products'):
            self.ext_show_price = True
        else:
            self.ext_show_price = False

    def show_product_price_kanban_tree(self):
        for record in self:
            if self.env.user.has_group('frogblue_extensions.group_ext_user_products'):
                record.ext_show_price_kanban_tree = True
            else:
                record.ext_show_price_kanban_tree = False

    standard_price = fields.Float(tracking=True)
    lst_price = fields.Float(tracking=True)

    def write(self, vals):
        no_tax_text = _(" No tax selected")
        previous_taxes_products = {}
        for product in self:
            previous_taxes = ""
            for tax in product.taxes_id:
                previous_taxes += " %s" % (tax.name,)
            if not previous_taxes_products.get(product.id, False):
                previous_taxes_products[product.id] = {
                    'customer_tax': no_tax_text,
                    'supplier_tax': no_tax_text
                }
            previous_taxes_products[product.id]['customer_tax'] = previous_taxes
            previous_supplier_taxes = ""
            for tax in product.supplier_taxes_id:
                previous_supplier_taxes += " %s" % (tax.name,)
            if not previous_taxes_products.get(product.id, False):
                previous_taxes_products[product.id] = {
                    'customer_tax': no_tax_text,
                    'supplier_tax': no_tax_text
                }
            previous_taxes_products[product.id]['supplier_tax'] = previous_supplier_taxes
        res = super(ProductTemplate, self).write(vals)
        taxes = vals.get('taxes_id', [])
        new_taxes = ""
        for tax_signal in taxes:
            signal = tax_signal[0]
            tax_ids = tax_signal[2]
            if signal != 6:
                continue
            if len(tax_ids) < 1:
                new_taxes += no_tax_text
            taxes = self.env['account.tax'].browse(tax_ids)
            for tax in taxes:
                new_taxes += " %s" % (tax.name,)
        supplier_taxes = vals.get('supplier_taxes_id', [])
        new_supplier_taxes = ""
        for tax_signal in supplier_taxes:
            signal = tax_signal[0]
            supplier_tax_ids = tax_signal[2]
            if signal != 6:
                continue
            if len(supplier_tax_ids) < 1:
                new_supplier_taxes += no_tax_text
            supplier_taxes = self.env['account.tax'].browse(supplier_tax_ids)
            for tax in supplier_taxes:
                new_supplier_taxes += " %s" % (tax.name,)
        for product in self:
            previous_taxes = previous_taxes_products.get(
                product.id,
                no_tax_text
            )
            if taxes and previous_taxes['customer_tax'] != new_taxes:
                body = "Previous customer taxes:%s<br/>" % (previous_taxes['customer_tax'],)
                body += "New customer taxes:%s<br/>" % (new_taxes,)
                subject = "Customer taxes changed:"
                product.message_post(body=body, subject=subject)
            if supplier_taxes and previous_taxes['supplier_tax'] != new_supplier_taxes:
                body = "Previous supplier taxes:%s<br/>" % (previous_taxes['supplier_tax'],)
                body += "New supplier taxes:%s<br/>" % (new_supplier_taxes,)
                subject = "Supplier taxes changed:"
                product.message_post(body=body, subject=subject)
        return res


class SupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    ext_show_price = fields.Boolean('Show Price', compute='show_product_price', default=False)

    def show_product_price(self):
        for record in self:
            if self.env.user.has_group('frogblue_extensions.group_ext_user_products'):
                record.ext_show_price = True
            else:
                record.ext_show_price = False
