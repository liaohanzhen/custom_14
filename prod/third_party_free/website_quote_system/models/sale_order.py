# -*- coding: utf-8 -*-
#################################################################################
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
#################################################################################

from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_cancel(self):
        res = super(SaleOrder, self).action_cancel()
        for rec in self:
            for line in rec.order_line:
                if line.ref_quote_id:
                    quote_obj = self.env['quote.quote'].search([('id', '=', line.ref_quote_id)])
                    if quote_obj:
                        quote_obj.status = 'rejected'
                        quote_obj.send_quote_status_update_mail()
        return res

    def _cart_find_product_line(self, product_id=None, line_id=None, **kwargs):
        # case if plus minus or delete quote product line
        if line_id:
            line = self.env['sale.order.line'].browse(line_id)
            if line.customer_quote:
                return line
        res = super(SaleOrder, self)._cart_find_product_line(product_id, line_id, **kwargs)
        # case when the Quote is added to cart
        if kwargs.get("quote_line"):
            return self.env['sale.order.line']
        # case when no line of this product is in cart
        if len(res) == 0:
            return res
        else:
            # case for normal product add to cart and the quoted product is already in cart
            prod_line = res.filtered(lambda l: l.customer_quote == False)
            if prod_line:
                return self.env['sale.order.line'].browse(prod_line.ids)
            else:
                return self.env['sale.order.line']
        return res

    def _website_product_id_change(self, order_id, product_id, qty=0):
        res = super(SaleOrder, self)._website_product_id_change(order_id, product_id, qty)
        product = self.env['product.product'].browse(product_id)
        if product.quotation and self._context.get('quote_id') and self._context.get("quote_price"):
            vals = {
                'price_unit': self._context.get("quote_price"),
                'customer_quote': True,
                'ref_quote_id': int(self._context.get('quote_id')),
                'discount': 0,
            }
            res.update(vals)
        return res

    def _cart_update(self, product_id=None, line_id=None, add_qty=0, set_qty=0, attributes=None, **kwargs):
        # ------------- compatibility with website_sale_stock ---------
        if not line_id and kwargs.get("quote_line"):
            prod = self.env["product.product"].browse(int(product_id))
            if prod.type == 'product' and prod.inventory_availability in ['always', 'threshold']:
                cart_qty = sum(self.order_line.filtered(lambda p: p.product_id.id == prod.id).mapped('product_uom_qty'))
                quote_qty = add_qty
                available_qty = prod.virtual_available - cart_qty
                if available_qty < quote_qty:
                    # new_val = super(SaleOrder, self)._cart_update(product_id, line_id, None, 0, **kwargs)
                    if prod.virtual_available == 0:
                        self.warning_stock = _("Products with quoted quantity %s cannot be added to cart as it is temporarily out of stock. We're sorry for the inconvenience."%(quote_qty))
                    elif cart_qty and quote_qty and prod.virtual_available >= cart_qty:
                        self.warning_stock = _("Products with quoted quantity %s cannot be added to cart as only %s are available and %s are already in your cart. We're sorry for the inconvenience."%(quote_qty, prod.virtual_available, cart_qty))
                    else:
                        self.warning_stock = _("Products with quoted quantity %s cannot be added to cart. We're sorry for the inconvenience."%(quote_qty))
                    return {'warning': self.warning_stock}
        # ------------------------------------------------------------

        flag = 0
        if line_id:
            line_obj =  self.env['sale.order.line'].browse(line_id)
            if line_obj and line_obj.customer_quote:
                flag = 1
                # fix for multi currency
                try:
                    quote_obj = self.env['quote.quote'].sudo().browse(line_obj.ref_quote_id)
                    from_currency = quote_obj.website_currency_id
                    quote_prod_price = from_currency.compute(quote_obj.price, self.pricelist_id.currency_id)
                except Exception as e:
                    quote_prod_price = line_obj.price_unit

        res = super(SaleOrder, self)._cart_update(product_id, line_id, add_qty, set_qty, **kwargs)

        if not res.get("warning") and res.get('line_id') and flag == 1 and res.get('quantity') != 0:
            line_obj = self.env['sale.order.line'].browse(res.get('line_id'))
            line_obj.price_unit = quote_prod_price
        return res

    def _create_invoices(self, grouped=False, final=False):
        res = super(SaleOrder, self)._create_invoices(grouped, final)
        for order in self:
            for lines in order.order_line:
                if lines.ref_quote_id:
                    obj = self.env['quote.quote'].search([('id', '=', lines.ref_quote_id)])
                    if obj:
                        obj.status = 'sold'
                        obj.send_quote_status_update_mail()
        return res

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    customer_quote = fields.Boolean(string='Customer Quote')
    ref_quote_id = fields.Integer("Quote ID")

class AccountInvoice(models.Model):
    _inherit = "account.move"

    def action_cancel(self):
        res = super(AccountInvoice, self).action_cancel()
        for rec in self:
            if rec.origin:
                sale_order_obj = self.env['sale.order'].search([('name', 'ilike', self.origin)])
                if sale_order_obj:
                    for line in sale_order_obj.order_line:
                        if line.ref_quote_id:
                            quote_obj = self.env['quote.quote'].search([('id', '=', line.ref_quote_id)])
                            if quote_obj:
                                quote_obj.status = 'inprocess'
                                quote_obj.send_quote_status_update_mail()
        return res
